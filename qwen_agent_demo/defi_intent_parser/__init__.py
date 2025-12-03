"""
DeFi 意图解析包。

目前仅提供最小的 Swap 意图解析函数：
- parse_swap_intent(text): 从自然语言中抽取链名、代币和金额等字段。
"""

from .parser import parse_swap_intent

__all__ = ["parse_swap_intent"]


