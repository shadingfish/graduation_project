import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from neo4j import GraphDatabase
from django.http import JsonResponse
from django.conf import settings
from utils.store_data import create_neo4j_transaction, query_dict
from utils.question_type import (
    parse_query,
    question_type_dict,
    generate_answer,
    query_gpt,
)

from query.models import QueryHistory

import logging

logger = logging.getLogger(__name__)


# GraphDatabase information


class QueryView(LoginRequiredMixin, View):
    template_name = "query/main_query.html"

    def get(self, request, *args, **kwargs):
        # 获取用户的检索历史
        context = {
            "recent_queries": QueryHistory.objects.filter(
                user=self.request.user
            ).order_by("-timestamp")[:10],
        }
        return render(request, "query/main_query.html", context)

    def post(self, request, *args, **kwargs) -> (str, list):
        search_query = "default"
        print("In QueryView-post method")
        recent_queries = QueryHistory.objects.filter(user=self.request.user).order_by(
            "-timestamp"
        )[:10]
        search_query = request.POST.get("search_query")
        gpt_active = request.POST.get("gptActive") == "true"

        try:
            # 记录查询历史，无论 search_results 是否为空
            if search_query == "":
                return render(
                    request,
                    self.template_name,
                    {
                        "search_results": "",
                        "recent_queries": recent_queries,
                        "gpt_active": gpt_active,
                        "json_data": [],
                    },
                )

            parsed_query = parse_query(search_query)
            search_results, json_data = generate_answer(parsed_query)

            ans_status = "E"

            if search_results == "x":
                if gpt_active:
                    search_results = query_gpt(search_query)
                    ans_status = "LLM"
                else:
                    search_results = "没有找到答案，如果您愿意，可以开启GPT-3.5数据源"
                    ans_status = "F"
            else:
                json_data = build_graph_data(json_data)
                json_data = json.dumps(json_data, ensure_ascii=False)
                ans_status = "KG"

            print("Query results:" + search_results)

            QueryHistory.objects.create(
                user=request.user, query_content=search_query, ans_status=ans_status
            )
            # graph_data = query_neo4j(request)
            return render(
                request,
                self.template_name,
                {
                    "search_results": search_results,
                    "recent_queries": recent_queries,
                    "gpt_active": gpt_active,
                    "json_data": json_data,
                },
            )

        except Exception as e:

            QueryHistory.objects.create(
                user=request.user, query_content=search_query, ans_status="E"
            )
            # 发生异常时，返回错误信息
            return render(
                request,
                self.template_name,
                {
                    "error_message": str(e),
                    "recent_queries": recent_queries,
                    "gpt_active": gpt_active,
                    "json_data": [],
                },
            )


class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.__uri = uri
        self.__user = user
        self.__password = password
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(
                self.__uri, auth=(self.__user, self.__password)
            )
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, parameters=None, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = (
                self.__driver.session(database=db)
                if db is not None
                else self.__driver.session()
            )
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response


def truncate_text(text, max_length):
    if len(text) > max_length:
        return text[:max_length] + "..."
    else:
        return text


def build_graph_data(data):
    nodes = []
    links = []

    for item in data:
        # 创建主节点
        main_node = {
            "id": f"{item['cn_name']} {item['binomial']}",
            "abbr": truncate_text(item["cn_name"], 5),
        }
        nodes.append(main_node)

        # 处理湿度、温度
        for attr in ["suit_humidity", "suit_temperature"]:
            node = {"id": item[attr], "abbr": truncate_text(item[attr], 5)}
            nodes.append(node)
            links.append(
                {"source": main_node["abbr"], "target": node["abbr"], "type": attr}
            )

        # 处理土壤类型
        for soil in item.get("suit_soil", []):
            node = {"id": soil, "abbr": truncate_text(soil, 5)}
            nodes.append(node)
            links.append(
                {
                    "source": main_node["abbr"],
                    "target": node["abbr"],
                    "type": "suit_soil",
                }
            )

        # 处理病害
        for disease_info in item.get("diseases_and_pathogen", []):
            node = {
                "id": disease_info["pathogen"],
                "abbr": truncate_text(disease_info["pathogen"], 5),
            }
            nodes.append(node)
            links.append(
                {
                    "source": main_node["abbr"],
                    "target": node["abbr"],
                    "type": disease_info["disease"],
                }
            )

        # 处理科属
        if "genus_name" in item and item["genus_name"]:
            genus_node = {
                "id": item["genus_name"],
                "abbr": truncate_text(item["genus_name"], 5),
            }
            family_node = {
                "id": item["family_name"],
                "abbr": truncate_text(item["family_name"], 5),
            }
            nodes.extend([genus_node, family_node])
            links.append(
                {
                    "source": main_node["abbr"],
                    "target": genus_node["abbr"],
                    "type": "genus_name",
                }
            )
            links.append(
                {
                    "source": genus_node["abbr"],
                    "target": family_node["abbr"],
                    "type": "family_name",
                }
            )

    return {"nodes": nodes, "links": links}


@login_required
@method_decorator(csrf_exempt, name="dispatch")
def query_neo4j(request):
    print("Querying Neo4j...")
    conn = Neo4jConnection(settings.NEO4J_URL, "neo4j", settings.NEO4J_PASSWORD)

    # # 修改查询字符串以针对特定标签及其两层内的节点和关系
    # query_string = """
    # MATCH (n)-[r]-(m)RETURN n LIMIT 10
    # RETURN DISTINCT n, r, m
    # """.format(
    #     label=label
    # )  # 假设 label 是您想要查询的标签

    # 修改查询字符串以针对特定标签及其两层内的节点和关系
    query_string = """
    MATCH (n)-[r]-(m) RETURN DISTINCT n, r, m LIMIT 10
    """
    results = conn.query(query_string)
    conn.close()
    nodes = []
    edges = []
    print("Formatting fetched data...")

    for record in results:
        node_n = record["n"]
        node_m = record.get("m")  # m 可能不存在于所有记录中
        rel_r = record.get("r")  # r 可能不存在于所有记录中

        # 添加节点
        for node in [node_n, node_m]:
            if node:
                nodes.append(
                    {
                        "id": node.id,
                        "label": list(node.labels)[0],
                        "title": ", ".join(
                            [f"{key}: {node[key]}" for key in node.keys()]
                        ),
                    }
                )

        # 添加边
        if rel_r:
            for rel in rel_r:
                edges.append(
                    {
                        "from": rel.start_node.id,
                        "to": rel.end_node.id,
                        "label": type(rel).__name__,
                        "title": ", ".join(
                            [f"{key}: {rel[key]}" for key in rel.keys()]
                        ),
                    }
                )

    # 移除重复的节点
    nodes = list({v["id"]: v for v in nodes}.values())

    print("nodes: {}".format(nodes))
    print("edges: {}".format(edges))

    conn.close()

    print("Finished querying")
    return {"nodes": nodes, "edges": edges}


def chatbot(request):
    pass
