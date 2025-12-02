"""
集成自定义工具的交互式 Agent
你可以不断提问，Agent 会自动调用工具回答问题
"""
import os
from dotenv import load_dotenv
from qwen_agent.agents import Assistant
from qwen_agent.llm import get_chat_model

# 导入自定义工具（导入后会自动注册）
from custom_tools import ToUppercaseTool, CalculateSumTool, StringInfoTool

# 加载环境变量
load_dotenv()


def print_section(title):
    """打印分隔标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_tool_call(tool_name, arguments):
    """打印工具调用信息"""
    print(f"\n🔧 [调用工具] {tool_name}")
    print(f"   参数: {arguments}")


def print_tool_result(result):
    """打印工具返回结果"""
    print(f"✅ [工具返回] {result}")


def chat_with_agent(agent):
    """
    与 Agent 进行交互式对话
    
    Args:
        agent: Agent 实例
    """
    # 对话历史（用于多轮对话）
    messages = []
    
    print_section("开始对话")
    print("\n💡 提示：")
    print("  - 你可以让 Agent 将字符串转大写")
    print("  - 你可以让 Agent 计算两个数的和")
    print("  - 你可以让 Agent 分析字符串信息")
    print("  - 也可以直接聊天，Agent 会自动判断是否需要调用工具")
    print("\n  输入 'exit'、'quit' 或 '退出' 来结束对话")
    print("=" * 70)
    
    while True:
        # 获取用户输入
        try:
            user_input = input("\n👤 你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 再见！")
            break
        
        # 检查退出命令
        if user_input.lower() in ['exit', 'quit', '退出', 'q']:
            print("\n👋 再见！")
            break
        
        if not user_input:
            continue
        
        # 添加用户消息到历史
        messages.append({'role': 'user', 'content': user_input})
        
        # 调用 Agent
        print("\n🤖 Agent: ", end='', flush=True)
        
        responses = []
        tool_called = False
        
        for response in agent.run(messages=messages):
            responses.append(response)
        
        # 处理响应
        if responses:
            final_response = responses[-1]
            assistant_reply = ""
            
            for msg in final_response:
                role = msg.get('role', 'unknown')
                
                # 检测工具调用
                if 'function_call' in msg:
                    if not tool_called:
                        print()  # 换行
                        tool_called = True
                    func_call = msg['function_call']
                    print_tool_call(
                        func_call.get('name', 'unknown'),
                        func_call.get('arguments', {})
                    )
                
                # 显示工具返回
                if role == 'function':
                    print_tool_result(msg.get('content', ''))
                
                # 获取助手最终回复
                if role == 'assistant' and 'content' in msg:
                    content = msg.get('content', '')
                    if content:
                        assistant_reply = content
            
            # 打印最终回复
            if tool_called:
                print(f"\n🤖 Agent: {assistant_reply}")
            else:
                print(assistant_reply)
            
            # 更新对话历史（添加助手的回复）
            if assistant_reply:
                messages.append({'role': 'assistant', 'content': assistant_reply})


def main():
    """主函数"""
    
    # 配置 API
    api_key = os.getenv('DASHSCOPE_API_KEY', 'xxx')
    model_name = os.getenv('MODEL_NAME', 'qwen-plus')
    
    print_section("Qwen-Agent 交互式工具助手")
    print(f"\n📋 配置信息:")
    print(f"   模型: {model_name}")
    print(f"   可用工具: to_uppercase, calculate_sum, string_info")
    
    # 初始化 LLM
    llm_cfg = {
        'model': model_name,
        'api_key': api_key,
        'model_server': 'dashscope',
    }
    llm = get_chat_model(llm_cfg)
    
    # 创建工具实例
    tools = [
        ToUppercaseTool(),
        CalculateSumTool(),
        StringInfoTool(),
    ]
    
    # 创建 Agent 并挂载工具
    agent = Assistant(
        llm=llm,
        name='工具助手',
        description='一个能够使用各种工具完成任务的智能助手',
        system_message='''你是一个智能助手，能够使用工具来完成用户的请求。
当用户需要：
- 将字符串转换为大写时，使用 to_uppercase 工具
- 计算两个数的和时，使用 calculate_sum 工具
- 分析字符串信息时，使用 string_info 工具

请根据用户的需求自动选择合适的工具，并给出友好的回复。
回复要简洁明了。''',
        function_list=tools,  # 挂载工具
    )
    
    # 开始交互式对话
    chat_with_agent(agent)
    
    # 结束提示
    print("\n" + "=" * 70)
    print("学习要点总结：")
    print("  1. Agent 能够根据用户意图自动选择并调用工具")
    print("  2. 工具调用对用户是透明的，Agent 会自动处理")
    print("  3. Agent 可以在对话中灵活切换使用工具或直接回答")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()

