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
from utils.question_type import parse_query, question_type_dict, generate_answer

from query.models import QueryHistory


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

    def post(self, request, *args, **kwargs):
        recent_queries = QueryHistory.objects.filter(user=self.request.user).order_by(
            "-timestamp"
        )[:10]
        search_query = request.POST.get("search_query")
        try:
            with create_neo4j_transaction() as session:
                parsed_query = parse_query(search_query)
                search_results = generate_answer(parsed_query)

                if search_results == "x":
                    search_results = "没有找到答案，如果您愿意，可以使用在线询问服务。"

                print("Query results:")
                print(search_results)

            # 记录查询历史，无论 search_results 是否为空
            QueryHistory.objects.create(user=request.user, query_content=search_query)
            # graph_data = query_neo4j(request)
            return render(
                request,
                self.template_name,
                {"search_results": search_results, "recent_queries": recent_queries},
            )

        except Exception as e:
            # 发生异常时，返回错误信息
            return render(
                request,
                self.template_name,
                {"error_message": str(e), "recent_queries": recent_queries},
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
