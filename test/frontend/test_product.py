import pytest
import requests

from conftest import API_BASE_URL


class TestFrontendProduct:
    """前端商品测试"""

    def test_get_product_list(self):
        """测试获取商品列表"""
        url = f"{API_BASE_URL}/product/list"
        params = {
            "page": 1,
            "pageSize": 10
        }
        response = requests.get(url, params=params)
        assert response.status_code in [200, 400, 429]

    def test_get_product_detail(self):
        """测试获取商品详情"""
        url = f"{API_BASE_URL}/product/detail"
        params = {"productId": "1"}
        response = requests.get(url, params=params)
        assert response.status_code in [200, 400, 404, 429]

    def test_get_product_image(self):
        """测试获取商品图片"""
        url = f"{API_BASE_URL}/product/image"
        params = {"productId": "1"}
        response = requests.get(url, params=params)
        assert response.status_code in [200, 400, 404, 429]
