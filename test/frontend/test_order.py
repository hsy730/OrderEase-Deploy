"""
前端订单静态方法
"""

import requests

from conftest import API_BASE_URL, make_request_with_retry


class FrontendOrderHelper:
    """前端订单辅助类 - 提供静态方法"""

    @staticmethod
    def create_order(shop_id, user_id, product_id, token):
        """测试创建订单

        Args:
            shop_id: 店铺ID
            user_id: 用户ID
            product_id: 商品ID
            token: 认证token

        Returns:
            order_id: 订单ID，失败返回None
        """
        url = f"{API_BASE_URL}/order/create"
        payload = {
            "shop_id": int(shop_id),
            "user_id": str(user_id),
            "items": [
                {
                    "product_id": str(product_id),
                    "quantity": 1,
                    "price": 100
                }
            ]
        }
        print(f"创建订单请求参数: {payload}")
        headers = {"Authorization": f"Bearer {token}"}

        def request_func():
            return requests.post(url, json=payload, headers=headers)

        response = make_request_with_retry(request_func)
        print(f"创建订单响应码: {response.status_code}，响应内容: {response.text}")
        if response.status_code == 200:
            data = response.json()
            return data.get("order_id") or data.get("id") or data.get("orderId")
        return None

    @staticmethod
    def get_user_order_list(token, page=1, page_size=10):
        """测试获取用户订单列表

        Args:
            token: 认证token
            page: 页码
            page_size: 每页大小

        Returns:
            response: HTTP响应对象
        """
        url = f"{API_BASE_URL}/order/user/list"
        params = {
            "page": page,
            "pageSize": page_size
        }
        headers = {"Authorization": f"Bearer {token}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        return make_request_with_retry(request_func)

    @staticmethod
    def get_order_detail(order_id, token):
        """测试获取订单详情

        Args:
            order_id: 订单ID
            token: 认证token

        Returns:
            response: HTTP响应对象
        """
        url = f"{API_BASE_URL}/order/detail"
        params = {"id": order_id}
        headers = {"Authorization": f"Bearer {token}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        return make_request_with_retry(request_func)

    @staticmethod
    def delete_order(order_id, token):
        """测试删除订单

        Args:
            order_id: 订单ID
            token: 认证token

        Returns:
            response: HTTP响应对象
        """
        url = f"{API_BASE_URL}/order/delete"
        params = {"id": order_id}
        headers = {"Authorization": f"Bearer {token}"}

        def request_func():
            return requests.delete(url, params=params, headers=headers)

        return make_request_with_retry(request_func)
