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
st.set_page_config(page_title="基于Strands Agents & Bedrock 小红书文案写手", layout="wide")
st.title("基于Strands Agents & Bedrock 小红书文案写手")

# Create search input
search_query = st.text_input("请输入热点内容:", "")

# Create language selector
language = st.selectbox("选择语言:", ["中文", "English"])

if st.button("生成"):
    if search_query:
        with st.spinner("正在生成中..."):
            try:
               
                system_prompt = "你是一个专业文案写手，基于我输入的内容生成一个小红书风格文案。" if language == "中文" else \
                               "You are a professional search assistant. Pleae provide a concise summary based on the search results."
                
                agent= Agent(
                    system_prompt=system_prompt,
                    tools=[exa_search]
                )

                prompt = f"以下是关于'{search_query}'的搜索结果，你要确保是最新的消息，现在时间是2025年6月9日，生成1个小红书风格文案:" if language == "中文" else \
                         f"Here are the search results for '{search_query}', please provide a comprehensive summary:"
                
                # for i, content in enumerate(contents):
                #     prompt += f"\n\n结果 {i+1}:\n标题: {content['title']}\n内容: {content['content']}\n链接: {content['url']}"
                # Get response from Strands agent (with max_tokens control)
                response = agent(prompt, max_tokens=8000, temperature=0.3)
                
                # 以下为Guardrails集成示意，实际需根据AWS官方SDK调整
                # 假设有一个函数 apply_guardrail(text: str) -> str
                # safe_response = apply_guardrail(response)
                safe_response = response  # 实际使用时替换为真实调用
                # 提取文本内容
                if hasattr(safe_response, 'message'):
                    content = safe_response.message.get('content', [])
                    summary_text = "".join([item['text'] for item in content if 'text' in item])
                else:
                    summary_text = "未生成有效总结。"

                    
                # Display results
                st.subheader("文案生成" if language == "中文" else "Search Summary")
                st.write(summary_text)
                
                # Display individual search results
                # st.subheader("搜索结果" if language == "中文" else "Search Results")

            except Exception as e:
                st.error(f"搜索出错: {str(e)}" if language == "中文" else f"Error during search: {str(e)}")
    else:
        st.warning("请输入内容" if language == "中文" else "Please enter a search query")

# Add instructions at the bottom
st.markdown("---")
st.markdown("### 使用说明" if language == "中文" else "### Instructions")
st.markdown("""
✨ 三步开启智能文案之旅 ✨

1. **输入想问的内容**——不管是八卦、干货，还是生活小妙招，尽管大胆输入！
2. **选择语言**——中文英文随心切换，沟通无压力。
3. **点击“生成”按钮**——AI小助手秒速帮你生成文案。
4. **收获AI总结**—- 眼get重点，省时又省力！

让你的文案更聪明，生活更高效！快来试试吧～
""" if language == "中文" else """
✨ Three Easy Steps to Smart Search ✨

1. **Enter your question**—Anything you want to know, just type it in!
2. **Choose your language**—Switch between English and Chinese with ease.
3. **Click "Search"**—Let AI do the heavy lifting for you.
4. **Enjoy AI-generated summaries**—Get instant results and smart highlights, all in a snap!

Make your search smarter and your life easier. Try it now!
""")
