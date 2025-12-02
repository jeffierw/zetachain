"""
自定义工具实现
使用 Qwen-Agent 的工具注册机制创建自定义工具
"""
import json
from qwen_agent.tools.base import BaseTool, register_tool


@register_tool('to_uppercase')
class ToUppercaseTool(BaseTool):
    """字符串转大写工具"""
    
    description = '将输入的字符串转换为大写字母'
    parameters = [{
        'name': 'text',
        'type': 'string',
        'description': '需要转换为大写的字符串',
        'required': True
    }]
    
    def call(self, params: str, **kwargs) -> str:
        """
        执行工具调用
        
        Args:
            params: JSON 字符串或字典，包含 'text' 参数
            
        Returns:
            转换后的大写字符串
        """
        # 解析参数（可能是字符串或字典）
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except json.JSONDecodeError:
                return '错误：无法解析参数'
        
        text = params.get('text', '')
        
        if not text:
            return '错误：未提供文本内容'
        
        result = text.upper()
        return f'转换结果: {result}'


@register_tool('calculate_sum')
class CalculateSumTool(BaseTool):
    """计算两个数之和的工具"""
    
    description = '计算两个数字的和'
    parameters = [{
        'name': 'a',
        'type': 'number',
        'description': '第一个数字',
        'required': True
    }, {
        'name': 'b',
        'type': 'number',
        'description': '第二个数字',
        'required': True
    }]
    
    def call(self, params: str, **kwargs) -> str:
        """
        执行工具调用
        
        Args:
            params: JSON 字符串或字典，包含 'a' 和 'b' 参数
            
        Returns:
            计算结果的字符串
        """
        # 解析参数（可能是字符串或字典）
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except json.JSONDecodeError:
                return '错误：无法解析参数'
        
        try:
            a = float(params.get('a', 0))
            b = float(params.get('b', 0))
            result = a + b
            return f'{a} + {b} = {result}'
        except (ValueError, TypeError) as e:
            return f'错误：无法计算，请提供有效的数字。详情：{str(e)}'


# 可选：创建一个更复杂的工具示例
@register_tool('string_info')
class StringInfoTool(BaseTool):
    """分析字符串信息的工具"""
    
    description = '分析字符串的详细信息，包括长度、字符统计等'
    parameters = [{
        'name': 'text',
        'type': 'string',
        'description': '需要分析的字符串',
        'required': True
    }]
    
    def call(self, params: str, **kwargs) -> str:
        """
        执行工具调用
        
        Args:
            params: JSON 字符串或字典，包含 'text' 参数
            
        Returns:
            字符串分析结果
        """
        # 解析参数（可能是字符串或字典）
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except json.JSONDecodeError:
                return '错误：无法解析参数'
        
        text = params.get('text', '')
        
        if not text:
            return '错误：未提供文本内容'
        
        # 统计信息
        length = len(text)
        alpha_count = sum(c.isalpha() for c in text)
        digit_count = sum(c.isdigit() for c in text)
        space_count = sum(c.isspace() for c in text)
        
        result = f"""
字符串分析结果：
- 总长度: {length}
- 字母数量: {alpha_count}
- 数字数量: {digit_count}
- 空格数量: {space_count}
- 原文: "{text}"
        """.strip()
        
        return result


if __name__ == '__main__':
    """测试工具功能"""
    print("=" * 60)
    print("自定义工具测试")
    print("=" * 60)
    
    # 测试大写转换工具
    print("\n【测试 1】字符串转大写")
    tool1 = ToUppercaseTool()
    result1 = tool1.call({'text': 'hello world'})
    print(result1)
    
    # 测试加法工具
    print("\n【测试 2】计算两数之和")
    tool2 = CalculateSumTool()
    result2 = tool2.call({'a': 123, 'b': 456})
    print(result2)
    
    # 测试字符串分析工具
    print("\n【测试 3】字符串信息分析")
    tool3 = StringInfoTool()
    result3 = tool3.call({'text': 'Hello 2024!'})
    print(result3)
    
    print("\n" + "=" * 60)
    print("工具测试完成！")
    print("=" * 60)

