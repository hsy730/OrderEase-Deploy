import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry


class TestUnauthorizedAccess:
    """未授权访问测试 - 测试没有token或无效token的情况"""

    def test_admin_api_without_token(self):
        """测试管理员接口未提供token"""
        url = f"{API_BASE_URL}/admin/user/list"
        params = {"page": 1, "pageSize": 10}
        
        def request_func():
            return requests.get(url, params=params)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_admin_api_with_invalid_token(self):
        """测试管理员接口使用无效token"""
        url = f"{API_BASE_URL}/admin/user/list"
        params = {"page": 1, "pageSize": 10}
        headers = {"Authorization": "Bearer invalid_token"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_admin_api_with_expired_token(self):
        """测试管理员接口使用过期token"""
        url = f"{API_BASE_URL}/admin/user/list"
        params = {"page": 1, "pageSize": 10}
        headers = {"Authorization": "Bearer expired_token"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_shop_owner_api_without_token(self):
        """测试商家接口未提供token"""
        url = f"{API_BASE_URL}/shopOwner/user/list"
        params = {"page": 1, "pageSize": 10}
        
        def request_func():
            return requests.get(url, params=params)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_shop_owner_api_with_invalid_token(self):
        """测试商家接口使用无效token"""
        url = f"{API_BASE_URL}/shopOwner/user/list"
        params = {"page": 1, "pageSize": 10}
        headers = {"Authorization": "Bearer invalid_token"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_create_shop_without_token(self):
        """测试创建店铺未提供token"""
        url = f"{API_BASE_URL}/admin/shop/create"
        payload = {
            "name": "Test Shop",
            "owner": "test_owner",
            "password": "Test@123456"
        }
        
        def request_func():
            return requests.post(url, json=payload)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_create_user_without_token(self):
        """测试创建用户未提供token"""
        url = f"{API_BASE_URL}/admin/user/create"
        payload = {
            "name": "Test User",
            "password": "Test@123456",
            "type": "delivery",
            "phone": "13800138000",
            "address": "Test address"
        }
        
        def request_func():
            return requests.post(url, json=payload)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_update_order_without_token(self):
        """测试更新订单未提供token"""
        url = f"{API_BASE_URL}/admin/order/update"
        payload = {
            "id": "1",
            "status": "completed"
        }
        
        def request_func():
            return requests.put(url, json=payload)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_delete_product_without_token(self):
        """测试删除商品未提供token"""
        url = f"{API_BASE_URL}/admin/product/delete"
        payload = {"id": "1"}
        
        def request_func():
            return requests.delete(url, json=payload)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_malformed_token(self):
        """测试格式错误的token"""
        url = f"{API_BASE_URL}/admin/user/list"
        params = {"page": 1, "pageSize": 10}
        headers = {"Authorization": "invalid_format_token"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_empty_token(self):
        """测试空token"""
        url = f"{API_BASE_URL}/admin/user/list"
        params = {"page": 1, "pageSize": 10}
        headers = {"Authorization": "Bearer "}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
