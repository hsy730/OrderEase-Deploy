"""
前端商品静态方法
"""

import requests

from conftest import API_BASE_URL, make_request_with_retry


class FrontendProductHelper:
    """前端商品辅助类 - 提供静态方法"""

    @staticmethod
    def get_product_list(token, page=1, page_size=10):
        """测试获取商品列表

        Args:
            token: 认证token
            page: 页码
            page_size: 每页大小

        Returns:
            response: HTTP响应对象
        """
        url = f"{API_BASE_URL}/product/list"
        params = {
            "page": page,
            "pageSize": page_size
        }
        headers = {"Authorization": f"Bearer {token}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        return make_request_with_retry(request_func)

    @staticmethod
    def get_product_detail(product_id, token):
        """测试获取商品详情

        Args:
            product_id: 商品ID
            token: 认证token

        Returns:
            response: HTTP响应对象
        """
        url = f"{API_BASE_URL}/product/detail"
        params = {"id": product_id}
        headers = {"Authorization": f"Bearer {token}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        return make_request_with_retry(request_func)

    @staticmethod
    def get_product_image(product_id, token):
        """测试获取商品图片

        Args:
            product_id: 商品ID
            token: 认证token

        Returns:
            response: HTTP响应对象
        """
        url = f"{API_BASE_URL}/product/image"
        params = {"id": product_id}
        headers = {"Authorization": f"Bearer {token}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        return make_request_with_retry(request_func)
