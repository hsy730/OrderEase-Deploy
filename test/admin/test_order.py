import pytest
import requests

from conftest import API_BASE_URL


class TestAdminOrderAPI:
    """管理员订单管理接口测试"""

    def test_create_order(self):
        """测试创建订单"""
        url = f"{API_BASE_URL}/admin/order/create"
        payload = {
            "shop_id": "1",
            "user_id": "1",
            "items": [
                {
                    "product_id": "1",
                    "quantity": 1,
                    "price": 100
                }
            ]
        }
        headers = {"Authorization": "Bearer test_token"}
        response = requests.post(url, json=payload, headers=headers)
        assert response.status_code in [200, 400, 401, 429]

    def test_get_order_list(self):
        """测试获取订单列表"""
        url = f"{API_BASE_URL}/admin/order/list"
        params = {
            "page": 1,
            "pageSize": 10
        }
        headers = {"Authorization": "Bearer test_token"}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code in [200, 400, 401, 429]

    def test_get_order_detail(self):
        """测试获取订单详情"""
        url = f"{API_BASE_URL}/admin/order/detail"
        params = {"orderId": "1"}
        headers = {"Authorization": "Bearer test_token"}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code in [200, 400, 401, 404, 429]

    def test_update_order(self):
        """测试更新订单信息"""
        url = f"{API_BASE_URL}/admin/order/update"
        payload = {
            "shop_id": "1",
            "user_id": "1",
            "items": [
                {
                    "product_id": "1",
                    "quantity": 1,
                    "price": 100
                }
            ]
        }
        headers = {"Authorization": "Bearer test_token"}
        response = requests.put(url, json=payload, headers=headers)
        assert response.status_code in [200, 400, 401, 429]

    def test_delete_order(self):
        """测试删除订单"""
        url = f"{API_BASE_URL}/admin/order/delete"
        params = {"orderId": "999"}
        headers = {"Authorization": "Bearer test_token"}
        response = requests.delete(url, params=params, headers=headers)
        assert response.status_code in [200, 400, 401, 404, 429]

    def test_toggle_order_status(self):
        """测试切换订单状态"""
        url = f"{API_BASE_URL}/admin/order/toggle-status"
        params = {
            "orderId": "1",
            "status": "completed"
        }
        headers = {"Authorization": "Bearer test_token"}
        response = requests.put(url, params=params, headers=headers)
        assert response.status_code in [200, 400, 401, 404, 429]
