"""
DeFi Swap 意图解析 + ZetaChain 接口层 Agent

模式与 `defi_agent.py` 基本一致：
- 使用 Qwen-Agent + `ParseSwapIntentTool` 解析自然语言 DeFi Swap 意图；
- 在拿到结构化 JSON 结果后，调用 `ZetaInterfaceLayer` 生成“合约调用计划”；
- 最终仅在控制台打印“准备发起什么交易”（dry-run，无真实上链）。
"""

import json
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from qwen_agent.agents import Assistant
from qwen_agent.llm import get_chat_model

from defi_intent_parser.tool import ParseSwapIntentTool
from zeta_interface_layer import ZetaInterfaceLayer

# 加载环境变量
load_dotenv()


def print_section(title: str) -> None:
    """打印分隔标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_tool_call(tool_name: str, arguments: Dict[str, Any]) -> None:
    """打印工具调用信息"""
    print(f"\n🔧 [调用工具] {tool_name}")
    print(f"   参数: {arguments}")


def print_tool_result(result: str) -> None:
    """打印工具返回结果"""
    print(f"✅ [工具返回] {result}")


def print_plan_summary(intent: Dict[str, Any], interface_layer: ZetaInterfaceLayer) -> None:
    """
    基于解析结果，调用 Zeta 接口层并打印“将要发起的交易计划”信息。
    """
    plan = interface_layer.build_plan(intent)

    # 为了保证输出“交易计划”整体为中文，这里不用底层的 print 方法，
    # 而是自己组装一份中文字段的摘要。
    print("\n🚀 [ZetaChain 接口层] 已根据解析结果生成交易计划：")

    print("\n=== 解析后的意图（parse_swap_intent 输出） ===")
    print(json.dumps(intent, ensure_ascii=False, indent=2))

    # 使用 getattr 以防底层实现稍有变动
    entry_chain = getattr(plan, "entry_chain", "zetachain")
    dst_chain = getattr(plan, "destination_chain", intent.get("chain"))
    contract_name = getattr(plan, "contract_name", "未知合约")
    contract_address = getattr(plan, "contract_address", "<待填写合约地址>")
    method = getattr(plan, "method", "未知方法")
    params = getattr(plan, "params", {})
    notes = getattr(plan, "notes", [])

    cn_payload = {
        "入口链": entry_chain,
        "目标链": dst_chain,
        "调用合约": f"{contract_name} ({contract_address})",
        "调用方法": method,
        "调用参数": params,
        "备注": notes,
    }

    print("\n=== 规划得到的合约调用计划（仅演示，不上链） ===")
    print(json.dumps(cn_payload, ensure_ascii=False, indent=2))

    print("\n✅ 综述：准备发起的交易（示意）")
    print(
        f"- 链路: {entry_chain} -> {dst_chain}\n"
        f"- 合约调用: {contract_name}.{method}\n"
        f"- 参数: {json.dumps(params, ensure_ascii=False)}\n"
        f"- 备注: {' | '.join(map(str, notes))}"
    )


def chat_with_agent(agent: Assistant) -> None:
    """
    与 Agent 进行交互式对话：
    - Agent 负责解析 DeFi Swap 意图（调用 parse_swap_intent 工具）
    - ZetaInterfaceLayer 负责将解析结果映射为 ZetaChain 合约调用计划
    """
    # 对话历史（用于多轮对话）
    messages: List[Dict[str, Any]] = []

    print_section("DeFi Swap 意图解析 + Zeta 接口层 Agent")
    print("\n💡 提示：")
    print("  - 输入 DeFi Swap 相关的自然语言，例如：")
    print("    • 帮我在 Base 上用 10 USDC 换成 ETH")
    print("    • 把我 50 U 兑换成 Polygon 上的 MATIC")
    print("  - Agent 会自动解析并返回 JSON 格式的结果，并生成 ZetaChain 交易计划")
    print("\n  输入 'exit'、'quit' 或 '退出' 来结束对话")
    print("=" * 70)

    interface_layer = ZetaInterfaceLayer()

    while True:
        # 获取用户输入
        try:
            user_input = input("\n👤 你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 再见！")
            break

        # 检查退出命令
        if user_input.lower() in ["exit", "quit", "退出", "q"]:
            print("\n👋 再见！")
            break

        if not user_input:
            continue

        # 添加用户消息到历史
        messages.append({"role": "user", "content": user_input})

        # 调用 Agent
        print("\n🤖 Agent: ", end="", flush=True)

        responses: List[Any] = []
        tool_called = False
        tool_result_json: Dict[str, Any] | None = None

        for response in agent.run(messages=messages):
            responses.append(response)

        # 处理响应
        if responses:
            final_response = responses[-1]
            assistant_reply = ""

            for msg in final_response:
                role = msg.get("role", "unknown")

                # 检测工具调用
                if "function_call" in msg:
                    if not tool_called:
                        print()  # 换行
                        tool_called = True
                    func_call = msg["function_call"]
                    print_tool_call(
                        func_call.get("name", "unknown"),
                        func_call.get("arguments", {}),
                    )

                # 显示工具返回
                if role == "function":
                    tool_result = msg.get("content", "")
                    print_tool_result(tool_result)
                    # 尝试解析工具返回的 JSON
                    try:
                        tool_result_json = json.loads(tool_result)
                    except json.JSONDecodeError:
                        tool_result_json = None

                # 获取助手最终回复
                if role == "assistant" and "content" in msg:
                    content = msg.get("content", "")
                    if content:
                        assistant_reply = content

            # 打印最终解析 JSON
            if tool_called and tool_result_json:
                print(f"\n📋 解析结果 (JSON):")
                print(json.dumps(tool_result_json, ensure_ascii=False, indent=2))

                # 在此基础上，调用 Zeta 接口层生成并打印交易计划
                print_plan_summary(tool_result_json, interface_layer)

            elif assistant_reply:
                # 如果 Agent 有回复，也显示出来
                print(f"\n🤖 Agent: {assistant_reply}")

            # 更新对话历史（添加助手的回复）
            if assistant_reply:
                messages.append({"role": "assistant", "content": assistant_reply})


def main() -> None:
    """主函数：配置 LLM + 工具 + Agent，并启动对话循环。"""

    # 配置 API
    api_key = os.getenv("DASHSCOPE_API_KEY", "xxx")
    model_name = os.getenv("MODEL_NAME", "qwen-plus")

    print_section("DeFi Swap 意图解析 + Zeta 接口层 Agent")
    print(f"\n📋 配置信息:")
    print(f"   模型: {model_name}")
    print(f"   工具: parse_swap_intent + zeta_interface_layer")

    # 初始化 LLM
    llm_cfg = {
        "model": model_name,
        "api_key": api_key,
        "model_server": "dashscope",
    }
    llm = get_chat_model(llm_cfg)

    # 创建工具实例
    tools = [
        ParseSwapIntentTool(),
    ]

    # 创建 Agent 并挂载工具
    agent = Assistant(
        llm=llm,
        name="DeFi Swap + Zeta 接口层助手",
        description="解析 DeFi Swap 意图并生成 ZetaChain 合约调用计划的智能助手",
        system_message="""你是一个专门用于解析 DeFi Swap 意图并生成链上调用计划的助手。

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

后续会有一个后端服务（Zeta 接口层）读取这个 JSON，并规划实际要发起的链上交易。
请直接返回 JSON，不要添加额外的解释文字。如果解析失败，返回错误信息。""",
        function_list=tools,  # 挂载工具
    )

    # 开始交互式对话
    chat_with_agent(agent)

    # 结束提示
    print("\n" + "=" * 70)
    print("使用说明：")
    print("  - 输入自然语言描述 DeFi Swap 操作")
    print("  - Agent 会调用工具解析，并由 Zeta 接口层生成合约调用计划（仅打印，不上链）")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()


