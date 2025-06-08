import os
import streamlit as st
from dotenv import load_dotenv
from strandsagents import StrandsAgents
from exa_py import Exa
import json
import requests

# Load environment variables
load_dotenv()

# Initialize API clients
exa_client = Exa(api_key=os.getenv("EXA_API_KEY"))
strands_client = StrandsAgents()

# MCP Server configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")

# MCP Client for web search
class MCPWebSearchClient:
    def __init__(self, server_url):
        self.server_url = server_url
    
    def search(self, query, language="中文"):
        try:
            response = requests.post(
                f"{self.server_url}/search",
                json={"query": query, "language": language}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

# Initialize MCP client
mcp_client = MCPWebSearchClient(MCP_SERVER_URL)

# Set up Streamlit page
st.set_page_config(page_title="网络搜索助手 (MCP版)", layout="wide")
st.title("网络搜索助手 (MCP版)")
st.caption("使用 Model Context Protocol (MCP) 实现的网络搜索应用")

# Create tabs for different modes
tab1, tab2 = st.tabs(["MCP 模式", "直接 API 模式"])

with tab1:
    st.header("MCP 模式")
    st.info("此模式通过 MCP 服务器处理搜索请求，展示 MCP 的能力")
    
    # Create search input
    search_query_mcp = st.text_input("请输入搜索内容 (MCP):", "", key="mcp_query")
    
    # Create language selector
    language_mcp = st.selectbox("选择语言:", ["中文", "English"], key="mcp_lang")
    
    if st.button("通过 MCP 搜索", key="mcp_search"):
        if search_query_mcp:
            with st.spinner("正在通过 MCP 搜索中..."):
                try:
                    # Use MCP for web search
                    results = mcp_client.search(search_query_mcp, language_mcp)
                    
                    if "error" in results:
                        st.error(f"MCP 搜索出错: {results['error']}")
                    else:
                        # Display results
                        st.subheader("MCP 搜索总结" if language_mcp == "中文" else "MCP Search Summary")
                        st.write(results.get("summary", "无总结提供"))
                        
                        # Display individual search results
                        st.subheader("MCP 搜索结果" if language_mcp == "中文" else "MCP Search Results")
                        for i, content in enumerate(results.get("results", [])):
                            with st.expander(f"{i+1}. {content['title']}"):
                                st.write(content['content'])
                                st.write(f"[链接]({content['url']})" if language_mcp == "中文" else f"[Link]({content['url']})")
                
                except Exception as e:
                    st.error(f"MCP 处理出错: {str(e)}")
        else:
            st.warning("请输入搜索内容" if language_mcp == "中文" else "Please enter a search query")

with tab2:
    st.header("直接 API 模式")
    st.info("此模式直接使用 Exa 和 Strands API，不通过 MCP")
    
    # Create search input
    search_query = st.text_input("请输入搜索内容:", "", key="direct_query")
    
    # Create language selector
    language = st.selectbox("选择语言:", ["中文", "English"], key="direct_lang")
    
    if st.button("直接搜索", key="direct_search"):
        if search_query:
            with st.spinner("正在搜索中..."):
                try:
                    # Use Exa for web search
                    search_results = exa_client.search(
                        query=search_query,
                        num_results=5,
                        use_autoprompt=True
                    )
                    
                    # Extract content and URLs from search results
                    contents = []
                    for result in search_results.results:
                        contents.append({
                            "title": result.title,
                            "content": result.text,
                            "url": result.url
                        })
                    
                    # Use Strands to process and summarize the search results
                    system_prompt = "你是一个专业的搜索助手。请根据搜索结果提供简洁明了的总结。" if language == "中文" else \
                                   "You are a professional search assistant. Please provide a concise summary based on the search results."
                    
                    agent = strands_client.agent(system=system_prompt)
                    
                    # Create a prompt with the search results
                    prompt = f"以下是关于'{search_query}'的搜索结果，请提供一个全面的总结:" if language == "中文" else \
                             f"Here are the search results for '{search_query}', please provide a comprehensive summary:"
                    
                    for i, content in enumerate(contents):
                        prompt += f"\n\n结果 {i+1}:\n标题: {content['title']}\n内容: {content['content']}\n链接: {content['url']}"
                    
                    # Get response from Strands agent
                    response = agent.complete(prompt)
                    
                    # Display results
                    st.subheader("搜索总结" if language == "中文" else "Search Summary")
                    st.write(response)
                    
                    # Display individual search results
                    st.subheader("搜索结果" if language == "中文" else "Search Results")
                    for i, content in enumerate(contents):
                        with st.expander(f"{i+1}. {content['title']}"):
                            st.write(content['content'])
                            st.write(f"[链接]({content['url']})" if language == "中文" else f"[Link]({content['url']})")
                
                except Exception as e:
                    st.error(f"搜索出错: {str(e)}" if language == "中文" else f"Error during search: {str(e)}")
        else:
            st.warning("请输入搜索内容" if language == "中文" else "Please enter a search query")

# Add instructions at the bottom
st.markdown("---")
st.markdown("### 关于 MCP (Model Context Protocol)")
st.markdown("""
MCP (Model Context Protocol) 是一个开放协议，用于标准化应用程序如何向大型语言模型 (LLM) 提供上下文。
MCP 使系统能够与本地运行的 MCP 服务器通信，这些服务器提供额外的工具和资源来扩展 LLM 的能力。

在这个演示中，我们展示了如何使用 MCP 服务器来处理网络搜索请求，而不是直接在应用程序中调用 API。
""")

st.markdown("### 使用说明")
st.markdown("""
1. 选择模式标签页（MCP 模式或直接 API 模式）
2. 输入您想要搜索的内容
3. 选择您偏好的语言
4. 点击相应的搜索按钮
5. 查看搜索结果和 AI 生成的总结
""")
