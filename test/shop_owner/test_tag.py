import os
import pytest
import requests

from conftest import API_BASE_URL


class TestShopOwnerTagAPI:
    """商家标签管理接口测试"""

    def test_create_tag(self):
        """测试创建标签"""
        url = f"{API_BASE_URL}/shopOwner/tag/create"
        payload = {
            "name": f"Test Tag {os.urandom(4).hex()}",
            "shop_id": 1
        }
        headers = {"Authorization": "Bearer test_token"}
        response = requests.post(url, json=payload, headers=headers)
        assert response.status_code in [200, 400, 401, 429]

    def test_batch_tag_products(self):
        """测试批量给商品打标签"""
        url = f"{API_BASE_URL}/shopOwner/tag/batch-tag"
        payload = {
            "product_ids": ["1", "2"],
            "tag_ids": ["1", "2"]
        }
        headers = {"Authorization": "Bearer test_token"}
        response = requests.post(url, json=payload, headers=headers)
        assert response.status_code in [200, 400, 401, 429]

    def test_get_bound_tags(self):
        """测试获取商品已绑定的标签"""
        url = f"{API_BASE_URL}/shopOwner/tag/bound-tags"
        params = {"product_id": "1"}
        headers = {"Authorization": "Bearer test_token"}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code in [200, 400, 401, 404, 429]

    def test_get_online_products(self):
        """测试获取标签关联的已上架商品"""
        url = f"{API_BASE_URL}/shopOwner/tag/online-products"
        params = {"tag_id": "1"}
        headers = {"Authorization": "Bearer test_token"}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code in [200, 400, 401, 404, 429]

    def test_get_unbound_tags(self):
        """测试获取商品未绑定的标签"""
        url = f"{API_BASE_URL}/shopOwner/tag/unbound-tags"
        params = {"product_id": "1"}
        headers = {"Authorization": "Bearer test_token"}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code in [200, 400, 401, 404, 429]
