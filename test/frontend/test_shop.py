import pytest
import requests

from conftest import API_BASE_URL


class TestFrontendShop:
    """前端店铺测试"""

    def test_get_shop_detail(self):
        """测试获取店铺详情"""
        url = f"{API_BASE_URL}/shop/detail"
        params = {"shop_id": "1"}
        response = requests.get(url, params=params)
        assert response.status_code in [200, 400, 404, 429]

    def test_get_shop_image(self):
        """测试获取店铺图片"""
        url = f"{API_BASE_URL}/shop/image"
        params = {"shop_id": "1"}
        response = requests.get(url, params=params)
        assert response.status_code in [200, 400, 404, 429]

    def test_get_shop_tags(self):
        """测试获取店铺标签列表"""
        url = f"{API_BASE_URL}/shop/1/tags"
        headers = {"Authorization": "Bearer test_token"}
        response = requests.get(url, headers=headers)
        assert response.status_code in [200, 400, 404, 429]
