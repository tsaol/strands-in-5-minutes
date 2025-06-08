import os
import streamlit as st
from dotenv import load_dotenv
from exa_py import Exa
from strands import  Agent
from strands.models import BedrockModel
from strands import tool
import logging

# Configure the root strands logger
logging.getLogger("strands").setLevel(logging.DEBUG)

# Add a handler to see the logs
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s", 
    handlers=[logging.StreamHandler()]
)

# Load environment variables
load_dotenv()

# Function Decorator Approach
@tool
def exa_search(query: str) -> str:
    exa_client = Exa(api_key=os.getenv("EXA_API_KEY"))
    search_results = exa_client.search_and_contents(
        query=query,
        num_results=5,
        text=True
    )
    return search_results

         

model = BedrockModel(
    # model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    # aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    # aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "us-west-2")
)
# Strands defaults to the Bedrock model provider using Claude 3.7 Sonnet. The model your agent is using can be retrieved by accessing model.config
# Create an agent with a specific model by passing the model ID string
# strands_agent = Agent(model=model)

# Set up Streamlit page
st.set_page_config(page_title="基于Strands & Bedrock 联网搜索", layout="wide")
st.title("基于Strands Agents & Bedrock 联网搜索")

# Create search input
search_query = st.text_input("请输入搜索内容:", "")

# Create language selector
language = st.selectbox("选择语言:", ["中文", "English"])

if st.button("搜索"):
    if search_query:
        with st.spinner("正在搜索中..."):
            try:
               
                system_prompt = "你是一个专业的搜索助手。请根据搜索结果提供简洁明了的总结。" if language == "中文" else \
                               "You are a professional search assistant. Please provide a concise summary based on the search results."
                
                agent= Agent(
                    system_prompt=system_prompt,
                    tools=[exa_search]
                )

                prompt = f"以下是关于'{search_query}'的搜索结果，请提供一个全面的总结:" if language == "中文" else \
                         f"Here are the search results for '{search_query}', please provide a comprehensive summary:"
                
                # for i, content in enumerate(contents):
                #     prompt += f"\n\n结果 {i+1}:\n标题: {content['title']}\n内容: {content['content']}\n链接: {content['url']}"
                
                # Get response from Strands agent (with max_tokens control)
                response = agent(prompt, max_tokens=8000, temperature=0.3)
                
                # 以下为Guardrails集成示意，实际需根据AWS官方SDK调整
                # 假设有一个函数 apply_guardrail(text: str) -> str
                # safe_response = apply_guardrail(response)
                safe_response = response  # 实际使用时替换为真实调用

                # Display results
                st.subheader("搜索总结" if language == "中文" else "Search Summary")
                st.write(safe_response)
                
                # Display individual search results
                st.subheader("搜索结果" if language == "中文" else "Search Results")

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
