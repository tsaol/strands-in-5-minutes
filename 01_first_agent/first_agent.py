# first_agent.py
import sys
import logging
from strands import Agent

#打开debug 日志 
logging.getLogger("strands").setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)



agent = Agent(
    system_prompt = """
你是一个计算机科学教育专家，擅长用简单易懂的语言和实用例子解释计算机科学概念。
当用户提问时，请给出清晰、准确的回答，并尽量用代码或生活实例帮助理解。
"""
)


def interactive_session():
    print("计算机学科专家 (输入 'exit' to 退出)")
    print("-----------------------------------------------------------")
    
    while True:
        # Get user input
        user_input = input(f"\n你的问题是: ")
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
        
        # Send the input to the agent, which will automatically print the response
        print("\nThinking...\n")
        agent(user_input)

if __name__ == "__main__":
    interactive_session()




# # 调用 Agent
# response = agent.run("请解释什么是递归，并给出一个Python例子。")
# print(response)
