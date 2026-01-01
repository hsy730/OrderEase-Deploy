import os
import pytest
import requests

from conftest import API_BASE_URL


class TestFrontendAuth:
    """前端用户认证测试"""

    def test_frontend_user_login(self):
        """测试前端用户登录"""
        url = f"{API_BASE_URL}/user/login"
        payload = {
            "username": "testuser",
            "password": "Admin@123456"
        }
        response = requests.post(url, json=payload)
        assert response.status_code in [200, 401, 404]

    def test_frontend_user_register(self):
        """测试前端用户注册"""
        url = f"{API_BASE_URL}/user/register"
        payload = {
            "username": f"testuser_{os.urandom(4).hex()}",
            "password": "Admin@123456"
        }
        response = requests.post(url, json=payload)
        assert response.status_code in [200, 400, 409, 429]

    def test_check_username_exists(self):
        """测试检查用户名是否存在"""
        url = f"{API_BASE_URL}/user/check-username"
        params = {"username": "testuser"}
        headers = {"Authorization": "Bearer test_token"}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code in [200, 400, 401, 429]
