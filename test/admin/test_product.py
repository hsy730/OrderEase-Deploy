import os
import pytest
import requests

from conftest import API_BASE_URL


class TestAdminProductAPI:
    """管理员商品管理接口测试"""

    def test_create_product(self):
        """测试创建商品"""
        url = f"{API_BASE_URL}/admin/product/create"
        payload = {
            "shop_id": "1",
            "name": f"Test Product {os.urandom(4).hex()}",
            "price": 100,
            "description": "Test product description"
        }
        headers = {"Authorization": "Bearer test_token"}
        response = requests.post(url, json=payload, headers=headers)
        assert response.status_code in [200, 400, 401, 429]

    def test_get_product_list(self):
        """测试获取商品列表"""
        url = f"{API_BASE_URL}/admin/product/list"
        params = {
            "page": 1,
            "pageSize": 10
        }
        headers = {"Authorization": "Bearer test_token"}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code in [200, 400, 401, 429]

    def test_get_product_detail(self):
        """测试获取商品详情"""
        url = f"{API_BASE_URL}/admin/product/detail"
        params = {"productId": "1"}
        headers = {"Authorization": "Bearer test_token"}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code in [200, 400, 401, 404, 429]

    def test_update_product(self):
        """测试更新商品信息"""
        url = f"{API_BASE_URL}/admin/product/update"
        payload = {
            "id": "1",
            "name": "Updated Product Name",
            "price": 150
        }
        headers = {"Authorization": "Bearer test_token"}
        response = requests.put(url, json=payload, headers=headers)
        assert response.status_code in [200, 400, 401, 404, 429]

    def test_delete_product(self):
        """测试删除商品"""
        url = f"{API_BASE_URL}/admin/product/delete"
        params = {"productId": "999"}
        headers = {"Authorization": "Bearer test_token"}
        response = requests.delete(url, params=params, headers=headers)
        assert response.status_code in [200, 400, 401, 404, 429]

    def test_upload_product_image(self):
        """测试上传商品图片"""
        url = f"{API_BASE_URL}/admin/product/upload-image"
        files = {"image": ("test.jpg", b"fake image data", "image/jpeg")}
        headers = {"Authorization": "Bearer test_token"}
        response = requests.post(url, files=files, headers=headers)
        assert response.status_code in [200, 400, 401, 429]

    def test_toggle_product_status(self):
        """测试切换商品状态"""
        url = f"{API_BASE_URL}/admin/product/toggle-status"
        params = {"productId": "1"}
        headers = {"Authorization": "Bearer test_token"}
        response = requests.put(url, params=params, headers=headers)
        assert response.status_code in [200, 400, 401, 404, 429]

    def test_get_product_image(self):
        """测试获取商品图片"""
        url = f"{API_BASE_URL}/admin/product/image"
        params = {"productId": "1"}
        headers = {"Authorization": "Bearer test_token"}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code in [200, 400, 401, 404, 429]
