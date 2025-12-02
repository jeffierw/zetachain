"""
基础 Qwen-Agent 示例
演示如何使用 Qwen-Agent 框架进行基本对话
"""
import os
from dotenv import load_dotenv
from qwen_agent.agents import Assistant
from qwen_agent.llm import get_chat_model

# 加载环境变量
load_dotenv()

def main():
    """运行基础 Agent 示例"""
    
    # 配置 API Key（复用 qwen_demo 中的 key）
    api_key = os.getenv('DASHSCOPE_API_KEY', 'xxx')
    model_name = os.getenv('MODEL_NAME', 'qwen-plus')
    
    print("=" * 60)
    print("基础 Qwen-Agent 示例")
    print("=" * 60)
    print(f"使用模型: {model_name}")
    print()
    
    # 初始化 LLM 配置
    llm_cfg = {
        'model': model_name,
        'api_key': api_key,
        'model_server': 'dashscope',  # 使用阿里云 DashScope
    }
    
    # 创建 LLM 实例
    llm = get_chat_model(llm_cfg)
    
    # 创建 Agent（使用 Assistant，这是最基础的 Agent）
    agent = Assistant(
        llm=llm,
        name='技术助手',
        description='一个专业的技术领域助手',
        system_message='你是一个技术领域的专业助手，能够用简洁易懂的语言解答问题。'
    )
    
    # 测试对话
    test_queries = [
        "请用简洁易懂的语言介绍 ZetaChain 是什么？它的核心特点是什么？",
        "什么是区块链跨链技术？",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n【问题 {i}】{query}")
        print("-" * 60)
        
        # 调用 Agent（流式输出）
        responses = []
        for response in agent.run(messages=[{'role': 'user', 'content': query}]):
            responses.append(response)
        
        # 获取最终回复
        if responses:
            final_response = responses[-1]
            for msg in final_response:
                if msg.get('role') == 'assistant' and 'content' in msg:
                    print(msg['content'])
                    print()
    
    print("=" * 60)
    print("基础示例完成！")
    print()
    print("对比说明：")
    print("- qwen_demo/index.js: 直接调用 OpenAI 兼容 API")
    print("- basic_agent.py: 使用 Qwen-Agent 框架，具备 Agent 能力")
    print("- 下一步：在 agent_with_tools.py 中体验工具调用能力")
    print("=" * 60)

if __name__ == '__main__':
    main()

