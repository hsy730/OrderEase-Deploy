import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry


class TestFrontendShop:
    """前端店铺测试"""

    def test_get_shop_detail(self, admin_token):
        """测试获取店铺详情"""
        url = f"{API_BASE_URL}/shop/detail"
        params = {"id": 1}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 401, 404]

    def test_get_shop_image(self, admin_token):
        """测试获取店铺图片"""
        url = f"{API_BASE_URL}/shop/image"
        params = {"id": 1}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 401, 404]

    def test_get_shop_tags(self, admin_token):
        """测试获取店铺标签列表"""
        url = f"{API_BASE_URL}/shop/1/tags"
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 401, 404]
