import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry


class TestRefreshToken:
    """刷新令牌接口测试"""

    def test_refresh_admin_token(self, admin_token):
        """测试刷新管理员令牌"""
        url = f"{API_BASE_URL}/admin/refresh-token"
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.post(url, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_refresh_shop_token(self, shop_owner_token):
        """测试刷新商家令牌"""
        url = f"{API_BASE_URL}/shop/refresh-token"
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.post(url, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200
