import json
from typing import Any

from qwen_agent.tools.base import BaseTool, register_tool

from .parser import parse_swap_intent


@register_tool("parse_swap_intent")
class ParseSwapIntentTool(BaseTool):
    """解析 DeFi Swap 意图的工具"""

    description = (
        "从用户的自然语言输入中解析 DeFi Swap 意图，"
        "提取链名、输入代币、输出代币和金额等字段。"
    )
    parameters = [
        {
            "name": "text",
            "type": "string",
            "description": "用户的原始自然语言输入，例如：'帮我在 Base 上用 10 USDC 换成 ETH'",
            "required": True,
        }
    ]

    def call(self, params: Any, **kwargs) -> str:
        """
        执行工具调用。

        Args:
            params: JSON 字符串或字典，包含 'text' 字段。

        Returns:
            字符串形式的 JSON，包含解析后的意图字段。
        """
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except json.JSONDecodeError:
                return json.dumps({"error": "参数解析失败，期望 JSON 字符串或字典。"}, ensure_ascii=False)

        text = params.get("text", "")
        if not text:
            return json.dumps({"error": "缺少必需参数 text。"}, ensure_ascii=False)

        intent = parse_swap_intent(text)
        return json.dumps(intent, ensure_ascii=False)


