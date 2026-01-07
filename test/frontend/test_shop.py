"""
前端店铺静态方法
"""

import requests

from conftest import API_BASE_URL, make_request_with_retry


class FrontendShopHelper:
    """前端店铺辅助类 - 提供静态方法"""

    @staticmethod
    def get_shop_detail(shop_id, token):
        """测试获取店铺详情

        Args:
            shop_id: 店铺ID
            token: 认证token

        Returns:
            response: HTTP响应对象
        """
        url = f"{API_BASE_URL}/shop/detail"
        params = {"shop_id": shop_id}
        headers = {"Authorization": f"Bearer {token}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        return make_request_with_retry(request_func)

    @staticmethod
    def get_shop_image(path, token):
        """测试获取店铺图片

        Args:
            path: 图片文件路径
            token: 认证token

        Returns:
            response: HTTP响应对象
        """
        url = f"{API_BASE_URL}/shop/image"
        params = {"path": path}
        headers = {"Authorization": f"Bearer {token}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        return make_request_with_retry(request_func)

    @staticmethod
    def get_shop_tags(shop_id, token):
        """测试获取店铺标签列表

        Args:
            shop_id: 店铺ID
            token: 认证token

        Returns:
            response: HTTP响应对象
        """
        url = f"{API_BASE_URL}/shop/{shop_id}/tags"
        headers = {"Authorization": f"Bearer {token}"}

        def request_func():
            return requests.get(url, headers=headers)

        return make_request_with_retry(request_func)
