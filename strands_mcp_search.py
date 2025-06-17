import streamlit as st
from strands import Agent
from strands.tools.mcp import MCPClient  # 正确导入路径[1][5]
from mcp.transports.http import streamablehttp_client_factory
from mcp.client.streamable_http import streamablehttp_client

# 页面配置
st.set_page_config(page_title="EXA MCP Search", layout="wide")
st.title("EXA 实时搜索（MCP协议）")
st.markdown("基于 Strands Agents SDK 官方示例构建")

def create_exa_client():
    """创建EXA MCP客户端工厂函数"""
    return streamablehttp_client_factory(
        server_url="https://mcp.exa.ai/mcp",
        headers={"exa-api-key": st.secrets["EXA_API_KEY"]}  # 从Streamlit Secrets获取密钥
    )

# 搜索执行函数
def execute_search(query: str):
    with MCPClient(create_exa_client) as client:
        # 获取工具列表并创建Agent
        tools = client.list_tools_sync()
        agent = Agent(tools=tools)
        
        # 执行搜索请求
        response = agent.run(
            input=query,
            tool_choice="web_search_exa",
            tool_parameters={
                "num_results": 5,
                "include_domains": ["arxiv.org", "exa.ai"]
            }
        )
        
        # 处理响应结果
        results = []
        for item in response.results:
            results.append({
                "title": item.get("title", "Untitled"),
                "url": item.get("url", "#"),
                "content": item.get("content", "")[:250] + "..."
            })
        return results

# Streamlit UI组件
with st.form("search_form"):
    query = st.text_area("输入搜索内容", height=100)
    submitted = st.form_submit_button("执行搜索")

if submitted:
    if not query.strip():
        st.error("请输入有效搜索内容")
    else:
        with st.spinner("正在通过MCP协议查询EXA..."):
            try:
                search_results = execute_search(query)
                
                # 显示结果
                st.subheader(f"找到 {len(search_results)} 条结果")
                for result in search_results:
                    with st.expander(result["title"]):
                        st.markdown(f"[{result['url']}]({result['url']})")
                        st.caption(result["content"])
                        
            except Exception as e:
                st.error(f"搜索失败: {str(e)}")
                st.exception(e)  # 显示完整错误堆栈
