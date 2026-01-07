"""
前端用户认证静态方法
"""

import os
import requests

from conftest import API_BASE_URL, make_request_with_retry


class FrontendAuthHelper:
    """前端用户认证辅助类 - 提供静态方法"""

    @staticmethod
    def frontend_user_login(username, password="Admin@123456"):
        """测试前端用户登录

        Args:
            username: 用户名
            password: 密码

        Returns:
            response: HTTP响应对象
        """
        url = f"{API_BASE_URL}/user/login"
        payload = {
            "username": username,
            "password": password
        }

        def request_func():
            return requests.post(url, json=payload)

        return make_request_with_retry(request_func)

    @staticmethod
    def frontend_user_register(username, password="Admin@123456"):
        """测试前端用户注册

        Args:
            username: 用户名
            password: 密码

        Returns:
            response: HTTP响应对象
        """
        url = f"{API_BASE_URL}/user/register"
        payload = {
            "username": username,
            "password": password
        }

        def request_func():
            return requests.post(url, json=payload)

        return make_request_with_retry(request_func)

    @staticmethod
    def check_username_exists(username):
        """测试检查用户名是否存在

        Args:
            username: 用户名

        Returns:
            response: HTTP响应对象
        """
        url = f"{API_BASE_URL}/user/check-username"
        params = {"username": username}

        def request_func():
            return requests.get(url, params=params)

        return make_request_with_retry(request_func)
