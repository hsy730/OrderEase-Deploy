import os
import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry


class TestShopOwnerBusinessFlow:
    """商家业务流程测试 - 按照正确的业务顺序执行测试"""

    def test_complete_business_flow(self, shop_owner_token, shop_owner_shop_id):
        """测试完整的业务流程：获取店铺 → 创建商品 → 创建订单 → 管理标签 → 删除订单 → 删除商品"""
        
        # 第一步：获取店铺信息（店铺已存在）
        shop_id = shop_owner_shop_id
        assert shop_id is not None, "获取店铺ID失败"
        print(f"✓ 成功获取店铺，ID: {shop_id}")
        
        # 第二步：创建商品
        product_id = self._create_product(shop_owner_token, shop_id)
        assert product_id is not None, "创建商品失败"
        print(f"✓ 成功创建商品，ID: {product_id}")
        
        # 第三步：获取用户ID（创建订单需要）
        user_id = self._get_user_id(shop_owner_token)
        assert user_id is not None, "获取用户ID失败"
        print(f"✓ 成功获取用户ID，ID: {user_id}")
        
        # 第四步：创建订单
        order_id = self._create_order(shop_owner_token, shop_id, user_id, product_id)
        assert order_id is not None, "创建订单失败"
        print(f"✓ 成功创建订单，ID: {order_id}")
        
        # 第五步：创建标签
        tag_id = self._create_tag(shop_owner_token, shop_id)
        assert tag_id is not None, "创建标签失败"
        print(f"✓ 成功创建标签，ID: {tag_id}")
        
        # 第六步：给商品打标签
        self._tag_product(shop_owner_token, product_id, tag_id, shop_id)
        print(f"✓ 成功给商品打标签")
        
        # 第七步：删除订单（按正确顺序先删除订单）
        self._delete_order(shop_owner_token, order_id, shop_id)
        print(f"✓ 成功删除订单，ID: {order_id}")
        
        # 第八步：删除商品
        self._delete_product(shop_owner_token, product_id, shop_id)
        print(f"✓ 成功删除商品，ID: {product_id}")
        
        # 第九步：删除标签
        self._delete_tag(shop_owner_token, tag_id)
        print(f"✓ 成功删除标签，ID: {tag_id}")
        
        print("✓ 完整业务流程测试通过")

    def _create_product(self, shop_owner_token, shop_id):
        """创建商品"""
        url = f"{API_BASE_URL}/shopOwner/product/create"
        payload = {
            "shop_id": shop_id,
            "name": f"Business Flow Test Product {os.urandom(4).hex()}",
            "price": 100,
            "description": "Business flow test product description"
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"创建商品响应状态码: {response.status_code}, 响应内容: {response.text}")
        if response.status_code == 200:
            data = response.json()
            return data.get("id") or data.get("product_id") or data.get("productId")
        return None

    def _get_user_id(self, shop_owner_token):
        """获取用户ID"""
        url = f"{API_BASE_URL}/shopOwner/user/list"
        params = {
            "page": 1,
            "pageSize": 1
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"获取用户ID响应状态码: {response.status_code}, 响应内容: {response.text}")
        if response.status_code == 200:
            data = response.json()
            users = data.get("data", data.get("users", []))
            if users and len(users) > 0:
                return users[0].get("id")
        return None

    def _create_order(self, shop_owner_token, shop_id, user_id, product_id):
        """创建订单"""
        url = f"{API_BASE_URL}/shopOwner/order/create"
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
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"创建订单响应状态码: {response.status_code}, 响应内容: {response.text}")
        if response.status_code == 200:
            data = response.json()
            return data.get("order_id") or data.get("id")
        return None

    def _create_tag(self, shop_owner_token, shop_id):
        """创建标签"""
        url = f"{API_BASE_URL}/shopOwner/tag/create"
        payload = {
            "name": f"Business Flow Test Tag {os.urandom(4).hex()}",
            "shop_id": shop_id
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"创建标签响应状态码: {response.status_code}, 响应内容: {response.text}")
        if response.status_code == 200:
            data = response.json()
            return data.get("id") or data.get("tag_id") or data.get("tagId")
        return None

    def _tag_product(self, shop_owner_token, product_id, tag_id, shop_id):
        """给商品打标签"""
        url = f"{API_BASE_URL}/shopOwner/tag/batch-tag"
        payload = {
            "product_ids": [product_id],
            "tag_id": tag_id,  # API期望的是tag_id（单数），不是tag_ids（复数）
            "shop_id": shop_id
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"商品打标签响应状态码: {response.status_code}, 响应内容: {response.text}")
        assert response.status_code == 200, f"给商品打标签失败，状态码: {response.status_code}, 响应: {response.text}"

    def _delete_order(self, shop_owner_token, order_id, shop_id):
        """删除订单"""
        url = f"{API_BASE_URL}/shopOwner/order/delete"
        params = {
            "id": str(order_id),
            "shop_id": str(shop_id)
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.delete(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"删除订单响应状态码: {response.status_code}, 响应内容: {response.text}")
        assert response.status_code == 200, f"删除订单失败，状态码: {response.status_code}, 响应: {response.text}"

    def _delete_product(self, shop_owner_token, product_id, shop_id):
        """删除商品"""
        url = f"{API_BASE_URL}/shopOwner/product/delete"
        params = {
            "id": product_id,
            "shop_id": shop_id
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.delete(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"删除商品响应状态码: {response.status_code}, 响应内容: {response.text}")
        assert response.status_code == 200, f"删除商品失败，状态码: {response.status_code}, 响应: {response.text}"

    def _delete_tag(self, shop_owner_token, tag_id):
        """删除标签"""
        url = f"{API_BASE_URL}/shopOwner/tag/delete"
        params = {"id": tag_id}
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.delete(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"删除标签响应状态码: {response.status_code}, 响应内容: {response.text}")
        assert response.status_code == 200, f"删除标签失败，状态码: {response.status_code}, 响应: {response.text}"