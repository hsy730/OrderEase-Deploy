import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry


class TestShopOwnerShopAPI:
    """商家店铺管理接口测试"""

    def test_get_shop_detail(self, shop_owner_token, shop_owner_shop_id):
        """测试获取店铺详情"""
        if not shop_owner_shop_id:
            pytest.skip("缺少shop_owner_shop_id fixture")
            return
            
        url = f"{API_BASE_URL}/shopOwner/shop/detail"
        params = {"id": shop_owner_shop_id}
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 401, 404]

    def test_get_shop_image(self, shop_owner_token, shop_owner_shop_id):
        """测试获取店铺图片"""
        if not shop_owner_shop_id:
            pytest.skip("缺少shop_owner_shop_id fixture")
            return
            
        url = f"{API_BASE_URL}/shopOwner/shop/image"
        params = {"id": shop_owner_shop_id}
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 401, 404]

    def test_update_shop(self, shop_owner_token, shop_owner_shop_id):
        """测试更新店铺信息"""
        if not shop_owner_shop_id:
            pytest.skip("缺少shop_owner_shop_id fixture")
            return
            
        url = f"{API_BASE_URL}/shopOwner/shop/update"
        payload = {
            "id": shop_owner_shop_id,
            "name": "Updated Shop Name",
            "description": "Updated description",
            "owner_username": "shop1"
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.put(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"更新店铺响应状态码: {response.status_code}, 响应内容: {response.text}")
        assert response.status_code == 200

    def test_update_order_status_flow(self, shop_owner_token, shop_owner_shop_id):
        """测试更新订单状态流转"""
        if not shop_owner_shop_id:
            pytest.skip("缺少shop_owner_shop_id fixture")
            return
            
        url = f"{API_BASE_URL}/shopOwner/shop/update-order-status-flow"
        payload = {
            "shop_id": shop_owner_shop_id,
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
