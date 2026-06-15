# 🌍 知识图谱多跳查询与可视化系统

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://neo4j-app-project-p4s6k7iqxv7nhnpgxsdmei.streamlit.app/)

这是一个基于 **Neo4j** 和 **Streamlit** 构建的轻量级知识图谱展示系统。它能够展示复杂的数据关联，并支持离线多跳推理查询。

## 🚀 功能特性
- **知识图谱可视化**：利用 ECharts 实现动态、可交互的力导向图。
- **离线多跳推理**：基于 BFS 算法，在无需连接数据库的情况下实现多跳路径搜索与展示。
- **实体检索与过滤**：支持关键词搜索，实时筛选感兴趣的知识节点。
- **数据聚类统计**：自动按实体类型分组，并提供占比饼图统计。
- **无后端运行**：通过导出的 `data.json` 实现 Web 端的完全独立运行。

## 🛠️ 技术栈
- **数据存储**：Neo4j (Ubuntu 部署)
- **数据处理**：Python, Pandas, PyArrow
- **Web 框架**：Streamlit
- **可视化库**：ECharts (via `streamlit-echarts`)

## 📖 快速开始

### 1. 环境准备
```bash
pip install streamlit pandas streamlit-echarts neo4j pyarrow fastparquet
```

### 2. 数据导入与导出 (需 Neo4j)
1. 配置 `1_connect_neo4j.py` 中的数据库连接信息。
2. 运行导入脚本：`python 4_import_parquet.py`
3. 导出 JSON 快照：`python 2_export_json.py`

### 3. 启动可视化界面
```bash
streamlit run app.py
```

## 🌐 在线演示
您可以通过以下链接直接访问部署在 Streamlit Cloud 上的演示版本：
👉 [点击查看在线演示](https://neo4j-app-project-p4s6k7iqxv7nhnpgxsdmei.streamlit.app/)

## 📂 项目结构
- `app.py`: Web 可视化主程序
- `2_export_json.py`: 数据库快照导出脚本
- `4_import_parquet.py`: 原始数据导入脚本
- `data.json`: 导出的静态图谱数据
- `requirements.txt`: 项目依赖列表
