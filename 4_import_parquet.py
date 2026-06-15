import pandas as pd
from neo4j import GraphDatabase
import importlib

# 动态加载连接配置
connect_mod = importlib.import_module("1_connect_neo4j")
get_driver = connect_mod.get_driver

# 数据文件列表
files = [
    "train-00000-of-00002.parquet",
    "train-00001-of-00002.parquet",
    "validation-00000-of-00001.parquet"
]

def import_data():
    driver = get_driver()
    
    with driver.session() as session:
        # 1. 不再进行旧数据清理，防止内存爆炸
        print("开始导入数据...")
        
        # 2. 创建约束（加速查询）
        try:
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (q:Question) REQUIRE q.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.title IS UNIQUE")
        except Exception as e:
            print("约束创建警告（可能已存在）：", e)

        for file in files:
            print(f"正在导入文件: {file}")
            try:
                df = pd.read_parquet(file)
            except Exception as e:
                print(f"读取文件 {file} 失败: {e}")
                continue

            # 移除限制，导入全部数据
            print(f"文件 {file} 共 {len(df)} 条数据，开始导入...")

            for idx, row in df.iterrows():
                # 创建问题节点
                session.run("""
                    MERGE (q:Question {id: $id})
                    SET q.question = $question,
                        q.answer = $answer,
                        q.type = $type,
                        q.level = $level,
                        q.name = $question_short
                """, {
                    "id": row["id"],
                    "question": row["question"],
                    "answer": row["answer"],
                    "type": row["type"],
                    "level": row["level"],
                    "question_short": row["question"][:20] + "..." # 缩略名用于显示
                })

                # 处理支持的事实（关系）
                supporting_facts = row["supporting_facts"]
                titles = supporting_facts.get("title", [])
                
                for title in titles:
                    # 创建文档节点并建立联系
                    session.run("""
                        MERGE (d:Document {title: $title})
                        SET d.name = $title, d.type = 'Document'
                        WITH d
                        MATCH (q:Question {id: $id})
                        MERGE (q)-[:SUPPORTED_BY]->(d)
                    """, {"title": title, "id": row["id"]})
                
                # 每处理 100 条打印一次进度
                if (idx + 1) % 100 == 0:
                    print(f"  已处理 {idx + 1} / {len(df)} 条...")

        print("✅ 数据导入完成！")
    
    driver.close()

if __name__ == "__main__":
    import_data()
