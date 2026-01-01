import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry


class TestRefreshToken:
    """刷新令牌接口测试"""

    def test_refresh_admin_token(self):
        """测试刷新管理员令牌"""
        url = f"{API_BASE_URL}/admin/refresh-token"
        payload = {
            "token": "test_refresh_token"
        }
        
        def request_func():
            return requests.post(url, json=payload)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_refresh_shop_token(self):
        """测试刷新商家令牌"""
        url = f"{API_BASE_URL}/shop/refresh-token"
        payload = {
            "token": "test_refresh_token"
        }
        
        def request_func():
            return requests.post(url, json=payload)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
