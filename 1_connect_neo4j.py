from neo4j import GraphDatabase

# Neo4j 连接信息（请替换为您自己的连接信息）
URI = "bolt://your-ip-address:7687"
USER = "neo4j"
PASSWORD = "your-password"

def get_driver():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    return driver

# 测试连接
if __name__ == "__main__":
    try:
        driver = get_driver()
        print("✅ Neo4j 连接成功")
        driver.close()
    except Exception as e:
        print("❌ 连接失败：", e)