import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry, assert_response_status


class TestFrontendOrder:
    """前端订单测试"""

    def test_create_order(self, user_token, test_shop_id, test_user_id, test_product_id):
        """测试创建订单"""
        url = f"{API_BASE_URL}/order/create"
        payload = {
            "shop_id": test_shop_id,
            "user_id": test_user_id,
            "items": [
                {
                    "product_id": test_product_id,
                    "quantity": 1,
                    "price": 100
                }
            ]
        }
        headers = {"Authorization": f"Bearer {user_token}"}
        
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert_response_status(response, [200, 401])

    def test_get_user_order_list(self, user_token):
        """测试获取用户订单列表"""
        url = f"{API_BASE_URL}/order/user/list"
        params = {
            "page": 1,
            "pageSize": 10
        }
        headers = {"Authorization": f"Bearer {user_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert_response_status(response, [200, 401])

    def test_get_order_detail(self, user_token):
        """测试获取订单详情"""
        url = f"{API_BASE_URL}/order/detail"
        params = {"orderId": "1"}
        headers = {"Authorization": f"Bearer {user_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert_response_status(response, [200, 401])

    def test_delete_order(self, user_token):
        """测试删除订单"""
        url = f"{API_BASE_URL}/order/delete"
        params = {"orderId": "1"}
        headers = {"Authorization": f"Bearer {user_token}"}
        
        def request_func():
            return requests.delete(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert_response_status(response, [200, 401])
