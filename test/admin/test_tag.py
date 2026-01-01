import os
import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry


class TestAdminTagAPI:
    """管理员标签管理接口测试"""

    def test_create_tag(self, admin_token):
        """测试创建标签"""
        url = f"{API_BASE_URL}/admin/tag/create"
        payload = {
            "name": f"Test Tag {os.urandom(4).hex()}",
            "shop_id": 1
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 401]

    def test_batch_tag_products(self, admin_token):
        """测试批量给商品打标签"""
        url = f"{API_BASE_URL}/admin/tag/batch-tag"
        payload = {
            "product_ids": [1, 2],
            "tag_ids": [1, 2]
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 401]

    def test_get_bound_tags(self, admin_token):
        """测试获取商品已绑定的标签"""
        url = f"{API_BASE_URL}/admin/tag/bound-tags"
        params = {"product_id": 1}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_get_online_products(self, admin_token):
        """测试获取标签关联的已上架商品"""
        url = f"{API_BASE_URL}/admin/tag/online-products"
        params = {"tag_id": 1}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_get_unbound_tags(self, admin_token):
        """测试获取商品未绑定的标签"""
        url = f"{API_BASE_URL}/admin/tag/unbound-tags"
        params = {"product_id": 1}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200
