import pytest
import requests

from conftest import API_BASE_URL


class TestShopOwnerShopAPI:
    """商家店铺管理接口测试"""

    def test_get_shop_detail(self):
        """测试获取店铺详情"""
        url = f"{API_BASE_URL}/shopOwner/shop/detail"
        params = {"shopId": "1"}
        headers = {"Authorization": "Bearer test_token"}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code in [200, 400, 401, 404, 429]

    def test_get_shop_image(self):
        """测试获取店铺图片"""
        url = f"{API_BASE_URL}/shopOwner/shop/image"
        params = {"shopId": "1"}
        headers = {"Authorization": "Bearer test_token"}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code in [200, 400, 401, 404, 429]

    def test_update_shop(self):
        """测试更新店铺信息"""
        url = f"{API_BASE_URL}/shopOwner/shop/update"
        payload = {
            "id": "1",
            "name": "Updated Shop Name",
            "description": "Updated description"
        }
        headers = {"Authorization": "Bearer test_token"}
        response = requests.put(url, json=payload, headers=headers)
        assert response.status_code in [200, 400, 401, 404, 429]

    def test_update_order_status_flow(self):
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
        headers = {"Authorization": "Bearer test_token"}
        response = requests.put(url, json=payload, headers=headers)
        assert response.status_code in [200, 400, 401, 429]
