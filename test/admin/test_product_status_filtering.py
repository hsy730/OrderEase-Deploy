"""
商品状态过滤测试 - 验证客户端和管理端商品查询差异

验证以下行为：
1. 客户端查询只返回 online 状态的商品
2. 管理端查询返回所有状态的商品（pending、offline、online）
"""

import os
import pytest
import requests
import sys
from pathlib import Path

# 添加父目录到 sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import API_BASE_URL, make_request_with_retry
import admin.shop_actions as admin_shop_actions
import admin.product_actions as admin_product_actions


class TestProductStatusFiltering:
    """商品状态过滤测试类 - 验证客户端和管理端的查询差异"""

    @pytest.fixture(scope="class", autouse=True)
    def setup_test_data(self, request, admin_token):
        """设置测试数据 - 创建包含不同状态商品的店铺"""
        print("\n===== 设置商品状态过滤测试数据 =====")

        # 使用 request.cls 设置类属性，确保测试方法可以访问
        cls = request.cls
        cls.admin_token = admin_token
        cls.test_data = {}

        # 创建测试店铺
        unique_suffix = os.urandom(4).hex()
        shop_id = admin_shop_actions.create_shop(
            admin_token,
            name=f"Status Filter Test Shop {unique_suffix}",
            description="Shop for testing product status filtering",
            address="Test address"
        )
        assert shop_id is not None, "创建店铺失败"
        cls.test_data['shop_id'] = shop_id
        print(f"[OK] 创建店铺，ID: {shop_id}")

        # 创建不同状态的商品
        cls.test_data['online_product_id'] = TestProductStatusFiltering._create_product_with_status(
            admin_token, shop_id, "online", f"Online Product {unique_suffix}"
        )
        print(f"[OK] 创建 online 商品，ID: {cls.test_data['online_product_id']}")

        cls.test_data['offline_product_id'] = TestProductStatusFiltering._create_product_with_status(
            admin_token, shop_id, "offline", f"Offline Product {unique_suffix}"
        )
        print(f"[OK] 创建 offline 商品，ID: {cls.test_data['offline_product_id']}")

        cls.test_data['pending_product_id'] = TestProductStatusFiltering._create_product_with_status(
            admin_token, shop_id, "pending", f"Pending Product {unique_suffix}"
        )
        print(f"[OK] 创建 pending 商品，ID: {cls.test_data['pending_product_id']}")

        # 创建前端用户和 token
        frontend_username = f"frontend_user_{unique_suffix}"
        register_url = f"{API_BASE_URL}/user/register"
        register_payload = {
            "username": frontend_username,
            "password": "Admin@123456"
        }
        def register_func():
            return requests.post(register_url, json=register_payload)
        register_response = make_request_with_retry(register_func)
        if register_response.status_code == 200:
            data = register_response.json()
            cls.test_data['frontend_user_id'] = data.get("user", {}).get("id") or data.get("id")
            print(f"[OK] 创建前端用户，ID: {cls.test_data['frontend_user_id']}")

            # 登录获取 token
            login_url = f"{API_BASE_URL}/user/login"
            login_payload = {
                "username": frontend_username,
                "password": "Admin@123456"
            }
            def login_func():
                return requests.post(login_url, json=login_payload)
            login_response = make_request_with_retry(login_func)
            if login_response.status_code == 200:
                login_data = login_response.json()
                cls.test_data['frontend_token'] = login_data.get("token", "")
                print(f"[OK] 获取前端用户 token")

        print("===== 测试数据设置完成 =====\n")

        yield

        # 清理测试数据
        print("\n===== 清理商品状态过滤测试数据 =====")
        try:
            admin_product_actions.delete_product(admin_token, cls.test_data['pending_product_id'], shop_id)
        except:
            pass
        try:
            admin_product_actions.delete_product(admin_token, cls.test_data['offline_product_id'], shop_id)
        except:
            pass
        try:
            admin_product_actions.delete_product(admin_token, cls.test_data['online_product_id'], shop_id)
        except:
            pass

        try:
            admin_shop_actions.delete_shop(admin_token, shop_id)
            print(f"[OK] 删除店铺")
        except:
            pass

        print("===== 测试数据清理完成 =====\n")

    @staticmethod
    def _create_product_with_status(admin_token, shop_id, status, name):
        """创建指定状态的商品"""
        product_id = admin_product_actions.create_product(
            admin_token,
            shop_id,
            name=name,
            price=100,
            description=f"Product with status {status}",
            stock=100
        )
        if product_id:
            # 设置商品状态
            result = admin_product_actions.toggle_product_status(
                admin_token,
                product_id,
                shop_id,
                status=status
            )
            if not result:
                print(f"[WARN] 设置商品状态失败: {status}")
        return product_id

    # ==================== 客户端商品列表过滤测试 ====================

    def test_frontend_product_list_only_returns_online(self):
        """测试客户端商品列表只返回 online 状态的商品"""
        print("\n========== 测试客户端商品列表只返回 online 商品 ==========")

        assert 'frontend_token' in self.test_data, "缺少前端用户 token"

        url = f"{API_BASE_URL}/product/list"
        params = {
            "page": 1,
            "pageSize": 100,
            "shop_id": str(self.test_data['shop_id'])
        }
        headers = {"Authorization": f"Bearer {self.test_data['frontend_token']}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"获取客户端商品列表失败: {response.status_code}"

        data = response.json()
        products = data.get("data", data.get("products", []))

        # 验证所有返回的商品都是 online 状态
        for product in products:
            status = product.get("status") or product.get("Status", "")
            assert status != "offline", f"客户端不应该看到 offline 状态的商品: {product.get('name')}"
            assert status != "pending", f"客户端不应该看到 pending 状态的商品: {product.get('name')}"

        # 验证至少能看到 online 商品
        online_product_ids = [p.get("id") or p.get("ID") for p in products]
        assert str(self.test_data['online_product_id']) in online_product_ids, \
            "客户端应该能看到 online 状态的商品"

        print(f"[OK] 客户端商品列表正确过滤，共 {len(products)} 个商品，都是 online 状态")

    def test_frontend_should_not_see_offline_products(self):
        """测试客户端不应该看到 offline 状态的商品"""
        print("\n========== 测试客户端不应该看到 offline 商品 ==========")

        assert 'frontend_token' in self.test_data, "缺少前端用户 token"

        url = f"{API_BASE_URL}/product/list"
        params = {
            "page": 1,
            "pageSize": 100,
            "shop_id": str(self.test_data['shop_id'])
        }
        headers = {"Authorization": f"Bearer {self.test_data['frontend_token']}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"获取客户端商品列表失败: {response.status_code}"

        data = response.json()
        products = data.get("data", data.get("products", []))

        # 验证 offline 商品不在列表中
        product_ids = [p.get("id") or p.get("ID") for p in products]
        assert str(self.test_data['offline_product_id']) not in product_ids, \
            "客户端不应该看到 offline 状态的商品"

        print(f"[OK] 客户端正确过滤掉 offline 商品")

    def test_frontend_should_not_see_pending_products(self):
        """测试客户端不应该看到 pending 状态的商品"""
        print("\n========== 测试客户端不应该看到 pending 商品 ==========")

        assert 'frontend_token' in self.test_data, "缺少前端用户 token"

        url = f"{API_BASE_URL}/product/list"
        params = {
            "page": 1,
            "pageSize": 100,
            "shop_id": str(self.test_data['shop_id'])
        }
        headers = {"Authorization": f"Bearer {self.test_data['frontend_token']}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"获取客户端商品列表失败: {response.status_code}"

        data = response.json()
        products = data.get("data", data.get("products", []))

        # 验证 pending 商品不在列表中
        product_ids = [p.get("id") or p.get("ID") for p in products]
        assert str(self.test_data['pending_product_id']) not in product_ids, \
            "客户端不应该看到 pending 状态的商品"

        print(f"[OK] 客户端正确过滤掉 pending 商品")

    # ==================== 管理端商品列表测试 ====================

    def test_admin_product_list_returns_all_statuses(self):
        """测试管理端商品列表返回所有状态的商品"""
        print("\n========== 测试管理端商品列表返回所有状态商品 ==========")

        products = admin_product_actions.get_product_list(
            self.admin_token,
            self.test_data['shop_id'],
            page=1,
            page_size=100
        )

        # 提取商品ID列表
        product_ids = [p.get("id") or p.get("ID") for p in products]

        # 验证所有状态的商品都在列表中
        assert str(self.test_data['online_product_id']) in product_ids, \
            "管理端应该能看到 online 状态的商品"
        assert str(self.test_data['offline_product_id']) in product_ids, \
            "管理端应该能看到 offline 状态的商品"
        assert str(self.test_data['pending_product_id']) in product_ids, \
            "管理端应该能看到 pending 状态的商品"

        print(f"[OK] 管理端商品列表包含所有状态商品，共 {len(products)} 个")

    # ==================== 对比测试 ====================

    def test_admin_vs_frontend_product_count_difference(self):
        """测试管理端和客户端商品数量差异"""
        print("\n========== 测试管理端和客户端商品数量差异 ==========")

        assert 'frontend_token' in self.test_data, "缺少前端用户 token"

        # 获取管理端商品列表
        admin_products = admin_product_actions.get_product_list(
            self.admin_token,
            self.test_data['shop_id'],
            page=1,
            page_size=100
        )

        # 获取客户端商品列表
        url = f"{API_BASE_URL}/product/list"
        params = {
            "page": 1,
            "pageSize": 100,
            "shop_id": str(self.test_data['shop_id'])
        }
        headers = {"Authorization": f"Bearer {self.test_data['frontend_token']}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"获取客户端商品列表失败: {response.status_code}"
        frontend_products = response.json().get("data", response.json().get("products", []))

        # 管理端应该比客户端看到更多商品（因为包含 offline 和 pending）
        admin_product_ids = [p.get("id") or p.get("ID") for p in admin_products]
        frontend_product_ids = [p.get("id") or p.get("ID") for p in frontend_products]

        print(f"[INFO] 管理端看到 {len(admin_products)} 个商品")
        print(f"[INFO] 客户端看到 {len(frontend_products)} 个商品")

        assert len(admin_products) > len(frontend_products), \
            "管理端应该看到比客户端更多的商品（包含 offline 和 pending）"

        # 验证管理端看到 offline 和 pending 商品，但客户端看不到
        assert str(self.test_data['offline_product_id']) in admin_product_ids, \
            "管理端应该能看到 offline 商品"
        assert str(self.test_data['offline_product_id']) not in frontend_product_ids, \
            "客户端不应该能看到 offline 商品"

        assert str(self.test_data['pending_product_id']) in admin_product_ids, \
            "管理端应该能看到 pending 商品"
        assert str(self.test_data['pending_product_id']) not in frontend_product_ids, \
            "客户端不应该能看到 pending 商品"

        print(f"[OK] 管理端比客户端多看到 {len(admin_products) - len(frontend_products)} 个非 online 商品")
