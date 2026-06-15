import importlib
# 由于文件名以数字开头，不能直接 import，使用 importlib 加载
connect_mod = importlib.import_module("1_connect_neo4j")
get_driver = connect_mod.get_driver

driver = get_driver()

# 3跳查询示例
query = """
MATCH path = (b)-[:创作]->(p)-[:出生地]->(c)-[:市长]->(m)
RETURN path, nodes(path) AS nodes, relationships(path) AS rels
"""

with driver.session() as session:
    records = session.run(query)
    for rec in records:
        nodes = rec["nodes"]
        rels = rec["rels"]
        print("\n🧠 多跳推理过程：")
        for i in range(len(nodes)-1):
            n1 = nodes[i]["name"]
            r = rels[i]
            n2 = nodes[i+1]["name"]
            print(f"第{i+1}跳：{n1} -[{r.type}]-> {n2}")

driver.close()