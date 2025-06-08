import os
import streamlit as st
from dotenv import load_dotenv
from exa_py import Exa
from strands import  Agent
from strands.models import BedrockModel

# Load environment variables
load_dotenv()

# Initialize API clients
exa_client = Exa(api_key=os.getenv("EXA_API_KEY"))
model = BedrockModel(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "us-west-2")
)
strands_agent = Agent(model=model)

# Set up Streamlit page
st.set_page_config(page_title="网络搜索助手", layout="wide")
st.title("网络搜索助手")

# Create search input
search_query = st.text_input("请输入搜索内容:", "")

# Create language selector
language = st.selectbox("选择语言:", ["中文", "English"])

if st.button("搜索"):
    if search_query:
        with st.spinner("正在搜索中..."):
            try:
                # Use Exa for web search
                search_results = exa_client.search(
                    query=search_query,
                    num_results=5,
                    use_autoprompt=True,
                    text=True
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
                
                agent = strands_agent.agent(system=system_prompt)
                
                # Create a prompt with the search results
                prompt = f"以下是关于'{search_query}'的搜索结果，请提供一个全面的总结:" if language == "中文" else \
                         f"Here are the search results for '{search_query}', please provide a comprehensive summary:"
                
                for i, content in enumerate(contents):
                    prompt += f"\n\n结果 {i+1}:\n标题: {content['title']}\n内容: {content['content']}\n链接: {content['url']}"
                
                # Get response from Strands agent (with max_tokens control)
                response = agent.complete(prompt, max_tokens=1000, temperature=0.3)
                
                # 以下为Guardrails集成示意，实际需根据AWS官方SDK调整
                # 假设有一个函数 apply_guardrail(text: str) -> str
                # safe_response = apply_guardrail(response)
                safe_response = response  # 实际使用时替换为真实调用

                # Display results
                st.subheader("搜索总结" if language == "中文" else "Search Summary")
                st.write(safe_response)
                
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
st.markdown("### 使用说明" if language == "中文" else "### Instructions")
st.markdown("""
1. 输入您想要搜索的内容
2. 选择您偏好的语言
3. 点击"搜索"按钮
4. 查看搜索结果和AI生成的总结
""" if language == "中文" else """
1. Enter what you want to search for
2. Select your preferred language
3. Click the "Search" button
4. View the search results and AI-generated summary
""")
