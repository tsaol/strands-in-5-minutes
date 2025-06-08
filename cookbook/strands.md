# Strands Agentic 开发入门：核心架构与Agentic Loop

Strands Agents SDK 通过**模型驱动架构**重新定义了AI代理开发范式，使开发者能够快速构建具备自主推理和工具调用能力的智能体。其核心设计理念是让大型语言模型（LLM）成为代理的"决策中枢"，通过Agentic Loop实现任务分解、工具调用和结果整合的自动化流程。

## 核心架构三要素

Strands代理由以下组件构成结构化工作流：

- **模型（Model）**
  - 作为代理的推理引擎，支持Amazon Bedrock、Anthropic Claude、Meta Llama等主流模型
  - 通过LiteLLM兼容OpenAI、Mistral等第三方API
  - 示例模型配置：
    ```
    from strands.models import BedrockModel
    model = BedrockModel(model_id="us.amazon.nova-micro-v1:0", region_name='us-east-1')
    ```

- **工具（Tools）**
  - 预置20+工具（计算器、HTTP请求、Python REPL等）
  - 使用`@tool`装饰器快速集成自定义函数：
    ```
    from strands import tool
    @tool
    def file_analyzer(path: str) -> dict:
        """文件分析工具"""
        # 实现文件解析逻辑
        return analysis_result
    ```

- **提示（Prompt）**
  - 系统提示定义代理行为准则：
    ```
    SYSTEM_PROMPT = """你是一个数据分析专家，使用工具处理数据并生成可视化报告：
    1. 优先使用pandas进行数据清洗
    2. 使用matplotlib创建交互式图表
    3. 输出Markdown格式报告"""
    ```
  - 用户提示指定具体任务："分析sales.csv中的季度销售趋势"

## Agentic Loop 机制

代理通过以下循环实现自主任务处理：

```

flowchart LR
A[输入请求] --> B{模型推理}
B -->|工具调用| C[执行工具]
C --> D[结果反馈]
D --> B
B -->|完成任务| E[输出结果]

```

**生命周期阶段：**

1. **上下文初始化**
   加载会话历史、工具描述和系统提示

2. **动态规划阶段**
   模型解析任务并生成执行计划（如："需先调用API获取数据，再进行统计分析"）

3. **工具执行阶段**
   - 自动选择工具（如http_request工具访问REST API）
   - 支持工具链式调用（前序工具输出作为后续工具输入）

4. **反射优化阶段**
   模型评估执行结果，必要时调整策略（如："API返回超时，尝试指数退避重试"）

5. **结果生成阶段**
   整合工具输出生成最终响应（文本/数据/代码等形式）

