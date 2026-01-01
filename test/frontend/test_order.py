import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry, assert_response_status


class TestFrontendOrder:
    """前端订单测试"""

    def test_create_order(self, admin_token, test_shop_id, test_user_id, test_product_id):
        """测试创建订单"""
        url = f"{API_BASE_URL}/order/create"
        payload = {
            "shop_id": int(test_shop_id) if test_shop_id else 1,
            "user_id": int(test_user_id) if test_user_id else 1,
            "items": [
                {
                    "product_id": int(test_product_id) if test_product_id else 1,
                    "quantity": 1,
                    "price": 100
                }
            ]
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert_response_status(response, 200)

    def test_get_user_order_list(self, admin_token):
        """测试获取用户订单列表"""
        url = f"{API_BASE_URL}/order/user/list"
        params = {
            "page": 1,
            "pageSize": 10
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert_response_status(response, 200)

    def test_get_order_detail(self, admin_token):
        """测试获取订单详情"""
        url = f"{API_BASE_URL}/order/detail"
        params = {"orderId": 1}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert_response_status(response, 200)

    def test_delete_order(self, admin_token):
        """测试删除订单"""
        url = f"{API_BASE_URL}/order/delete"
        params = {"orderId": 1}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.delete(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert_response_status(response, 200)
