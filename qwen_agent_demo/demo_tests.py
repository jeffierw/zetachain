"""
Agent 工具调用演示测试
运行预设的测试场景，展示 Agent 的工具调用能力
"""
import os
from dotenv import load_dotenv
from qwen_agent.agents import Assistant
from qwen_agent.llm import get_chat_model

# 导入自定义工具
from custom_tools import ToUppercaseTool, CalculateSumTool, StringInfoTool

# 加载环境变量
load_dotenv()


def run_test(agent, query, test_name):
    """运行单个测试"""
    print("\n" + "=" * 70)
    print(f"【测试】{test_name}")
    print("=" * 70)
    print(f"👤 问题: {query}\n")
    
    responses = []
    for response in agent.run(messages=[{'role': 'user', 'content': query}]):
        responses.append(response)
    
    if responses:
        final_response = responses[-1]
        
        # 检查是否有工具调用
        has_tool = False
        for msg in final_response:
            if 'function_call' in msg or msg.get('role') == 'function':
                has_tool = True
                break
        
        if has_tool:
            print("🔧 Agent 响应流程:")
            for msg in final_response:
                if 'function_call' in msg:
                    func_call = msg['function_call']
                    print(f"  → 调用工具: {func_call.get('name')}")
                    print(f"    参数: {func_call.get('arguments')}")
                
                if msg.get('role') == 'function':
                    print(f"  ← 工具返回: {msg.get('content')}")
        
        # 打印最终回复
        for msg in final_response:
            if msg.get('role') == 'assistant' and 'content' in msg:
                content = msg.get('content', '')
                if content:
                    print(f"\n🤖 Agent 回复:\n{content}")


def main():
    """主函数"""
    api_key = os.getenv('DASHSCOPE_API_KEY', 'xxx')
    model_name = os.getenv('MODEL_NAME', 'qwen-plus')
    
    print("\n" + "=" * 70)
    print("  Qwen-Agent 工具调用演示测试")
    print("=" * 70)
    print(f"模型: {model_name}")
    print(f"工具: to_uppercase, calculate_sum, string_info\n")
    
    # 初始化
    llm_cfg = {
        'model': model_name,
        'api_key': api_key,
        'model_server': 'dashscope',
    }
    llm = get_chat_model(llm_cfg)
    
    tools = [
        ToUppercaseTool(),
        CalculateSumTool(),
        StringInfoTool(),
    ]
    
    agent = Assistant(
        llm=llm,
        name='工具助手',
        description='一个能够使用各种工具完成任务的智能助手',
        system_message='''你是一个智能助手，能够使用工具来完成用户的请求。
当用户需要转换大写时使用 to_uppercase 工具；
需要计算加法时使用 calculate_sum 工具；
需要分析字符串时使用 string_info 工具。
请给出简洁友好的回复。''',
        function_list=tools,
    )
    
    # 运行测试
    tests = [
        ("请把 'hello world' 转换成大写", "字符串转大写"),
        ("帮我计算 123 加 456", "计算两数之和"),
        ("分析 'ZetaChain 2024' 这个字符串", "字符串信息分析"),
        ("什么是 Agent？", "普通对话（无工具）"),
        ("把 python 转大写，然后告诉我有几个字母", "复合任务"),
    ]
    
    for query, name in tests:
        run_test(agent, query, name)
    
    print("\n" + "=" * 70)
    print("✅ 所有测试完成！")
    print("=" * 70)
    print("\n💡 提示: 运行 'python agent_with_tools.py' 进行交互式对话\n")


if __name__ == '__main__':
    main()

