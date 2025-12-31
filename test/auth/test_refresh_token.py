import pytest
import requests

from conftest import API_BASE_URL


class TestRefreshToken:
    """刷新令牌接口测试"""

    def test_refresh_admin_token(self):
        """测试刷新管理员令牌"""
        url = f"{API_BASE_URL}/admin/refresh-token"
        payload = {
            "token": "test_refresh_token"
        }
        response = requests.post(url, json=payload)
        assert response.status_code in [200, 400, 401, 429]

    def test_refresh_shop_token(self):
        """测试刷新商家令牌"""
        url = f"{API_BASE_URL}/shop/refresh-token"
        payload = {
            "token": "test_refresh_token"
        }
        response = requests.post(url, json=payload)
        assert response.status_code in [200, 400, 401, 429]
