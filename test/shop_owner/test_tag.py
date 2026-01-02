import os
import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry


class TestShopOwnerTagAPI:
    """商家标签管理接口测试"""

    def test_create_tag(self, shop_owner_token, shop_owner_shop_id):
        """测试创建标签"""
        url = f"{API_BASE_URL}/shopOwner/tag/create"
        payload = {
            "name": f"Test Tag {os.urandom(4).hex()}",
            "shop_id": shop_owner_shop_id
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_batch_tag_products(self, shop_owner_token, shop_owner_product_id, shop_owner_tag_id):
        """测试批量给商品打标签"""
            
        url = f"{API_BASE_URL}/shopOwner/tag/batch-tag"
        payload = {
            "product_ids": [shop_owner_product_id],
            "tag_ids": [shop_owner_tag_id]
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_get_bound_tags(self, shop_owner_token, shop_owner_product_id, shop_owner_shop_id):
        """测试获取商品已绑定的标签"""
        url = f"{API_BASE_URL}/shopOwner/tag/bound-tags"
        params = {
            "product_id": shop_owner_product_id,
            "shop_id": shop_owner_shop_id
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"获取商品已绑定标签响应状态码: {response.status_code}, 响应内容: {response.text}")
        assert response.status_code == 200

    def test_get_online_products(self, shop_owner_token, shop_owner_tag_id):
        """测试获取标签关联的已上架商品"""
        url = f"{API_BASE_URL}/shopOwner/tag/online-products"
        params = {"tag_id": shop_owner_tag_id}
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_get_unbound_tags(self, shop_owner_token, shop_owner_product_id, shop_owner_shop_id):
        """测试获取商品未绑定的标签"""            
        url = f"{API_BASE_URL}/shopOwner/tag/unbound-tags"
        params = {"product_id": shop_owner_product_id, "shop_id": shop_owner_shop_id}
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"获取商品未绑定标签响应状态码: {response.status_code}, 响应内容: {response.text}")
        assert response.status_code == 200
