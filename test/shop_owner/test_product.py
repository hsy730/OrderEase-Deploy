import os
import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry


class TestShopOwnerProductAPI:
    """商家商品管理接口测试"""

    def test_create_product(self, shop_owner_token, shop_owner_shop_id):
        """测试创建商品"""
        if not shop_owner_shop_id:
            pytest.skip("缺少shop_owner_shop_id fixture")
            return
            
        url = f"{API_BASE_URL}/shopOwner/product/create"
        payload = {
            "shop_id": shop_owner_shop_id,
            "name": f"Test Product {os.urandom(4).hex()}",
            "price": 100,
            "description": "Test product description"
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"创建商品响应状态码: {response.status_code}, 响应内容: {response.text}")
        assert response.status_code == 200

    def test_get_product_list(self, shop_owner_token, shop_owner_shop_id):
        """测试获取商品列表"""
        if not shop_owner_shop_id:
            pytest.skip("缺少shop_owner_shop_id fixture")
            return
            
        url = f"{API_BASE_URL}/shopOwner/product/list"
        params = {
            "page": 1,
            "pageSize": 10,
            "shop_id": shop_owner_shop_id
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_get_product_detail(self, shop_owner_token, shop_owner_product_id, shop_owner_shop_id):
        """测试获取商品详情"""
        if not shop_owner_product_id:
            pytest.skip("缺少shop_owner_product_id fixture")
            return
            
        if not shop_owner_shop_id:
            pytest.skip("缺少shop_owner_shop_id fixture")
            return
            
        url = f"{API_BASE_URL}/shopOwner/product/detail"
        params = {
            "id": shop_owner_product_id,
            "shop_id": shop_owner_shop_id
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"获取商品详情响应状态码: {response.status_code}, 响应内容: {response.text}")
        assert response.status_code == 200

    def test_update_product(self, shop_owner_token, shop_owner_product_id, shop_owner_shop_id):
        """测试更新商品信息"""
        if not shop_owner_product_id:
            pytest.skip("缺少shop_owner_product_id fixture")
            return
            
        if not shop_owner_shop_id:
            pytest.skip("缺少shop_owner_shop_id fixture")
            return
            
        url = f"{API_BASE_URL}/shopOwner/product/update"
        params = {
            "id": shop_owner_product_id,
            "shop_id": shop_owner_shop_id
        }
        payload = {
            "name": "Updated Product Name",
            "price": 150
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.put(url, params=params, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"更新商品响应状态码: {response.status_code}, 响应内容: {response.text}")
        assert response.status_code == 200

    def test_upload_product_image(self, shop_owner_token, shop_owner_product_id, shop_owner_shop_id):
        """测试上传商品图片"""
        if not shop_owner_product_id:
            pytest.skip("缺少shop_owner_product_id fixture")
            return
            
        if not shop_owner_shop_id:
            pytest.skip("缺少shop_owner_shop_id fixture")
            return
            
        url = f"{API_BASE_URL}/shopOwner/product/upload-image"
        files = {"image": ("test.jpg", b"fake image data", "image/jpeg")}
        params = {
            "id": shop_owner_product_id,
            "shop_id": shop_owner_shop_id
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.post(url, files=files, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"上传商品图片响应状态码: {response.status_code}, 响应内容: {response.text}")
        assert response.status_code == 200

    def test_toggle_product_status(self, shop_owner_token, shop_owner_product_id, shop_owner_shop_id):
        """测试切换商品状态"""
        if not shop_owner_product_id:
            pytest.skip("缺少shop_owner_product_id fixture")
            return
            
        url = f"{API_BASE_URL}/shopOwner/product/toggle-status"
        payload = {
            "id": shop_owner_product_id,
            "shop_id": shop_owner_shop_id,
            "status": "online"
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.put(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"切换商品状态响应状态码: {response.status_code}, 响应内容: {response.text}")
        assert response.status_code == 200

    def test_get_product_image(self, shop_owner_token, shop_owner_product_id):
        """测试获取商品图片"""
        if not shop_owner_product_id:
            pytest.skip("缺少shop_owner_product_id fixture")
            return
            
        url = f"{API_BASE_URL}/shopOwner/product/image"
        params = {"id": shop_owner_product_id}
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"获取商品图片响应状态码: {response.status_code}, 响应内容: {response.text}")
        assert response.status_code == 200


    def test_delete_product(self, shop_owner_token, shop_owner_shop_id):
        """测试删除商品"""
        # First create a new product specifically for deletion testing
        create_url = f"{API_BASE_URL}/shopOwner/product/create"
        create_payload = {
            "shop_id": shop_owner_shop_id,
            "name": f"Product for Deletion Test {os.urandom(4).hex()}",
            "price": 100,
            "description": "Product created specifically for deletion test"
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def create_request_func():
            return requests.post(create_url, json=create_payload, headers=headers)
        
        create_response = make_request_with_retry(create_request_func)
        print(f"创建测试商品响应状态码: {create_response.status_code}, 响应内容: {create_response.text}")
        
        if create_response.status_code != 200:
            pytest.skip("Failed to create product for deletion test")
            return
            
        # Extract the product ID from the creation response
        product_data = create_response.json()
        test_product_id = product_data.get("id") or product_data.get("product_id")
        
        if not test_product_id:
            pytest.skip("Could not extract product ID from creation response")
            return
            
        # Now delete the newly created product
        url = f"{API_BASE_URL}/shopOwner/product/delete"
        params = {
            "id": test_product_id,
            "shop_id": shop_owner_shop_id
        }
        
        def delete_request_func():
            return requests.delete(url, params=params, headers=headers)
        
        response = make_request_with_retry(delete_request_func)
        print(f"删除商品响应状态码: {response.status_code}, 响应内容: {response.text}")
        assert response.status_code == 200
