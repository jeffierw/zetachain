# Qwen-Agent 学习项目

这是一个 Qwen-Agent 框架的学习示例项目，帮助你理解和掌握 Agent 框架的核心概念和使用方法。

## 📚 学习目标

- ✅ 理解 Qwen-Agent 框架的基本组成（LLM / Agent / Tools / Memory）
- ✅ 搭建一个最小的 Agent，并挂载简单 Tool
- ✅ 验证 Agent 能够自动调用工具完成任务

## 🏗️ 项目结构

```
qwen_agent_demo/
├── README.md                  # 项目说明文档（本文件）
├── requirements.txt           # Python 依赖
├── .gitignore                # Git 忽略配置
├── basic_agent.py            # 基础 Agent 示例
├── custom_tools.py           # 自定义工具实现
└── agent_with_tools.py       # 集成工具的完整 Agent
```

## 🚀 快速开始

### 1. 环境准备

确保你已经安装了 Python 3.8 或更高版本。

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key

创建 `.env` 文件（或直接使用代码中的默认值）：

```bash
# 阿里云 DashScope API Key
DASHSCOPE_API_KEY=your_api_key_here

# 模型配置（可选）
MODEL_NAME=qwen-plus
```

> **提示**：当前代码中已内置了一个测试用的 API Key，你也可以从 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/) 获取你自己的 Key。

### 3. 运行示例

#### 示例 1：基础 Agent（无工具）

```bash
python basic_agent.py
```

这个示例展示了如何使用 Qwen-Agent 框架进行基本对话，与 `../qwen_demo/index.js` 中的纯 API 调用方式对比。

#### 示例 2：工具独立测试

```bash
python custom_tools.py
```

单独测试自定义工具的功能，验证工具逻辑是否正确。

#### 示例 3：Agent 工具调用（核心示例）

```bash
python agent_with_tools.py
```

这是最重要的示例，展示了 Agent 如何自动识别用户意图并调用相应的工具。

## 🔧 核心概念

### 1. LLM（大语言模型）

LLM 是 Agent 的"大脑"，负责理解用户意图和生成响应。

```python
from qwen_agent.llm import get_chat_model

llm_cfg = {
    'model': 'qwen-plus',
    'api_key': 'your_api_key',
    'model_server': 'dashscope',
}
llm = get_chat_model(llm_cfg)
```

### 2. Agent（智能体）

Agent 是执行任务的主体，能够进行推理、决策和调用工具。

```python
from qwen_agent.agents import Assistant

agent = Assistant(
    llm=llm,
    name='助手名称',
    description='助手描述',
    system_message='系统提示词',
    function_list=tools,  # 挂载工具
)
```

### 3. Tools（工具）

工具扩展了 Agent 的能力，让 Agent 能够执行特定任务。

```python
from qwen_agent.tools.base import BaseTool, register_tool

@register_tool('tool_name')
class MyTool(BaseTool):
    description = '工具描述'
    parameters = [{
        'name': 'param_name',
        'type': 'string',
        'description': '参数描述',
        'required': True
    }]
    
    def call(self, params: dict, **kwargs) -> str:
        # 实现工具逻辑
        return "工具执行结果"
```

### 4. Memory（记忆）

Memory 让 Agent 能够记住历史对话，实现多轮对话能力。（本项目暂未实现，是后续学习方向）

## 📝 自定义工具示例

本项目实现了三个简单的自定义工具：

### 1. 字符串转大写工具

```python
@register_tool('to_uppercase')
class ToUppercaseTool(BaseTool):
    description = '将输入的字符串转换为大写字母'
    # ...
```

### 2. 计算两数之和工具

```python
@register_tool('calculate_sum')
class CalculateSumTool(BaseTool):
    description = '计算两个数字的和'
    # ...
```

### 3. 字符串信息分析工具

```python
@register_tool('string_info')
class StringInfoTool(BaseTool):
    description = '分析字符串的详细信息'
    # ...
```

## 🎯 作业检验

运行 `agent_with_tools.py` 后，你应该能看到：

- ✅ Agent 能够理解 "把 'hello world' 转换成大写" 并调用 `to_uppercase` 工具
- ✅ Agent 能够理解 "计算 123 + 456" 并调用 `calculate_sum` 工具
- ✅ Agent 能够自动选择合适的工具完成任务
- ✅ 对于不需要工具的问题，Agent 能够直接回答

## 📖 学习资料

### 官方文档

- [Qwen-Agent 官方文档](https://qwen.readthedocs.io/en/v2.5/framework/qwen_agent.html)
- [Qwen-Agent GitHub](https://github.com/QwenLM/Qwen-Agent)
- [阿里云 DashScope](https://dashscope.console.aliyun.com/)

### 代码对比

- **qwen_demo/index.js**：使用 OpenAI SDK 直接调用 Qwen API
- **basic_agent.py**：使用 Qwen-Agent 框架的基础对话
- **agent_with_tools.py**：Agent 自动调用工具的完整流程

## 🔄 与纯 API 调用的区别

| 特性 | 纯 API 调用 | Qwen-Agent 框架 |
|------|------------|----------------|
| 基础对话 | ✅ 支持 | ✅ 支持 |
| 工具调用 | ❌ 需手动实现 | ✅ 自动处理 |
| 多轮对话 | ❌ 需手动管理 | ✅ 内置支持 |
| 复杂推理 | ❌ 需手动编排 | ✅ Agent 自动推理 |
| 开发效率 | 低 | 高 |

## 🎓 后续学习方向

完成本项目后，你可以继续探索：

1. **添加 Memory**：实现多轮对话记忆
2. **接入实用工具**：
   - 网络搜索工具
   - 数据库查询工具
   - 文件操作工具
   - API 调用工具
3. **多 Agent 协作**：创建多个 Agent 协同完成复杂任务
4. **自定义 Agent 行为**：
   - 实现自己的 Agent 类
   - 自定义决策逻辑
   - 优化 prompt 策略
5. **RAG（检索增强生成）**：结合向量数据库实现知识问答

## 🐛 常见问题

### Q1: 安装依赖时报错？

确保 Python 版本 >= 3.8，并且网络连接正常。可以尝试使用镜像源：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q2: API 调用失败？

检查：
1. API Key 是否正确
2. 网络是否能访问阿里云 DashScope
3. 账户是否有余额

### Q3: Agent 没有调用工具？

可能原因：
1. 工具描述不够清晰，Agent 无法理解工具用途
2. 用户请求不够明确
3. 模型选择不当（建议使用 qwen-plus 或更高版本）

## 📄 许可

本项目仅用于学习目的。

## 🙏 致谢

感谢 Qwen 团队提供的优秀框架和文档！

