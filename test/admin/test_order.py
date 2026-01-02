import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry, assert_response_status


@pytest.mark.skip(reason="业务流程测试已整合到 test_business_flow.py 中")
class TestAdminOrderAPI:
    """管理员订单管理接口测试"""

    def test_create_order(self, admin_token, test_shop_id, test_user_id, test_product_id):
        """测试创建订单"""
        url = f"{API_BASE_URL}/admin/order/create"
        payload = {
            "shop_id": int(test_shop_id) if test_shop_id else 7,
            "user_id": str(test_user_id) if test_user_id else "2006633621737181184",
            "items": [
                {
                    "product_id": str(test_product_id) if test_product_id else "2006734306319273984",
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

    def test_get_order_list(self, admin_token, test_shop_id):
        """测试获取订单列表"""
        url = f"{API_BASE_URL}/admin/order/list"
        params = {
            "page": 1,
            "pageSize": 10,
            "shop_id": str(test_shop_id) if test_shop_id else "7"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert_response_status(response, 200)

    def test_get_order_detail(self, admin_token, test_order_id, test_shop_id):
        """测试获取订单详情"""
        url = f"{API_BASE_URL}/admin/order/detail"
        params = {
            "id": str(test_order_id) if test_order_id else "2006670542223970304",
            "shop_id": str(test_shop_id) if test_shop_id else "7"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert_response_status(response, 200)

    def test_update_order(self, admin_token, test_order_id, test_shop_id, test_user_id, test_product_id):
        """测试更新订单信息"""
        url = f"{API_BASE_URL}/admin/order/update"
        params = {
            "id": str(test_order_id) if test_order_id else "2006670542223970304",
            "shop_id": str(test_shop_id) if test_shop_id else "7"
        }
        payload = {
            "id": str(test_order_id) if test_order_id else "2006670542223970304",
            "user_id": str(test_user_id) if test_user_id else "2006633621737181184",
            "shop_id": int(test_shop_id) if test_shop_id else 7,
            "total_price": "100.00",
            "status": 1,
            "remark": "44",
            "items": [
                {
                    "product_id": str(test_product_id) if test_product_id else "2006734306319273984",
                    "quantity": 1,
                    "price": 100,
                    "options": []
                }
            ]
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.put(url, params=params, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert_response_status(response, 200)



    def test_toggle_order_status(self, admin_token, test_order_id, test_shop_id):
        """测试切换订单状态"""
        url = f"{API_BASE_URL}/admin/order/toggle-status"
        payload = {
            "id": str(test_order_id) if test_order_id else "2006670542223970304",
            "shop_id": int(test_shop_id) if test_shop_id else 7,
            "next_status": 2
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.put(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert_response_status(response, 200)

    def test_delete_order(self, admin_token, test_order_id, test_shop_id):
        """测试删除订单"""
        url = f"{API_BASE_URL}/admin/order/delete"
        params = {
            "id": str(test_order_id) if test_order_id else "2006670542223970304",
            "shop_id": str(test_shop_id) if test_shop_id else "7"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.delete(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert_response_status(response, 200)
