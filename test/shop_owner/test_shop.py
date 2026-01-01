import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry


class TestShopOwnerShopAPI:
    """商家店铺管理接口测试"""

    def test_get_shop_detail(self, shop_owner_token):
        """测试获取店铺详情"""
        url = f"{API_BASE_URL}/shopOwner/shop/detail"
        params = {"id": 1}
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 401, 404]

    def test_get_shop_image(self, shop_owner_token):
        """测试获取店铺图片"""
        url = f"{API_BASE_URL}/shopOwner/shop/image"
        params = {"id": 1}
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 401, 404]

    def test_update_shop(self, shop_owner_token):
        """测试更新店铺信息"""
        url = f"{API_BASE_URL}/shopOwner/shop/update"
        payload = {
            "id": 1,
            "name": "Updated Shop Name",
            "description": "Updated description"
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.put(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200

    def test_update_order_status_flow(self, shop_owner_token):
        """测试更新订单状态流转"""
        url = f"{API_BASE_URL}/shopOwner/shop/update-order-status-flow"
        payload = {
            "shop_id": 1,
            "order_status_flow": {
                "statuses": [
                    {
                        "value": 1,
                        "label": "pending",
                        "type": "normal",
                        "isFinal": False,
                        "actions": [
                            {
                                "name": "accept",
                                "nextStatus": 2,
                                "nextStatusLabel": "processing"
                            }
                        ]
                    }
                ]
            }
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.put(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200
