"""
响应验证工具模块 - 提供统一的响应数据验证功能
"""

from typing import Any, Dict, List, Optional, Union
import pytest
from .field_resolver import FieldResolver


class ResponseValidator:
    """响应验证器类 - 提供链式验证API"""

    def __init__(self, response):
        self.response = response
        self.json_data = None

    def status(self, expected_status: Union[int, List[int]]):
        """验证状态码

        Args:
            expected_status: 期望的状态码，可以是单个整数或整数列表

        Returns:
            self - 支持链式调用
        """
        if isinstance(expected_status, list):
            assert self.response.status_code in expected_status, (
                f"状态码验证失败: 期望 {expected_status}, "
                f"实际 {self.response.status_code}\n响应: {self.response.text}"
            )
        else:
            assert self.response.status_code == expected_status, (
                f"状态码验证失败: 期望 {expected_status}, "
                f"实际 {self.response.status_code}\n响应: {self.response.text}"
            )
        return self

    def has_data(self):
        """验证响应包含data字段

        Returns:
            self - 支持链式调用
        """
        if self.json_data is None:
            self.json_data = self.response.json()

        assert "data" in self.json_data or any(
            key in self.json_data for key in ["id", "ID", "order_id", "shop_id", "product_id", "user_id", "tag_id"]
        ), f"响应缺少data或ID字段: {self.json_data}"
        return self

    def has_field(self, field_path: str, expected_type: type = None):
        """验证响应包含指定字段（支持嵌套路径如 'data.user.id'）

        Args:
            field_path: 字段路径，支持点号分隔的嵌套路径
            expected_type: 期望的字段类型（可选）

        Returns:
            self - 支持链式调用
        """
        if self.json_data is None:
            self.json_data = self.response.json()

        # 使用 FieldResolver 获取嵌套字段（支持命名变体）
        value = FieldResolver.get_nested_field(self.json_data, field_path)

        assert value is not None, f"响应缺少字段: {field_path}"

        if expected_type:
            assert isinstance(value, expected_type), (
                f"字段 {field_path} 类型错误: 期望 {expected_type}, 实际 {type(value)}"
            )

        return self

    def field_equals(self, field_path: str, expected_value: Any):
        """验证字段值等于期望值

        Args:
            field_path: 字段路径，支持点号分隔的嵌套路径
            expected_value: 期望的字段值

        Returns:
            self - 支持链式调用
        """
        if self.json_data is None:
            self.json_data = self.response.json()

        # 使用 FieldResolver 获取嵌套字段（支持命名变体）
        value = FieldResolver.get_nested_field(self.json_data, field_path)

        assert value is not None, f"字段 {field_path} 不存在"
        assert value == expected_value, (
            f"字段 {field_path} 值不匹配: 期望 {expected_value}, 实际 {value}"
        )
        return self

    def field_contains(self, field_path: str, substring: str):
        """验证字段值包含子串

        Args:
            field_path: 字段路径
            substring: 期望包含的子串

        Returns:
            self - 支持链式调用
        """
        if self.json_data is None:
            self.json_data = self.response.json()

        # 使用 FieldResolver 获取嵌套字段（支持命名变体）
        value = FieldResolver.get_nested_field(self.json_data, field_path)

        assert value is not None, f"字段 {field_path} 不存在"
        assert isinstance(value, str), f"字段 {field_path} 不是字符串类型"
        assert substring in value, f"字段 {field_path} (值: {value}) 不包含子串: {substring}"
        return self

    def list_length(self, field_path: str, expected_length: int = None, min_length: int = 0):
        """验证列表字段长度

        Args:
            field_path: 字段路径
            expected_length: 期望的确切长度（可选）
            min_length: 期望的最小长度（默认0）

        Returns:
            self - 支持链式调用
        """
        if self.json_data is None:
            self.json_data = self.response.json()

        # 使用 FieldResolver 获取嵌套字段（支持命名变体）
        value = FieldResolver.get_nested_field(self.json_data, field_path)

        assert value is not None, f"字段 {field_path} 不存在"
        assert isinstance(value, list), f"字段 {field_path} 不是列表类型"
        assert len(value) >= min_length, f"列表 {field_path} 长度 {len(value)} 小于最小值 {min_length}"

        if expected_length is not None:
            assert len(value) == expected_length, (
                f"列表 {field_path} 长度不匹配: 期望 {expected_length}, 实际 {len(value)}"
            )

        return self

    def extract_id(self) -> Optional[Any]:
        """提取响应中的ID（兼容多种格式）

        Returns:
            ID值，如果找不到则返回None
        """
        if self.json_data is None:
            self.json_data = self.response.json()

        # 使用 FieldResolver 提取ID（自动处理多种命名格式）
        return FieldResolver.extract_id(self.json_data)


def validate_response(response, expected_status=200):
    """便捷函数：创建ResponseValidator实例并验证状态码

    Args:
        response: HTTP响应对象
        expected_status: 期望的状态码

    Returns:
        ResponseValidator实例
    """
    return ResponseValidator(response).status(expected_status)


def assert_success_response(response, expected_data_keys: List[str] = None):
    """断言成功响应（状态码200）

    Args:
        response: HTTP响应对象
        expected_data_keys: 期望响应包含的data字段键列表

    Returns:
        ResponseValidator实例
    """
    validator = ResponseValidator(response)
    validator.status(200)

    if expected_data_keys:
        for key in expected_data_keys:
            validator.has_field(f"data.{key}" if "data" in response.json() else key)

    return validator


def assert_error_response(response, expected_status: int, expected_message: str = None):
    """断言错误响应

    Args:
        response: HTTP响应对象
        expected_status: 期望的错误状态码
        expected_message: 期望的错误消息（可选）

    Returns:
        ResponseValidator实例
    """
    validator = ResponseValidator(response)
    validator.status(expected_status)

    if expected_message:
        json_data = response.json()
        error_msg = json_data.get("error") or json_data.get("message") or str(json_data)
        assert expected_message in error_msg, (
            f"错误消息不匹配: 期望包含 '{expected_message}', 实际 '{error_msg}'"
        )

    return validator
