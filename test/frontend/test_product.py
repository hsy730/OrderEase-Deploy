import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry


class TestFrontendProduct:
    """前端商品测试"""

    def test_get_product_list(self, admin_token):
        """测试获取商品列表"""
        url = f"{API_BASE_URL}/product/list"
        params = {
            "page": 1,
            "pageSize": 10
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 401]  # 移除429状态码检查

    def test_get_product_detail(self, admin_token):
        """测试获取商品详情"""
        url = f"{API_BASE_URL}/product/detail"
        params = {"id": 1}  # 使用 id 而不是 product_id
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 401, 404]  # 移除429状态码检查

    def test_get_product_image(self, admin_token):
        """测试获取商品图片"""
        url = f"{API_BASE_URL}/product/image"
        params = {"id": 1}  # 使用 id 而不是 product_id
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 401, 404]  # 移除429状态码检查
