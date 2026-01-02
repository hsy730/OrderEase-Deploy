import os
import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry


@pytest.mark.skip(reason="业务流程测试已整合到 test_business_flow.py 中")
class TestAdminProductAPI:
    """管理员商品管理接口测试"""

    def test_create_product(self, admin_token, test_shop_id):
        """测试创建商品"""
        url = f"{API_BASE_URL}/admin/product/create"
        payload = {
            "shop_id": test_shop_id if test_shop_id else 1,
            "name": f"Test Product {os.urandom(4).hex()}",
            "price": 100,
            "description": "Test product description"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_get_product_list(self, admin_token, test_shop_id):
        """测试获取商品列表"""
        url = f"{API_BASE_URL}/admin/product/list"
        params = {
            "shop_id": test_shop_id if test_shop_id else 1,
            "page": 1,
            "pageSize": 10
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
            
        def request_func():
            return requests.get(url, params=params, headers=headers)
            
        response = make_request_with_retry(request_func)
        try:
            assert response.status_code == 200
        except AssertionError:
            print(f"获取商品列表失败，状态码: {response.status_code}, 响应内容: {response.text}")
            raise
    
    def test_get_product_list_with_shop(self, admin_token, test_shop_id):
        """测试获取指定店铺的商品列表"""
        url = f"{API_BASE_URL}/admin/product/list"
        params = {
            "page": 1,
            "pageSize": 10,
            "shop_id": test_shop_id if test_shop_id else 1
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
            
        def request_func():
            return requests.get(url, params=params, headers=headers)
            
        response = make_request_with_retry(request_func)
        try:
            assert response.status_code == 200
        except AssertionError:
            print(f"获取指定店铺商品列表失败，状态码: {response.status_code}, 响应内容: {response.text}")
            raise

    def test_get_product_detail(self, admin_token, test_product_id, test_shop_id):
        """测试获取商品详情"""
        url = f"{API_BASE_URL}/admin/product/detail"
        params = {"id": test_product_id if test_product_id else 1, "shop_id": test_shop_id if test_shop_id else 1}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        try:
            assert response.status_code == 200
        except AssertionError:
            print(f"获取商品详情失败，状态码: {response.status_code}, 响应内容: {response.text}")
            raise

    def test_update_product(self, admin_token, test_product_id, test_shop_id):
        """测试更新商品信息"""
        url = f"{API_BASE_URL}/admin/product/update"
        params = {
            "id": test_product_id if test_product_id else 1,
            "shop_id": test_shop_id if test_shop_id else 1
        }
        payload = {
            "name": "Updated Product Name",
            "price": 150
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
            
        def request_func():
            return requests.put(url, params=params, json=payload, headers=headers)
            
        response = make_request_with_retry(request_func)
        try:
            assert response.status_code == 200
        except AssertionError:
            print(f"更新商品信息失败，状态码: {response.status_code}, 响应内容: {response.text}")
            raise

    def test_upload_product_image(self, admin_token, test_product_id, test_shop_id):
        """测试上传商品图片"""
        url = f"{API_BASE_URL}/admin/product/upload-image"
        params = {
            "id": test_product_id if test_product_id else 1,
            "shop_id": test_shop_id if test_shop_id else 1
        }
        files = {"image": ("test.jpg", b"fake image data", "image/jpeg")}
        headers = {"Authorization": f"Bearer {admin_token}"}
            
        def request_func():
            return requests.post(url, params=params, files=files, headers=headers)
            
        response = make_request_with_retry(request_func)
        try:
            assert response.status_code == 200
            # 解析响应，获取图片URL
            response_data = response.json()
            print(f"上传商品图片成功，响应内容: {response_data}")
            if 'url' in response_data:
                # 将图片URL保存到类属性中，供后续测试使用
                self.__class__.uploaded_image_url = response_data['url']
                print(f"上传商品图片成功，图片URL: {self.__class__.uploaded_image_url}")
            else:
                print("上传成功但未返回图片URL")
        except AssertionError:
            print(f"上传商品图片失败，请求参数: {params}, 状态码: {response.status_code}, 响应内容: {response.text}")
            raise
        except Exception as e:
            print(f"解析上传图片响应失败: {str(e)}")
            raise

    def test_get_product_image(self, admin_token, test_product_id, test_shop_id):
        """测试获取商品图片"""
        url = f"{API_BASE_URL}/admin/product/image"
        # 尝试使用上传图片测试中保存的类属性URL，如果不存在则使用默认路径
        image_path = getattr(self.__class__, 'uploaded_image_url', None) if hasattr(self.__class__, 'uploaded_image_url') else f"product_{test_product_id if test_product_id else 1}_1234567890.jpg"
        params = {"path": image_path, "shop_id": test_shop_id if test_shop_id else 1}
        headers = {"Authorization": f"Bearer {admin_token}"}
            
        def request_func():
            return requests.get(url, params=params, headers=headers)
            
        response = make_request_with_retry(request_func)
        try:
            assert response.status_code == 200
        except AssertionError:
            print(f"获取商品图片失败，请求参数: {params}, 状态码: {response.status_code}, 响应内容: {response.text}")
            raise        

    def test_toggle_product_status(self, admin_token, test_product_id, test_shop_id):
        """测试切换商品状态"""
        url = f"{API_BASE_URL}/admin/product/toggle-status"
        payload = {
            "id": str(test_product_id) if test_product_id else "1",
            "status": "online",
            "shop_id": test_shop_id if test_shop_id else 1
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

    def test_delete_product(self, admin_token, test_product_id, test_shop_id):
        """测试删除商品"""
        url = f"{API_BASE_URL}/admin/product/delete"
        params = {
            "id": test_product_id if test_product_id else 999,
            "shop_id": test_shop_id if test_shop_id else 1
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
            
        def request_func():
            return requests.delete(url, params=params, headers=headers) 
            
        response = make_request_with_retry(request_func)
        
        try:
            assert response.status_code == 200
            print(f"删除商品成功，请求参数: {params}, 状态码: {response.status_code}, 响应内容: {response.text}")
        except AssertionError:
            print(f"删除商品失败，状态码: {response.status_code}, 响应内容: {response.text}")
            raise