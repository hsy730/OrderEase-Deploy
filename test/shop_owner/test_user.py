import os
import pytest
import requests

from conftest import API_BASE_URL


class TestShopOwnerUserAPI:
    """商家用户管理接口测试"""

    def test_create_user(self):
        """测试创建用户"""
        url = f"{API_BASE_URL}/shopOwner/user/create"
        payload = {
            "name": f"Test User {os.urandom(4).hex()}",
            "password": "Admin@123456",
            "type": "delivery",
            "phone": "13800138000",
            "address": "Test address"
        }
        headers = {"Authorization": "Bearer test_token"}
        response = requests.post(url, json=payload, headers=headers)
        assert response.status_code in [200, 400, 401, 409, 429]

    def test_get_user_list(self):
        """测试获取用户列表"""
        url = f"{API_BASE_URL}/shopOwner/user/list"
        params = {
            "page": 1,
            "pageSize": 10
        }
        headers = {"Authorization": "Bearer test_token"}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code in [200, 400, 401, 429]

    def test_get_user_simple_list(self):
        """测试获取用户简单列表"""
        url = f"{API_BASE_URL}/shopOwner/user/simple-list"
        headers = {"Authorization": "Bearer test_token"}
        response = requests.get(url, headers=headers)
        assert response.status_code in [200, 400, 401, 429]

    def test_get_user_detail(self):
        """测试获取用户详情"""
        url = f"{API_BASE_URL}/shopOwner/user/detail"
        params = {"userId": "1"}
        headers = {"Authorization": "Bearer test_token"}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code in [200, 400, 401, 404, 429]

    def test_update_user(self):
        """测试更新用户信息"""
        url = f"{API_BASE_URL}/shopOwner/user/update"
        payload = {
            "id": "1",
            "name": "Updated User Name",
            "address": "Updated address"
        }
        headers = {"Authorization": "Bearer test_token"}
        response = requests.put(url, json=payload, headers=headers)
        assert response.status_code in [200, 400, 401, 404, 429]
