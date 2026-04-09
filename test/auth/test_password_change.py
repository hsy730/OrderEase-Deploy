"""
密码修改接口测试
"""

import pytest
import requests
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import API_BASE_URL, make_request_with_retry


class TestAdminPasswordChange:
    """管理员密码修改接口测试"""

    def test_change_admin_password_same_password(self, admin_token):
        """测试新旧密码相同（应失败）"""
        url = f"{API_BASE_URL}/admin/change-password"
        payload = {
            "old_password": "Admin@123456",
            "new_password": "Admin@123456"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}

        def request_func():
            return requests.post(url, json=payload, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 400, f"新旧密码相同时应返回400，实际: {response.status_code}"
        print("✓ 新旧密码相同正确返回400错误")

    def test_change_admin_password_weak_password(self, admin_token):
        """测试使用弱密码（应失败）"""
        url = f"{API_BASE_URL}/admin/change-password"
        payload = {
            "old_password": "Admin@123456",
            "new_password": "123"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}

        def request_func():
            return requests.post(url, json=payload, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 400, f"弱密码应返回400，实际: {response.status_code}"
        print("✓ 弱密码正确返回400错误")

    def test_change_admin_password_missing_fields(self, admin_token):
        """测试缺少必填字段"""
        url = f"{API_BASE_URL}/admin/change-password"
        payload = {
            "new_password": "NewPassword@123456"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}

        def request_func():
            return requests.post(url, json=payload, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 400, f"缺少字段应返回400，实际: {response.status_code}"
        print("✓ 缺少必填字段正确返回400错误")
