import pytest
import requests

from conftest import API_BASE_URL


class TestLogout:
    """登出接口测试"""

    def test_admin_logout(self):
        """测试管理员登出"""
        url = f"{API_BASE_URL}/admin/logout"
        headers = {"Authorization": "Bearer test_token"}
        response = requests.post(url, headers=headers)
        assert response.status_code in [200, 401, 429]

    def test_shop_owner_logout(self):
        """测试商家登出"""
        url = f"{API_BASE_URL}/shopOwner/logout"
        headers = {"Authorization": "Bearer test_token"}
        response = requests.post(url, headers=headers)
        assert response.status_code in [200, 401, 429]
