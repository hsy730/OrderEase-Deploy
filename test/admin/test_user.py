# 该文件已被重构为 user_actions.py，仅保留用于参考，不再作为测试执行
__test__ = False

import os
import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry


class TestAdminUserAPI:
    """管理员用户管理接口测试"""

    def test_create_user(self, admin_token):
        """测试创建用户"""
        url = f"{API_BASE_URL}/admin/user/create"
        payload = {
            "name": f"Test User {os.urandom(4).hex()}",
            "password": "Admin@123456",
            "type": "delivery",
            "phone": "13800138000",
            "address": "Test address"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 401, 409]

    def test_get_user_list(self, admin_token):
        """测试获取用户列表"""
        url = f"{API_BASE_URL}/admin/user/list"
        params = {
            "page": 1,
            "pageSize": 10
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_get_user_simple_list(self, admin_token):
        """测试获取用户简单列表"""
        url = f"{API_BASE_URL}/admin/user/simple-list"
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_get_user_detail(self, admin_token, test_user_id):
        """测试获取用户详情"""
        url = f"{API_BASE_URL}/admin/user/detail"
        params = {"id": test_user_id if test_user_id else 1}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_update_user(self, admin_token, test_user_id):
        """测试更新用户信息"""
        url = f"{API_BASE_URL}/admin/user/update"
        payload = {
            "id": str(test_user_id) if test_user_id else "1",
            "name": "Updated User Name",
            "address": "Updated address"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
            
        def request_func():
            return requests.put(url, json=payload, headers=headers)
            
        response = make_request_with_retry(request_func)
        try:
            assert response.status_code == 200
        except AssertionError:
            print(f"更新用户信息失败，请求参数: {payload}, 状态码: {response.status_code}, 响应内容: {response.text}")
            raise
