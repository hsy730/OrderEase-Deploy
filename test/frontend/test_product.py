import pytest
import requests

from conftest import API_BASE_URL


class TestFrontendProduct:
    """前端商品测试"""

    def test_get_product_list(self, user_token):
        """测试获取商品列表"""
        url = f"{API_BASE_URL}/product/list"
        params = {
            "page": 1,
            "page_size": 10
        }
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code in [200, 400, 429]

    def test_get_product_detail(self, user_token):
        """测试获取商品详情"""
        url = f"{API_BASE_URL}/product/detail"
        params = {"product_id": "1"}
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code in [200, 400, 404, 429]

    def test_get_product_image(self, user_token):
        """测试获取商品图片"""
        url = f"{API_BASE_URL}/product/image"
        params = {"product_id": "1"}
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code in [200, 400, 404, 429]
