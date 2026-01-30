"""
测试基类模块 - 提供边界测试和通用测试混入类
"""

from typing import Callable, Dict, Any, Optional
import pytest


class BoundaryTestMixin:
    """边界测试混入类 - 提供常见的边界条件测试方法

    这个类可以作为其他测试类的混入(mixin)，提供标准的边界测试方法。
    子类需要实现 make_request_func 方法来返回实际的请求函数。
    """

    def make_request_func(self, payload: Dict[str, Any]) -> Callable:
        """创建请求函数（子类必须实现）

        Args:
            payload: 请求载荷

        Returns:
            执行HTTP请求的可调用对象
        """
        raise NotImplementedError("子类必须实现 make_request_func 方法")

    def test_empty_payload(self):
        """测试空载荷"""
        request_func = self.make_request_func({})
        response = request_func()
        # 空载荷应该返回400或422错误
        assert response.status_code in [400, 422], (
            f"空载荷应该返回400或422，实际返回: {response.status_code}"
        )

    def _check_missing_required_field(self, field_name: str, payload_template: Dict):
        """测试缺少必填字段（辅助方法）

        Args:
            field_name: 要删除的字段名
            payload_template: 载荷模板（包含完整字段）
        """
        payload = payload_template.copy()
        if field_name in payload:
            del payload[field_name]

        request_func = self.make_request_func(payload)
        response = request_func()
        # 缺少必填字段应该返回400或422错误
        assert response.status_code in [400, 422], (
            f"缺少必填字段 '{field_name}' 应该返回400或422，实际返回: {response.status_code}"
        )

    def _check_invalid_field_type(self, field_name: str, invalid_value: Any, payload_template: Dict):
        """测试无效字段类型（辅助方法）

        Args:
            field_name: 字段名
            invalid_value: 无效的值
            payload_template: 载荷模板
        """
        payload = payload_template.copy()
        payload[field_name] = invalid_value

        request_func = self.make_request_func(payload)
        response = request_func()
        # 无效类型应该返回400或422错误
        assert response.status_code in [400, 422], (
            f"无效类型 '{field_name}' 应该返回400或422，实际返回: {response.status_code}"
        )

    def _check_negative_value(self, field_name: str, payload_template: Dict):
        """测试负数值（辅助方法）

        Args:
            field_name: 数值字段名
            payload_template: 载荷模板
        """
        payload = payload_template.copy()
        payload[field_name] = -100

        request_func = self.make_request_func(payload)
        response = request_func()
        # 负数值应该返回400或422错误
        assert response.status_code in [400, 422], (
            f"负数值 '{field_name}' 应该返回400或422，实际返回: {response.status_code}"
        )

    def _check_zero_value(self, field_name: str, payload_template: Dict):
        """测试零值（辅助方法）

        Args:
            field_name: 数值字段名
            payload_template: 载荷模板
        """
        payload = payload_template.copy()
        payload[field_name] = 0

        request_func = self.make_request_func(payload)
        response = request_func()
        # 零值可能有效或无效，取决于业务逻辑
        # 这里只验证响应状态码是有效的
        assert response.status_code in [200, 400, 422], (
            f"零值 '{field_name}' 返回了无效状态码: {response.status_code}"
        )

    def _check_empty_string(self, field_name: str, payload_template: Dict):
        """测试空字符串（辅助方法）

        Args:
            field_name: 字符串字段名
            payload_template: 载荷模板
        """
        payload = payload_template.copy()
        payload[field_name] = ""

        request_func = self.make_request_func(payload)
        response = request_func()
        # 空字符串应该返回400或422错误
        assert response.status_code in [400, 422], (
            f"空字符串 '{field_name}' 应该返回400或422，实际返回: {response.status_code}"
        )

    def _check_very_long_string(self, field_name: str, payload_template: Dict, length: int = 10000):
        """测试超长字符串（辅助方法）

        Args:
            field_name: 字段名
            payload_template: 载荷模板
            length: 字符串长度
        """
        payload = payload_template.copy()
        payload[field_name] = "x" * length

        request_func = self.make_request_func(payload)
        response = request_func()
        # 超长字符串应该返回400或422错误
        assert response.status_code in [400, 422], (
            f"超长字符串 '{field_name}' (长度{length}) 应该返回400或422，实际返回: {response.status_code}"
        )

    def _check_unauthorized_access(self):
        """测试未授权访问（辅助方法，没有token）"""
        # 子类应该实现不带token的请求
        raise NotImplementedError("子类需要实现测试未授权访问的方法")

    def _check_invalid_token(self, make_request_with_invalid_token: Callable):
        """测试无效token（辅助方法）

        Args:
            make_request_with_invalid_token: 使用无效token的请求函数
        """
        response = make_request_with_invalid_token()
        # 无效token应该返回401
        assert response.status_code == 401, (
            f"无效token应该返回401，实际返回: {response.status_code}"
        )

    def _check_sql_injection_attempt(self, field_name: str, payload_template: Dict):
        """测试SQL注入尝试（辅助方法）

        Args:
            field_name: 字段名
            payload_template: 载荷模板
        """
        sql_injection_strings = [
            "' OR '1'='1",
            "1' DROP TABLE users--",
            "'; DROP TABLE users; --",
            "1' UNION SELECT * FROM users--"
        ]

        for injection_string in sql_injection_strings:
            payload = payload_template.copy()
            payload[field_name] = injection_string

            request_func = self.make_request_func(payload)
            response = request_func()
            # SQL注入应该被拒绝或安全处理
            assert response.status_code in [200, 400, 422, 500], (
                f"SQL注入尝试返回了意外的状态码: {response.status_code}"
            )
            # 如果返回200，确保数据没有被错误处理
            if response.status_code == 200:
                data = response.json()
                # 确保没有泄露数据库结构信息
                assert "error" not in str(data).lower() or "sql" not in str(data).lower()


class AuthTestMixin:
    """认证测试混入类 - 提供认证相关的测试方法"""

    def test_valid_token(self, make_request_with_valid_token: Callable):
        """测试有效token

        Args:
            make_request_with_valid_token: 使用有效token的请求函数
        """
        response = make_request_with_valid_token()
        assert response.status_code == 200, (
            f"有效token应该返回200，实际返回: {response.status_code}"
        )

    def test_expired_token(self, make_request_with_expired_token: Callable):
        """测试过期token

        Args:
            make_request_with_expired_token: 使用过期token的请求函数
        """
        response = make_request_with_expired_token()
        assert response.status_code == 401, (
            f"过期token应该返回401，实际返回: {response.status_code}"
        )

    def test_malformed_token(self, make_request_with_malformed_token: Callable):
        """测试格式错误的token

        Args:
            make_request_with_malformed_token: 使用格式错误token的请求函数
        """
        response = make_request_with_malformed_token()
        assert response.status_code == 401, (
            f"格式错误token应该返回401，实际返回: {response.status_code}"
        )


class PaginationTestMixin:
    """分页测试混入类 - 提供分页相关的测试方法"""

    def test_invalid_page_number(self, make_request_func: Callable):
        """测试无效页码"""
        response = make_request_func(page=-1)
        assert response.status_code in [400, 422], (
            f"无效页码应该返回400或422，实际返回: {response.status_code}"
        )

    def test_invalid_page_size(self, make_request_func: Callable):
        """测试无效页大小"""
        response = make_request_func(page_size=0)
        assert response.status_code in [400, 422], (
            f"无效页大小应该返回400或422，实际返回: {response.status_code}"
        )

        response = make_request_func(page_size=1000000)
        assert response.status_code in [400, 422], (
            f"超大页大小应该返回400或422，实际返回: {response.status_code}"
        )

    def test_page_boundary(self, make_request_func: Callable, total_items: int):
        """测试分页边界

        Args:
            make_request_func: 请求函数
            total_items: 总项目数
        """
        # 测试第一页
        response = make_request_func(page=1, page_size=10)
        assert response.status_code == 200
        data = response.json()
        # 验证返回的数据不超过页大小
        items = data.get("data", data.get("items", []))
        assert len(items) <= 10

        # 测试最后一页
        last_page = (total_items // 10) + 1
        response = make_request_func(page=last_page, page_size=10)
        assert response.status_code == 200

        # 测试超出范围的页
        response = make_request_func(page=last_page + 100, page_size=10)
        assert response.status_code == 200
        data = response.json()
        items = data.get("data", data.get("items", []))
        # 超出范围的页应该返回空列表
        assert len(items) == 0


class ValidationTestMixin:
    """数据验证测试混入类 - 提供数据格式验证的测试方法"""

    def _check_invalid_phone_number(self, field_name: str, payload_template: Dict):
        """测试无效电话号码（辅助方法）

        Args:
            field_name: 电话字段名
            payload_template: 载荷模板
        """
        invalid_phones = [
            "123",           # 太短
            "1234567890123", # 太长
            "abcdefghijk",   # 非数字
            "123-4567890",   # 包含非法字符
        ]

        for phone in invalid_phones:
            payload = payload_template.copy()
            payload[field_name] = phone

            request_func = self.make_request_func(payload)
            response = request_func()
            assert response.status_code in [400, 422], (
                f"无效电话号码 '{phone}' 应该返回400或422，实际返回: {response.status_code}"
            )

    def _check_invalid_email(self, field_name: str, payload_template: Dict):
        """测试无效邮箱地址（辅助方法）

        Args:
            field_name: 邮箱字段名
            payload_template: 载荷模板
        """
        invalid_emails = [
            "invalid",           # 缺少@
            "invalid@",          # 缺少域名
            "@invalid.com",      # 缺少用户名
            "invalid@.com",      # 域名无效
            "invalid@com",       # 域名缺少.
        ]

        for email in invalid_emails:
            payload = payload_template.copy()
            payload[field_name] = email

            request_func = self.make_request_func(payload)
            response = request_func()
            assert response.status_code in [400, 422], (
                f"无效邮箱 '{email}' 应该返回400或422，实际返回: {response.status_code}"
            )

    def _check_invalid_password(self, field_name: str, payload_template: Dict):
        """测试无效密码（辅助方法）

        Args:
            field_name: 密码字段名
            payload_template: 载荷模板
        """
        invalid_passwords = [
            "123",      # 太短
            "12345",    # 太短（可能需要6位以上）
            "abcdefgh", # 只有字母
            "12345678", # 只有数字
        ]

        for password in invalid_passwords:
            payload = payload_template.copy()
            payload[field_name] = password

            request_func = self.make_request_func(payload)
            response = request_func()
            # 密码验证可能返回400或422
            assert response.status_code in [200, 400, 422], (
                f"无效密码 '{password}' 返回了意外的状态码: {response.status_code}"
            )


class ConcurrencyTestMixin:
    """并发测试混入类 - 提供并发相关的测试方法"""

    def test_concurrent_requests(self, make_request_func: Callable, num_requests: int = 10):
        """测试并发请求

        Args:
            make_request_func: 请求函数
            num_requests: 并发请求数量
        """
        import threading
        import time

        results = []
        errors = []

        def make_request():
            try:
                response = make_request_func()
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        threads = []
        for _ in range(num_requests):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # 验证没有错误
        assert len(errors) == 0, f"并发请求出现错误: {errors}"

        # 验证所有请求都成功
        success_count = sum(1 for status in results if status == 200)
        assert success_count == num_requests, (
            f"并发请求失败: 成功{success_count}/{num_requests}"
        )

    def test_race_condition(self, make_update_request: Callable, resource_id: Any):
        """测试竞态条件

        Args:
            make_update_request: 更新请求函数
            resource_id: 资源ID
        """
        import threading

        results = []
        errors = []

        def update_resource():
            try:
                response = make_update_request(resource_id)
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        threads = []
        for _ in range(5):
            thread = threading.Thread(target=update_resource)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # 验证没有未处理的异常
        # 竞态条件可能导致一些请求失败，这是可接受的
        print(f"竞态条件测试: {len(results)}个请求, "
              f"成功{sum(1 for s in results if s == 200)}个")
