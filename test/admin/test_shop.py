# 该文件已被重构为 shop_actions.py，仅保留用于参考，不再作为测试执行
__test__ = False

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
            "address": "Test address",
            "owner_username": f"shop_owner_{os.urandom(4).hex()}",
            "owner_password": "TestPassword123"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"创建店铺响应码: {response.status_code}，响应内容: {response.text}")
        assert response.status_code == 200

    def test_update_shop(self, admin_token, test_shop_id):
        """测试更新店铺信息"""
        url = f"{API_BASE_URL}/admin/shop/update"
        params = {
            "id": test_shop_id if test_shop_id else 1
        }
        payload = {
            "name": "Updated Shop Name",
            "description": "Updated description"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.put(url, params=params, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_get_shop_detail(self, admin_token, test_shop_id):
        """测试获取店铺详情"""
        url = f"{API_BASE_URL}/admin/shop/detail"
        params = {"shop_id": test_shop_id if test_shop_id else 1}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

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

    def test_upload_shop_image(self, admin_token, test_shop_id):
        """测试上传店铺图片"""
        url = f"{API_BASE_URL}/admin/shop/upload-image"
        params = {
            "id": test_shop_id if test_shop_id else 1
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
            print(f"上传店铺图片成功，响应内容: {response_data}")
            if 'url' in response_data:
                # 将图片URL保存到类属性中，供后续测试使用
                self.__class__.uploaded_shop_image_url = response_data['url']
                print(f"上传店铺图片成功，图片URL: {self.__class__.uploaded_shop_image_url}")
            else:
                print("上传成功但未返回图片URL")
        except AssertionError:
            print(f"上传店铺图片失败，请求参数: {params}, 状态码: {response.status_code}, 响应内容: {response.text}")
            raise
        except Exception as e:
            print(f"解析上传图片响应失败: {str(e)}")
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

    def test_get_shop_image(self, admin_token, test_shop_id):
        """测试获取店铺图片"""
        url = f"{API_BASE_URL}/admin/shop/image"
        # 尝试使用上传图片测试中保存的类属性URL，如果不存在则使用默认路径
        image_path = getattr(self.__class__, 'uploaded_shop_image_url', None) if hasattr(self.__class__, 'uploaded_shop_image_url') else f"shop_{test_shop_id if test_shop_id else 1}_1234567890.jpg"
        params = {"path": image_path}
        headers = {"Authorization": f"Bearer {admin_token}"}
            
        def request_func():
            return requests.get(url, params=params, headers=headers)
            
        response = make_request_with_retry(request_func)
        try:
            assert response.status_code == 200
        except AssertionError:
            print(f"获取店铺图片失败，请求参数: {params}, 状态码: {response.status_code}, 响应内容: {response.text}")
            raise

    def test_get_shop_temp_token(self, admin_token, test_shop_id):
        """测试获取店铺临时令牌"""
        url = f"{API_BASE_URL}/admin/shop/temp-token"
        params = {"shop_id": test_shop_id if test_shop_id else 1}
        headers = {"Authorization": f"Bearer {admin_token}"}
            
        def request_func():
            return requests.get(url, params=params, headers=headers)
            
        response = make_request_with_retry(request_func)
        try:
            assert response.status_code == 200
        except AssertionError:
            print(f"获取店铺临时令牌失败，状态码: {response.status_code}, 响应内容: {response.text}")
            raise

    def test_update_order_status_flow(self, admin_token, test_shop_id):
        """测试更新订单状态流转"""
        url = f"{API_BASE_URL}/admin/shop/update-order-status-flow"
        payload = {
            "shop_id": test_shop_id if test_shop_id else 1,
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


    def test_delete_shop(self, admin_token, test_shop_id):
        """测试删除店铺"""
        shop_id = test_shop_id if test_shop_id else 999
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 先删除该店铺下的所有商品
        product_list_url = f"{API_BASE_URL}/admin/product/list"
        product_list_params = {
            "shop_id": shop_id,
            "page": 1,
            "pageSize": 100
        }

        def get_products_func():
            return requests.get(product_list_url, params=product_list_params, headers=headers)

        product_list_response = make_request_with_retry(get_products_func)

        if product_list_response.status_code == 200:
            try:
                products_data = product_list_response.json()
                products = products_data.get('list', products_data.get('data', []))

                # 删除所有商品
                for product in products:
                    product_id = product.get('id')
                    if product_id:
                        delete_product_url = f"{API_BASE_URL}/admin/product/delete"
                        delete_product_params = {
                            "id": product_id,
                            "shop_id": shop_id
                        }

                        def delete_product_func():
                            return requests.delete(delete_product_url, params=delete_product_params, headers=headers)

                        delete_product_response = make_request_with_retry(delete_product_func)
                        print(f"删除商品 {product_id}, 状态码: {delete_product_response.status_code}")

                print(f"已删除店铺 {shop_id} 下的所有商品")
            except Exception as e:
                print(f"获取或删除商品列表失败: {str(e)}")
        else:
            print(f"获取商品列表失败，状态码: {product_list_response.status_code}")

        # 删除店铺
        url = f"{API_BASE_URL}/admin/shop/delete"
        params = {"shop_id": shop_id}

        def request_func():
            return requests.delete(url, params=params, headers=headers)

        response = make_request_with_retry(request_func)
        try:
            assert response.status_code == 200
        except AssertionError:
            print(f"删除店铺失败，请求参数: {params}, 状态码: {response.status_code}, 响应内容: {response.text}")
            raise

