# 网络搜索助手 (Web Search Assistant)

这是一个使用 Strands Agents 和 Exa 实现的网络搜索应用，通过 Streamlit 页面展示 MCP (Model Context Protocol) 的基础功能。目前项目处于初始阶段，提供了基本的搜索功能，后续将添加更多 MCP 特色功能。

## 当前功能

- 使用 Exa API 进行网络搜索
- 使用 Strands Agents 处理和总结搜索结果
- 支持中文和英文界面
- 简洁直观的 Streamlit 用户界面
- 提供直接 API 调用和 MCP 调用两种模式对比

## 计划中的功能

- 搜索历史记录管理
- 搜索结果的智能过滤和分类
- 多语言翻译支持
- 搜索结果的深度分析
- 更多 MCP 特色工具和资源

## 安装步骤

1. 克隆仓库:
```bash
git clone https://github.com/yourusername/strands_agents_quickstart.git
cd strands_agents_quickstart
```

2. 使用 uv 构建环境:
```bash
# 安装 uv (如果尚未安装)
curl -sSf https://install.ultraviolet.rs | sh

# 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate

uv pip sync requirements.txt
```

3. 设置环境变量:
   - 复制 `.env.example` 文件为 `.env`
   - 在 `.env` 文件中填入您的 Exa API 密钥、Strands API 密钥和 MCP 服务器 URL

## 运行应用

1. 启动 MCP 服务器:
```bash
python mcp_server.py
```

2. 在新的终端窗口中启动 Streamlit 应用:
```bash
streamlit run strands_mcp_search.py
```

应用将在本地启动，通常在 http://localhost:8501

## 关于 MCP (Model Context Protocol)

MCP 是一个开放协议，用于标准化应用程序如何向大型语言模型 (LLM) 提供上下文。MCP 使系统能够与本地运行的 MCP 服务器通信，这些服务器提供额外的工具和资源来扩展 LLM 的能力。

在这个演示中，我们展示了如何使用 MCP 服务器来处理网络搜索请求，而不是直接在应用程序中调用 API。

## API 密钥获取

- Exa API: https://exa.ai
- reference doc : https://docs.exa.ai/reference/getting-started
## 许可证

请参阅 LICENSE 文件
