import os
import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry


class TestShopOwnerProductAPI:
    """商家商品管理接口测试"""

    def test_create_product(self, shop_owner_token):
        """测试创建商品"""
        url = f"{API_BASE_URL}/shopOwner/product/create"
        payload = {
            "shop_id": 1,
            "name": f"Test Product {os.urandom(4).hex()}",
            "price": 100,
            "description": "Test product description"
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 401]

    def test_get_product_list(self, shop_owner_token):
        """测试获取商品列表"""
        url = f"{API_BASE_URL}/shopOwner/product/list"
        params = {
            "page": 1,
            "pageSize": 10
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_get_product_detail(self, shop_owner_token):
        """测试获取商品详情"""
        url = f"{API_BASE_URL}/shopOwner/product/detail"
        params = {"id": 1}
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_update_product(self, shop_owner_token):
        """测试更新商品信息"""
        url = f"{API_BASE_URL}/shopOwner/product/update"
        payload = {
            "id": 1,
            "name": "Updated Product Name",
            "price": 150
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.put(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_delete_product(self, shop_owner_token):
        """测试删除商品"""
        url = f"{API_BASE_URL}/shopOwner/product/delete"
        params = {"id": 999}
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.delete(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_upload_product_image(self, shop_owner_token):
        """测试上传商品图片"""
        url = f"{API_BASE_URL}/shopOwner/product/upload-image"
        files = {"image": ("test.jpg", b"fake image data", "image/jpeg")}
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.post(url, files=files, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_toggle_product_status(self, shop_owner_token):
        """测试切换商品状态"""
        url = f"{API_BASE_URL}/shopOwner/product/toggle-status"
        payload = {
            "id": 1,
            "status": "online"
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.put(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_get_product_image(self, shop_owner_token):
        """测试获取商品图片"""
        url = f"{API_BASE_URL}/shopOwner/product/image"
        params = {"id": 1}
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200
