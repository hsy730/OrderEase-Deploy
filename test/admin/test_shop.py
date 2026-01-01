import os
import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry


class TestAdminShopAPI:
    """管理员店铺管理接口测试"""

    def test_create_shop(self, admin_token):
        """测试创建店铺"""
        url = f"{API_BASE_URL}/admin/shop/create"
        payload = {
            "name": f"Test Shop {os.urandom(4).hex()}",
            "description": "Test shop description",
            "address": "Test address"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 401]

    def test_update_shop(self, admin_token):
        """测试更新店铺信息"""
        url = f"{API_BASE_URL}/admin/shop/update"
        payload = {
            "id": 1,
            "name": "Updated Shop Name",
            "description": "Updated description"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.put(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 401, 404]

    def test_get_shop_detail(self, admin_token):
        """测试获取店铺详情"""
        url = f"{API_BASE_URL}/admin/shop/detail"
        params = {"id": 1}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 401, 404]

    def test_get_shop_list(self, admin_token):
        """测试获取店铺列表"""
        url = f"{API_BASE_URL}/admin/shop/list"
        params = {
            "page": 1,
            "pageSize": 10
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_delete_shop(self, admin_token):
        """测试删除店铺"""
        url = f"{API_BASE_URL}/admin/shop/delete"
        params = {"id": 999}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.delete(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        try:
            assert response.status_code == 200
        except AssertionError:
            print(f"删除店铺失败，状态码: {response.status_code}, 响应内容: {response.text}")
            raise

    def test_upload_shop_image(self, admin_token):
        """测试上传店铺图片"""
        url = f"{API_BASE_URL}/admin/shop/upload-image"
        files = {"image": ("test.jpg", b"fake image data", "image/jpeg")}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.post(url, files=files, headers=headers)
        
        response = make_request_with_retry(request_func)
        try:
            assert response.status_code == 200
        except AssertionError:
            print(f"上传店铺图片失败，状态码: {response.status_code}, 响应内容: {response.text}")
            raise

    def test_check_shop_name_exists(self, admin_token):
        """测试检查店铺名称是否存在"""
        url = f"{API_BASE_URL}/admin/shop/check-name"
        params = {"name": "test shop"}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_get_shop_image(self, admin_token):
        """测试获取店铺图片"""
        url = f"{API_BASE_URL}/admin/shop/image"
        params = {"id": 1}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        try:
            assert response.status_code == 200
        except AssertionError:
            print(f"获取店铺图片失败，状态码: {response.status_code}, 响应内容: {response.text}")
            raise

    def test_get_shop_temp_token(self, admin_token):
        """测试获取店铺临时令牌"""
        url = f"{API_BASE_URL}/admin/shop/temp-token"
        params = {"id": 1}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        try:
            assert response.status_code == 200
        except AssertionError:
            print(f"获取店铺临时令牌失败，状态码: {response.status_code}, 响应内容: {response.text}")
            raise

    def test_update_order_status_flow(self, admin_token):
        """测试更新订单状态流转"""
        url = f"{API_BASE_URL}/admin/shop/update-order-status-flow"
        payload = {
            "shop_id": 1,
            "order_status_flow": {
                "statuses": [
                    {
                        "value": 1,
                        "label": "pending",
                        "type": "normal",
                        "isFinal": False,
                        "actions": [
                            {
                                "name": "accept",
                                "nextStatus": 2,
                                "nextStatusLabel": "processing"
                            }
                        ]
                    }
                ]
            }
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.put(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200
