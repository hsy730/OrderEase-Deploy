import os
import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry


class TestBusinessFlow:
    """业务流程测试 - 按照正确的业务顺序执行测试"""

    def test_complete_business_flow(self, admin_token):
        """测试完整的业务流程：创建店铺 → 创建商品 → 创建订单 → 删除订单 → 删除商品 → 删除店铺"""
        
        # 第一步：创建店铺
        shop_id = self._create_shop(admin_token)
        assert shop_id is not None, "创建店铺失败"
        print(f"✓ 成功创建店铺，ID: {shop_id}")
        
        # 第二步：创建商品
        product_id = self._create_product(admin_token, shop_id)
        assert product_id is not None, "创建商品失败"
        print(f"✓ 成功创建商品，ID: {product_id}")
        
        # 第三步：获取用户ID（创建订单需要）
        user_id = self._get_user_id(admin_token)
        assert user_id is not None, "获取用户ID失败"
        print(f"✓ 成功获取用户ID，ID: {user_id}")
        
        # 第四步：创建订单
        order_id = self._create_order(admin_token, shop_id, user_id, product_id)
        assert order_id is not None, "创建订单失败"
        print(f"✓ 成功创建订单，ID: {order_id}")
        
        # 第五步：删除订单
        self._delete_order(admin_token, order_id, shop_id)
        print(f"✓ 成功删除订单，ID: {order_id}")
        
        # 第六步：删除商品
        self._delete_product(admin_token, product_id, shop_id)
        print(f"✓ 成功删除商品，ID: {product_id}")
        
        # 第七步：删除店铺
        self._delete_shop(admin_token, shop_id)
        print(f"✓ 成功删除店铺，ID: {shop_id}")
        
        print("✓ 完整业务流程测试通过")

    def _create_shop(self, admin_token):
        """创建店铺"""
        url = f"{API_BASE_URL}/admin/shop/create"
        payload = {
            "name": f"Business Flow Test Shop {os.urandom(4).hex()}",
            "owner_username": f"shop_owner_{os.urandom(4).hex()}",
            "owner_password": "Admin@123456",
            "contact_phone": "13900139000",
            "contact_email": f"shop_{os.urandom(4).hex()}@test.com",
            "description": "Business flow test shop description",
            "address": "Business flow test address"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"创建店铺请求响应状态码: {response.status_code}, 响应内容: {response.text}")
        if response.status_code == 200:
            data = response.json()
            shop_data = data.get("data", {})
            return shop_data.get("id") or data.get("id") or data.get("shop_id") or data.get("shopId")
        return None

    def _create_product(self, admin_token, shop_id):
        """创建商品"""
        url = f"{API_BASE_URL}/admin/product/create"
        payload = {
            "shop_id": shop_id,
            "name": f"Business Flow Test Product {os.urandom(4).hex()}",
            "price": 100,
            "description": "Business flow test product description"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"创建商品请求响应状态码: {response.status_code}, 响应内容: {response.text}")
        if response.status_code == 200:
            data = response.json()
            return data.get("id")
        return None

    def _get_user_id(self, admin_token):
        """获取用户ID"""
        url = f"{API_BASE_URL}/admin/user/list"
        params = {
            "page": 1,
            "pageSize": 1
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        if response.status_code == 200:
            data = response.json()
            users = data.get("data", data.get("users", []))
            if users and len(users) > 0:
                return users[0].get("id")
        return None

    def _create_order(self, admin_token, shop_id, user_id, product_id):
        """创建订单"""
        url = f"{API_BASE_URL}/admin/order/create"
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
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"创建订单请求响应状态码: {response.status_code}, 响应内容: {response.text}")
        if response.status_code == 200:
            data = response.json()
            return data.get("order_id") or data.get("id")
        return None

    def _delete_order(self, admin_token, order_id, shop_id):
        """删除订单"""
        url = f"{API_BASE_URL}/admin/order/delete"
        params = {
            "id": str(order_id),
            "shop_id": str(shop_id)
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.delete(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"删除订单失败，状态码: {response.status_code}, 响应: {response.text}"

    def _delete_product(self, admin_token, product_id, shop_id):
        """删除商品"""
        url = f"{API_BASE_URL}/admin/product/delete"
        params = {
            "id": product_id,
            "shop_id": shop_id
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.delete(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"删除商品失败，状态码: {response.status_code}, 响应: {response.text}"

    def _delete_shop(self, admin_token, shop_id):
        """删除店铺"""
        url = f"{API_BASE_URL}/admin/shop/delete"
        params = {"shop_id": shop_id}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def request_func():
            return requests.delete(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"删除店铺失败，状态码: {response.status_code}, 响应: {response.text}"