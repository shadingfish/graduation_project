from django.shortcuts import render
from neo4j import GraphDatabase
from django.http import JsonResponse
from django.conf import settings


# GraphDatabase information
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


def query_neo4j(request):
    print("Querying Neo4j...")
    conn = Neo4jConnection(settings.NEO4J_URL, "neo4j", settings.NEO4J_PASSWORD)
    query_string = "MATCH (n)-[r]->(m) RETURN n, r, m"
    results = conn.query(query_string)
    conn.close()
    nodes = []
    edges = []
    print("Formatting fetched data...")
    for record in results:
        node_n = record['n']
        node_m = record['m']
        rel_r = record['r']

        # 添加节点
        for node in [node_n, node_m]:
            nodes.append({
                'id': node.id,
                'label': list(node.labels)[0],
                'title': ', '.join([f"{key}: {node[key]}" for key in node.keys()]),
            })

        # 添加边
        edges.append({
            'from': node_n.id,
            'to': node_m.id,
            'label': type(rel_r).__name__,
            'title': ', '.join([f"{key}: {rel_r[key]}" for key in rel_r.keys()]),
        })

    # 移除重复的节点
    nodes = list({v['id']:v for v in nodes}.values())
    
    print("nodes: {}".format(nodes))
    print("edges: {}".format(edges))

    conn.close()
    
    print("Finished querying")
    return JsonResponse({'nodes': nodes, 'edges': edges})


def query_page(request):
    return render(request, "query/main_query.html")


def chatbot(request):
    pass
