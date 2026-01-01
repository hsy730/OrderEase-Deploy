import pytest
import requests

from conftest import API_BASE_URL


class TestLogin:
    """登录接口测试"""

    def test_universal_login_admin(self):
        """测试管理员登录"""
        url = f"{API_BASE_URL}/login"
        payload = {
            "username": "admin",
            "password": "Admin@123456"
        }
        response = requests.post(url, json=payload)
        assert response.status_code == 200

    def test_universal_login_shop_owner(self):
        """测试商家登录"""
        url = f"{API_BASE_URL}/login"
        payload = {
            "username": "shop1",
            "password": "Admin@123456"
        }
        response = requests.post(url, json=payload)
        assert response.status_code == 200
