import os
import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry


class TestFrontendAuth:
    """前端用户认证测试"""

    def test_frontend_user_login(self):
        """测试前端用户登录"""
        url = f"{API_BASE_URL}/login"
        payload = {
            "username": "admin",  # 使用默认管理员账户
            "password": "Admin@123456"
        }
        
        def request_func():
            return requests.post(url, json=payload)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_frontend_user_register(self):
        """测试前端用户注册"""
        url = f"{API_BASE_URL}/user/register"
        payload = {
            "username": f"testuser_{os.urandom(4).hex()}",
            "password": "Admin@123456"
        }
        
        def request_func():
            return requests.post(url, json=payload)
        
        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 409]  # 200成功, 400参数错误, 409用户名已存在

    def test_check_username_exists(self):
        """测试检查用户名是否存在"""
        url = f"{API_BASE_URL}/user/check-username"
        params = {"username": "admin"}
        
        def request_func():
            return requests.get(url, params=params)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200
