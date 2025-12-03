import re
from typing import Any, Dict, Optional


# 简单的链名映射表（可以根据需要扩展）
CHAIN_ALIASES = {
    "base": "base",
    "Base": "base",
    "BASE": "base",
    "polygon": "polygon",
    "Polygon": "polygon",
    "POLYGON": "polygon",
}


# 简单的代币符号映射表（可以根据需要扩展）
TOKEN_ALIASES = {
    "usdc": "USDC",
    "USDC": "USDC",
    "usdt": "USDT",
    "USDT": "USDT",
    # 口语中的“U”统一先映射为 USDT，后续可根据项目需要调整为 USDC
    "u": "USDT",
    "U": "USDT",
    "eth": "ETH",
    "ETH": "ETH",
    "matic": "MATIC",
    "MATIC": "MATIC",
}


def _normalize_token(token: str) -> Optional[str]:
    """将各种大小写 / 口语 token 归一化为标准代币符号。"""
    if not token:
        return None
    return TOKEN_ALIASES.get(token, TOKEN_ALIASES.get(token.lower()))


def _extract_chain(text: str) -> Optional[str]:
    """从文本中提取链名（Base、Polygon 等），返回规范化后的 chain 标识。"""
    for alias, normalized in CHAIN_ALIASES.items():
        if alias in text:
            return normalized
    return None


def _extract_amount_and_token_in(text: str) -> (Optional[str], Optional[str]):
    """
    提取输入金额和代币：
    - 支持类似“10 USDC”、“50 U”、“5.5 usdt”等形式。
    """
    # 匹配金额 + 代币的简单正则
    pattern = r"(\d+(?:\.\d+)?)\s*([A-Za-z]+|[Uu])"
    match = re.search(pattern, text)
    if not match:
        return None, None
    amount = match.group(1)
    raw_token = match.group(2)
    token = _normalize_token(raw_token)
    return amount, token


def _extract_token_out(text: str) -> Optional[str]:
    """
    根据"换成 / 兑换成 / 换为"等关键字，提取目标代币。
    示例：
    - 帮我在 Base 上用 10 USDC 换成 ETH
    - 把我 50 U 兑换成 Polygon 上的 MATIC
    """
    # 为了简单，这里只找第一个出现"换成/兑换成/换为"的位置
    for kw in ["换成", "兑换成", "换为"]:
        if kw in text:
            idx = text.index(kw) + len(kw)
            tail = text[idx:]
            # 在 tail 中找所有可能的英文串（代币或链名）
            all_matches = re.findall(r"([A-Za-z]+)", tail)
            # 排除链名，找第一个代币符号
            for match in all_matches:
                normalized = _normalize_token(match)
                if normalized and normalized not in CHAIN_ALIASES.values():
                    return normalized
    # 如果没有关键词，就尝试直接在句子末尾找一个代币符号（兜底）
    tail_match = re.search(r"([A-Za-z]{2,})\s*$", text)
    if tail_match:
        normalized = _normalize_token(tail_match.group(1))
        if normalized and normalized not in CHAIN_ALIASES.values():
            return normalized
    return None


def parse_swap_intent(text: str) -> Dict[str, Any]:
    """
    从自然语言文本中解析 DeFi Swap 意图。

    返回一个最小结构的 JSON 字典，例如：
    {
        "chain": "base",
        "tokenIn": "USDC",
        "tokenOut": "ETH",
        "amount": "10"
    }

    解析不出的字段返回 None。
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    chain = _extract_chain(text)
    amount, token_in = _extract_amount_and_token_in(text)
    token_out = _extract_token_out(text)

    return {
        "chain": chain,
        "tokenIn": token_in,
        "tokenOut": token_out,
        "amount": amount,
    }


