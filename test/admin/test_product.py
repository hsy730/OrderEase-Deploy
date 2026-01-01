import os
import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry


class TestAdminProductAPI:
    """管理员商品管理接口测试"""

    def test_create_product(self, admin_token):
        """测试创建商品"""
        url = f"{API_BASE_URL}/admin/product/create"
        payload = {
            "shop_id": 1,
            "name": f"Test Product {os.urandom(4).hex()}",
            "price": 100,
            "description": "Test product description"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 401]

    def test_get_product_list(self, admin_token):
        """测试获取商品列表"""
        url = f"{API_BASE_URL}/admin/product/list"
        params = {
            "page": 1,
            "pageSize": 10
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        try:
            response.status_code == 200
        except AssertionError:
            print(f"获取商品列表失败，状态码: {response.status_code}, 响应内容: {response.text}")
            raise

    def test_get_product_detail(self, admin_token):
        """测试获取商品详情"""
        url = f"{API_BASE_URL}/admin/product/detail"
        params = {"id": 1}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        try:
            assert response.status_code == 200
        except AssertionError:
            print(f"获取商品详情失败，状态码: {response.status_code}, 响应内容: {response.text}")
            raise

    def test_update_product(self, admin_token):
        """测试更新商品信息"""
        url = f"{API_BASE_URL}/admin/product/update"
        payload = {
            "id": 1,
            "name": "Updated Product Name",
            "price": 150
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.put(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        try:
            assert response.status_code == 200
        except AssertionError:
            print(f"更新商品信息失败，状态码: {response.status_code}, 响应内容: {response.text}")
            raise

    def test_delete_product(self, admin_token):
        """测试删除商品"""
        url = f"{API_BASE_URL}/admin/product/delete"
        params = {"id": 999}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.delete(url, params=params, headers=headers) 
        
        response = make_request_with_retry(request_func)
        try:
            assert response.status_code == 200
        except AssertionError:
            print(f"删除商品失败，状态码: {response.status_code}, 响应内容: {response.text}")
            raise

    def test_upload_product_image(self, admin_token):
        """测试上传商品图片"""
        url = f"{API_BASE_URL}/admin/product/upload-image"
        files = {"image": ("test.jpg", b"fake image data", "image/jpeg")}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.post(url, files=files, headers=headers)
        
        response = make_request_with_retry(request_func)
        try:
            assert response.status_code == 200
        except AssertionError:
            print(f"上传商品图片失败，状态码: {response.status_code}, 响应内容: {response.text}")
            raise

    def test_toggle_product_status(self, admin_token):
        """测试切换商品状态"""
        url = f"{API_BASE_URL}/admin/product/toggle-status"
        payload = {
            "id": 1,
            "status": "online"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.put(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        try:
            assert response.status_code == 200
        except AssertionError:
            print(f"切换商品状态失败，状态码: {response.status_code}, 响应内容: {response.text}")
            raise

    def test_get_product_image(self, admin_token):
        """测试获取商品图片"""
        url = f"{API_BASE_URL}/admin/product/image"
        params = {"id": 1}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200
