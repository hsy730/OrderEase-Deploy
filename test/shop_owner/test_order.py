import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry, assert_response_status


class TestShopOwnerOrderAPI:
    """商家订单管理接口测试"""

    def test_create_order(self, shop_owner_token, shop_owner_shop_id, shop_owner_user_id, shop_owner_product_id):
        """测试创建订单"""
        if not shop_owner_shop_id or not shop_owner_user_id or not shop_owner_product_id:
            pytest.skip("缺少必要的fixture数据")
            return
            
        url = f"{API_BASE_URL}/shopOwner/order/create"
        payload = {
            "shop_id": shop_owner_shop_id,
            "user_id": shop_owner_user_id,
            "items": [
                {
                    "product_id": shop_owner_product_id,
                    "quantity": 1,
                    "price": 100
                }
            ]
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert_response_status(response, 200)

    def test_get_order_list(self, shop_owner_token, shop_owner_shop_id):
        """测试获取订单列表"""
        if not shop_owner_shop_id:
            pytest.skip("缺少shop_owner_shop_id fixture")
            return
            
        url = f"{API_BASE_URL}/shopOwner/order/list"
        params = {
            "page": 1,
            "pageSize": 10,
            "shop_id": shop_owner_shop_id
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert_response_status(response, 200)

    def test_get_order_detail(self, shop_owner_token, shop_owner_order_id, shop_owner_shop_id):
        """测试获取订单详情"""
        if not shop_owner_order_id or not shop_owner_shop_id:
            pytest.skip("缺少必要的fixture数据")
            return
            
        url = f"{API_BASE_URL}/shopOwner/order/detail"
        params = {
            "id": shop_owner_order_id,
            "shop_id": int(shop_owner_shop_id) if shop_owner_shop_id else 1
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert_response_status(response, 200)

    def test_update_order(self, shop_owner_token, shop_owner_order_id, shop_owner_shop_id, shop_owner_user_id, shop_owner_product_id):
        """测试更新订单信息"""
        if not shop_owner_order_id or not shop_owner_shop_id or not shop_owner_user_id or not shop_owner_product_id:
            pytest.skip("缺少必要的fixture数据")
            return
            
        url = f"{API_BASE_URL}/shopOwner/order/update"
        params = {
            "id": shop_owner_order_id
        }
        payload = {
            "shop_id": int(shop_owner_shop_id) if shop_owner_shop_id else 1,
            "user_id": shop_owner_user_id,
            "items": [
                {
                    "product_id": shop_owner_product_id,
                    "quantity": 1,
                    "price": 100
                }
            ]
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.put(url, params=params, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert_response_status(response, 200)

    def test_toggle_order_status(self, shop_owner_token, shop_owner_order_id, shop_owner_shop_id):
        """测试切换订单状态"""
        if not shop_owner_order_id or not shop_owner_shop_id:
            pytest.skip("缺少必要的fixture数据")
            return
            
        url = f"{API_BASE_URL}/shopOwner/order/toggle-status"
        payload = {
            "id": shop_owner_order_id,
            "shop_id": int(shop_owner_shop_id) if shop_owner_shop_id else 1,
            "next_status": 10
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.put(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert_response_status(response, 200)

    def test_delete_order(self, shop_owner_token, shop_owner_order_id, shop_owner_shop_id):
        """测试删除订单"""
        if not shop_owner_order_id or not shop_owner_shop_id:
            pytest.skip("缺少必要的fixture数据")
            return
            
        url = f"{API_BASE_URL}/shopOwner/order/delete"
        params = {
            "id": shop_owner_order_id,
            "shop_id": int(shop_owner_shop_id) if shop_owner_shop_id else 1
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.delete(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert_response_status(response, 200)