import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry


class TestTempLogin:
    """临时令牌登录接口测试"""

    def test_temp_token_login(self):
        """测试临时令牌登录"""
        url = f"{API_BASE_URL}/shop/temp-login"
        payload = {
            "shop_id": 1,
            "token": "test_temp_token"
        }
        
        def request_func():
            return requests.post(url, json=payload)
        
        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400], f"Expected 200 or 400, got {response.status_code}"
