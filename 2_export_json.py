import json
from neo4j import GraphDatabase

# 连接信息
URI = "bolt://192.168.198.137:7687"
AUTH = ("neo4j", "Hd026115@")


def export_graph():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    try:
        with driver.session() as session:
            # 获取所有节点及其所有属性
            print("正在从 Neo4j 读取节点...")
            nodes_query = session.run("""
                MATCH (n)
                RETURN 
                    id(n) AS id,
                    labels(n) AS labels,
                    properties(n) AS props
            """)
            nodes = []
            for record in nodes_query:
                node_data = record["props"]
                node_data["id"] = record["id"]
                # 优先取 name 属性，没有就取 id
                if "name" not in node_data:
                    node_data["name"] = f"Node_{record['id']}"
                # 取第一个标签作为 type
                node_data["type"] = record["labels"][0] if record["labels"] else "Unknown"
                nodes.append(node_data)

            # 获取所有关系
            print("正在从 Neo4j 读取关系...")
            edges_query = session.run("""
                MATCH (a)-[r]->(b)
                RETURN
                    id(a) AS source,
                    id(b) AS target,
                    type(r) AS relation,
                    properties(r) AS props
            """)
            edges = []
            for record in edges_query:
                edge_data = record["props"]
                edge_data["source"] = record["source"]
                edge_data["target"] = record["target"]
                edge_data["relation"] = record["relation"]
                edges.append(edge_data)

        # 保存 JSON
        graph_data = {"nodes": nodes, "edges": edges}
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(graph_data, f, ensure_ascii=False, indent=2)

        print(f"✅ data.json 导出成功！共 {len(nodes)} 个节点，{len(edges)} 条关系。")

    except Exception as e:
        print(f"❌ 导出失败: {e}")
    finally:
        driver.close()


if __name__ == "__main__":
    export_graph()