import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry


class TestLogout:
    """登出接口测试"""

    def test_admin_logout(self, admin_token):
        """测试管理员登出"""
        url = f"{API_BASE_URL}/admin/logout"
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.post(url, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_shop_owner_logout(self, shop_owner_token):
        """测试商家登出"""
        url = f"{API_BASE_URL}/shopOwner/logout"
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.post(url, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 401], f"Expected 200 or 401, got {response.status_code}"
