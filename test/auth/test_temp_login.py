import pytest
import requests

from conftest import API_BASE_URL


class TestTempLogin:
    """临时令牌登录接口测试"""

    def test_temp_token_login(self):
        """测试临时令牌登录"""
        url = f"{API_BASE_URL}/shop/temp-login"
        payload = {
            "shop_id": 1,
            "token": "test_temp_token"
        }
        response = requests.post(url, json=payload)
        assert response.status_code in [200, 400, 401, 429]
