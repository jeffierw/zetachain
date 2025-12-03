"""
DeFi Swap 意图解析 Agent
专门用于从自然语言中解析 DeFi Swap 操作参数，返回结构化 JSON
"""
import json
import os
from dotenv import load_dotenv
from qwen_agent.agents import Assistant
from qwen_agent.llm import get_chat_model

from defi_intent_parser.tool import ParseSwapIntentTool

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
    
    print_section("DeFi Swap 意图解析 Agent")
    print("\n💡 提示：")
    print("  - 输入 DeFi Swap 相关的自然语言，例如：")
    print("    • 帮我在 Base 上用 10 USDC 换成 ETH")
    print("    • 把我 50 U 兑换成 Polygon 上的 MATIC")
    print("  - Agent 会自动解析并返回 JSON 格式的结果")
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
        tool_result_json = None
        
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
                    tool_result = msg.get('content', '')
                    print_tool_result(tool_result)
                    # 尝试解析工具返回的 JSON
                    try:
                        tool_result_json = json.loads(tool_result)
                    except json.JSONDecodeError:
                        pass
                
                # 获取助手最终回复
                if role == 'assistant' and 'content' in msg:
                    content = msg.get('content', '')
                    if content:
                        assistant_reply = content
            
            # 打印最终回复（优先显示解析出的 JSON）
            if tool_called and tool_result_json:
                print(f"\n📋 解析结果 (JSON):")
                print(json.dumps(tool_result_json, ensure_ascii=False, indent=2))
            elif assistant_reply:
                # 如果 Agent 有回复，也显示出来
                print(f"\n🤖 Agent: {assistant_reply}")
            
            # 更新对话历史（添加助手的回复）
            if assistant_reply:
                messages.append({'role': 'assistant', 'content': assistant_reply})


def main():
    """主函数"""
    
    # 配置 API
    api_key = os.getenv('DASHSCOPE_API_KEY', 'xxx')
    model_name = os.getenv('MODEL_NAME', 'qwen-plus')
    
    print_section("DeFi Swap 意图解析 Agent")
    print(f"\n📋 配置信息:")
    print(f"   模型: {model_name}")
    print(f"   工具: parse_swap_intent")
    
    # 初始化 LLM
    llm_cfg = {
        'model': model_name,
        'api_key': api_key,
        'model_server': 'dashscope',
    }
    llm = get_chat_model(llm_cfg)
    
    # 创建工具实例
    tools = [
        ParseSwapIntentTool(),
    ]
    
    # 创建 Agent 并挂载工具
    agent = Assistant(
        llm=llm,
        name='DeFi Swap 解析助手',
        description='专门用于解析 DeFi Swap 意图的智能助手',
        system_message='''你是一个专门用于解析 DeFi Swap 意图的助手。

当用户输入 DeFi Swap 相关的自然语言时（例如："帮我在 Base 上用 10 USDC 换成 ETH"），
你需要：
1. 自动调用 parse_swap_intent 工具来解析用户的意图
2. 工具会返回一个 JSON 对象，包含 chain、tokenIn、tokenOut、amount 等字段
3. 你只需要直接返回这个 JSON 对象，格式如下：
   {
     "chain": "base",
     "tokenIn": "USDC",
     "tokenOut": "ETH",
     "amount": "10"
   }

请直接返回 JSON，不要添加额外的解释文字。如果解析失败，返回错误信息。''',
        function_list=tools,  # 挂载工具
    )
    
    # 开始交互式对话
    chat_with_agent(agent)
    
    # 结束提示
    print("\n" + "=" * 70)
    print("使用说明：")
    print("  - 输入自然语言描述 DeFi Swap 操作")
    print("  - Agent 会自动解析并返回 JSON 格式的结构化数据")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()

