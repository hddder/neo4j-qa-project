import sys

# 检查是否使用了错误的启动方式
if "streamlit" not in sys.modules and "__file__" in globals():
    if not any(arg.endswith("streamlit") for arg in sys.argv):
        print("\n" + "!"*60)
        print("❌ 启动失败：检测到您正在使用 'python app.py'")
        print("💡 请务必改用以下命令启动网页：")
        print("\n   streamlit run app.py\n")
        print("!"*60 + "\n")
        sys.exit(0) # 强制停止执行后续代码

import streamlit as st
import json
import pandas as pd
import streamlit_echarts as echarts

# --------------------------
# 1. 加载数据
# --------------------------
@st.cache_data
def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"nodes": [], "edges": []}
    except Exception as e:
        st.error(f"加载数据失败: {e}")
        return {"nodes": [], "edges": []}

graph = load_data()
nodes = graph.get("nodes", [])
edges = graph.get("edges", [])

if not nodes:
    st.warning("⚠️ 暂无数据，请先运行 2_export_json.py 导出数据。")
    st.stop()

# --------------------------
# 2. 页面样式（美观）
# --------------------------
st.set_page_config(page_title="知识图谱多跳查询", layout="wide")
st.title("🌍 知识图谱多跳查询与可视化系统")
st.markdown("---")

# --------------------------
# 3. 聚类与配色（适配新数据）
# --------------------------
type_color = {
    "Question": "#ee6666",  # 红色
    "Document": "#5470c6",  # 蓝色
    "Person": "#91cc75",    # 绿色
    "City": "#fac858",      # 黄色
    "Unknown": "#999"
}

# --------------------------
# 4. 检索功能（搜索框）
# --------------------------
st.sidebar.header("🔍 检索")
search_key = st.sidebar.text_input("搜索实体名称")

# 过滤搜索结果
filtered_nodes = []
for n in nodes:
    if search_key in str(n["name"]):
        filtered_nodes.append(n)
if not search_key:
    filtered_nodes = nodes

# --------------------------
# 5. 多跳查询逻辑 (BFS)
# --------------------------
st.sidebar.header("🧠 多跳查询")
hop_select = st.sidebar.selectbox("选择跳数", [1, 2, 3, 4, 5])
start_entity = st.sidebar.text_input("起始实体（如：哈利波特）")

path_nodes = set()
path_edges = []
path_results = []

if start_entity:
    # 1. 找到起点（从全局节点找，不受检索过滤影响）
    start_node = next((n for n in nodes if n["name"] == start_entity), None)
    
    if start_node:
        st.markdown(f"## 🧬 从「{start_entity}」出发的 {hop_select} 跳推理")
        
        # BFS 查找多跳路径
        queue = [(start_node, 0, [])] # (当前节点, 当前跳数, 路径文本)
        path_nodes.add(start_node["id"])
        
        while queue:
            curr_node, depth, history = queue.pop(0)
            
            if depth < hop_select:
                for e in edges:
                    if e["source"] == curr_node["id"]:
                        target_node = next((n for n in nodes if n["id"] == e["target"]), None)
                        if target_node:
                            new_history = history + [f"{curr_node['name']} →[{e['relation']}]→ {target_node['name']}"]
                            path_nodes.add(target_node["id"])
                            path_edges.append(e)
                            path_results.append(" | ".join(new_history))
                            queue.append((target_node, depth + 1, new_history))
        
        # 展示推理路径
        if path_results:
            for res in path_results:
                st.success(res)
        else:
            st.warning("未找到后续跳数的关系。")
    else:
        st.error(f"未在图中找到实体：{start_entity}")

# --------------------------
# 6. 聚类展示 (按类型分组)
# --------------------------
st.markdown("## 📦 聚类分组与统计")
cluster_data = {}
for n in filtered_nodes:
    t = n.get("type", "Unknown")
    if t not in cluster_data:
        cluster_data[t] = []
    cluster_data[t].append(n["name"])

# 统计图表
col_c1, col_c2 = st.columns([1, 2])
with col_c1:
    st.write("### 类别分布")
    type_counts = [{"name": k, "value": len(v)} for k, v in cluster_data.items()]
    pie_option = {
        "tooltip": {"trigger": "item"},
        "series": [{
            "type": "pie",
            "radius": "70%",
            "data": type_counts,
            "emphasis": {
                "itemStyle": {"shadowBlur": 10, "shadowOffsetX": 0, "shadowColor": "rgba(0, 0, 0, 0.5)"}
            }
        }]
    }
    echarts.st_echarts(options=pie_option, height="300px")

with col_c2:
    st.write("### 实体聚类详情")
    for tp, names in cluster_data.items():
        with st.expander(f"📌 {tp}（{len(names)}个）"):
            st.write(", ".join(names[:30]))

# --------------------------
# 7. 可视化图谱（带高亮）
# --------------------------
st.markdown("## 🌌 知识图谱可视化")

# 构建可视化数据
viz_nodes = []
for n in filtered_nodes:
    is_in_path = n["id"] in path_nodes
    
    # 动态构建显示文本
    display_name = n.get("name", n.get("title", str(n["id"])))
    tooltip_content = f"类型: {n['type']}<br/>名称: {display_name}"
    if "answer" in n:
        tooltip_content += f"<br/>答案: {n['answer']}"
    if "question" in n:
        tooltip_content = f"问题: {n['question']}<br/>" + tooltip_content

    viz_nodes.append({
        "id": str(n["id"]),
        "name": display_name,
        "category": n["type"],
        "symbolSize": 35 if is_in_path else 20,
        "value": tooltip_content, # 用于 tooltip
        "itemStyle": {
            "color": type_color.get(n["type"], "#999"),
            "borderColor": "#000" if is_in_path else "transparent",
            "borderWidth": 2 if is_in_path else 0,
            "opacity": 1.0 if (not path_nodes or is_in_path) else 0.3
        },
        "label": {"show": True if (is_in_path or not search_key) else False}
    })

viz_links = []
for e in edges:
    # 只有当两个端点都在 filtered_nodes 中时才显示边（或者在路径中）
    source_exists = any(n["id"] == e["source"] for n in filtered_nodes)
    target_exists = any(n["id"] == e["target"] for n in filtered_nodes)
    
    is_path_edge = any(pe["source"] == e["source"] and pe["target"] == e["target"] for pe in path_edges)
    
    if (source_exists and target_exists) or is_path_edge:
        viz_links.append({
            "source": str(e["source"]),
            "target": str(e["target"]),
            "value": e["relation"],
            "lineStyle": {
                "width": 3 if is_path_edge else 1,
                "color": "#ff4b4b" if is_path_edge else "#aaa",
                "opacity": 1.0 if (not path_edges or is_path_edge) else 0.2
            },
            "label": {"show": True if is_path_edge else False, "formatter": e["relation"]}
        })

option = {
    "tooltip": {"trigger": "item", "formatter": "{c}"},
    "legend": [{"data": list(type_color.keys())}],
    "series": [{
        "type": "graph",
        "layout": "force",
        "roam": True,
        "draggable": True,
        "label": {"show": True, "position": "right"},
        "force": {"repulsion": 1000, "edgeLength": 200},
        "data": viz_nodes,
        "links": viz_links,
        "categories": [{"name": k} for k in type_color.keys()]
    }]
}

echarts.st_echarts(options=option, height="700px")

# --------------------------
# 8. 数据列表
# --------------------------
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.subheader("📊 实体列表")
    st.dataframe(pd.DataFrame(filtered_nodes), use_container_width=True)
with col2:
    st.subheader("🔗 关系列表")
    st.dataframe(pd.DataFrame(edges), use_container_width=True)