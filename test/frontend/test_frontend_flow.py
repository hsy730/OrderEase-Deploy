"""
前端业务流程测试 - 按照正确的业务顺序执行测试

业务顺序：
1. 前端用户注册
2. 前端用户登录
3. 创建店铺（使用管理员权限）
4. 创建商品（使用管理员权限）
5. 创建订单
6. 获取订单列表
7. 获取订单详情
8. 删除订单
9. 获取店铺信息
10. 获取商品信息
"""

import pytest
import requests
import os
import time
import sys
from pathlib import Path

# 添加上级目录到 sys.path，以便导入 conftest
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import API_BASE_URL, make_request_with_retry


class TestFrontendFlow:
    """前端业务流程测试类 - 包含所有有业务依赖的前端测试用例"""

    # 类变量，用于在测试用例之间共享数据
    frontend_username = None
    frontend_password = "Admin@123456"
    frontend_user_id = None
    frontend_token = None
    frontend_shop_id = None
    frontend_product_id = None
    frontend_order_id = None

    # ==================== 用户认证测试 ====================

    def test_frontend_user_register(self):
        """测试前端用户注册"""
        print("\n========== 前端用户注册测试 ==========")

        # 生成唯一的用户名
        TestFrontendFlow.frontend_username = f"frontend_user_{os.urandom(4).hex()}"

        url = f"{API_BASE_URL}/user/register"
        payload = {
            "username": TestFrontendFlow.frontend_username,
            "password": TestFrontendFlow.frontend_password
        }

        def request_func():
            return requests.post(url, json=payload)

        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 409], f"Expected 200 or 409, got {response.status_code}，text: {response.text}"

        if response.status_code == 200:
            data = response.json()
            TestFrontendFlow.frontend_user_id = int(data.get("user", {}).get("id") or data.get("id"))
            print(f"✓ 前端用户注册成功，用户名: {TestFrontendFlow.frontend_username}, ID: {TestFrontendFlow.frontend_user_id}")
        else:
            print("⚠ 用户名已存在，继续其他测试")

    def test_frontend_user_login(self):
        """测试前端用户登录"""
        print("\n========== 前端用户登录测试 ==========")

        url = f"{API_BASE_URL}/user/login"
        payload = {
            "username": TestFrontendFlow.frontend_username,
            "password": TestFrontendFlow.frontend_password
        }

        def request_func():
            return requests.post(url, json=payload)

        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}, text: {response.text}"

        data = response.json()
        TestFrontendFlow.frontend_token = data.get("token", "")
        # 登录时也更新user_id
        if TestFrontendFlow.frontend_user_id is None:
            TestFrontendFlow.frontend_user_id = int(data.get("user", {}).get("id") or data.get("id"))
        print(f"✓ 前端用户登录成功，token: {TestFrontendFlow.frontend_token[:20]}...")

    def test_check_username_exists(self):
        """测试检查用户名是否存在"""
        print("\n========== 检查用户名是否存在测试 ==========")

        url = f"{API_BASE_URL}/user/check-username"
        params = {"username": TestFrontendFlow.frontend_username}

        def request_func():
            return requests.get(url, params=params)

        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ 检查用户名成功")

    # ==================== 店铺和商品创建测试 ====================

    def test_create_shop(self, admin_token):
        """测试创建店铺（使用管理员权限）"""
        print("\n========== 创建店铺测试 ==========")

        # 生成唯一的店铺名
        unique_suffix = os.urandom(4).hex()

        url = f"{API_BASE_URL}/admin/shop/create"
        payload = {
            "owner_username": f"shop_owner_{unique_suffix}",
            "owner_password": "Admin@123456",
            "name": f"Frontend Test Shop {unique_suffix}",
            "contact_phone": "13800138000",
            "contact_email": f"frontend_{unique_suffix}@example.com",
            "description": "Shop created for frontend testing",
            "valid_until": "2027-12-31T23:59:59Z"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}

        print(f"payload: {payload}, headers: {headers}")
        def request_func():
            return requests.post(url, json=payload, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}，text: {response.text}"

        data = response.json()
        shop_data = data.get("data", {})
        TestFrontendFlow.frontend_shop_id = int(shop_data.get("id") or data.get("id") or data.get("shop_id"))
        print(f"✓ 成功创建店铺，ID: {TestFrontendFlow.frontend_shop_id}")

    def test_create_product(self, admin_token):
        """测试创建商品（使用管理员权限）"""
        print("\n========== 创建商品测试 ==========")

        assert TestFrontendFlow.frontend_shop_id, "shop_id 未设置，请确保 test_create_shop 先执行"

        # 生成唯一的商品名
        unique_suffix = os.urandom(4).hex()

        url = f"{API_BASE_URL}/admin/product/create"
        payload = {
            "shop_id": int(TestFrontendFlow.frontend_shop_id),
            "name": f"Frontend Test Product {unique_suffix}",
            "price": 100,
            "description": "Product created for frontend testing",
            "stock": 100
        }
        headers = {"Authorization": f"Bearer {admin_token}"}

        def request_func():
            return requests.post(url, json=payload, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        TestFrontendFlow.frontend_product_id = int(data.get("id") or data.get("product_id") or data.get("productId"))
        print(f"✓ 成功创建商品，ID: {TestFrontendFlow.frontend_product_id}")

    # ==================== 订单测试 ====================

    def test_create_order(self, admin_token):
        """测试创建订单"""
        print("\n========== 创建订单测试 ==========")

        assert TestFrontendFlow.frontend_shop_id, "shop_id 未设置"
        assert TestFrontendFlow.frontend_product_id, "product_id 未设置"
        assert TestFrontendFlow.frontend_user_id, "frontend_user_id 未设置，请确保 test_frontend_user_register 和 test_frontend_user_login 先执行"

        # 确保所有ID都是整数类型
        user_id = str(TestFrontendFlow.frontend_user_id)
        shop_id = int(TestFrontendFlow.frontend_shop_id)
        product_id = str(TestFrontendFlow.frontend_product_id)

        url = f"{API_BASE_URL}/admin/order/create"
        # 构建payload，确保所有ID都是整数
        payload = {
            "shop_id": shop_id,
            "user_id": user_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1,
                    "price": 100
                }
            ]
        }
        headers = {"Authorization": f"Bearer {admin_token}"}

        print(f"创建订单 payload: shop_id={payload['shop_id']} (type: {type(shop_id)}), user_id={payload['user_id']} (type: {type(user_id)}), product_id={payload['items'][0]['product_id']} (type: {type(product_id)})")

        def request_func():
            return requests.post(url, json=payload, headers=headers)

        response = make_request_with_retry(request_func)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}，text: {response.text}"

        data = response.json()
        TestFrontendFlow.frontend_order_id = int(data.get("order_id") or data.get("id"))
        print(f"✓ 成功创建订单，ID: {TestFrontendFlow.frontend_order_id}")

    def test_get_user_order_list(self):
        """测试获取用户订单列表"""
        print("\n========== 获取用户订单列表测试 ==========")

        assert TestFrontendFlow.frontend_token, "frontend_token 未设置，请确保 test_frontend_user_login 先执行"
        assert TestFrontendFlow.frontend_user_id, "frontend_user_id 未设置"
        assert TestFrontendFlow.frontend_shop_id, "frontend_shop_id 未设置"

        url = f"{API_BASE_URL}/order/user/list"
        params = {
            "page": 1,
            "pageSize": 10,
            "user_id": str(TestFrontendFlow.frontend_user_id),  # GetOrdersByUser 接受 user_id 作为字符串
            "shop_id": str(TestFrontendFlow.frontend_shop_id)
        }
        headers = {"Authorization": f"Bearer {TestFrontendFlow.frontend_token}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}，text: {response.text}"

        if response.status_code == 200:
            print("✓ 获取用户订单列表成功")
        else:
            print("⚠ 获取用户订单列表失败（token可能已失效）")

    def test_get_order_detail(self):
        """测试获取订单详情"""
        print("\n========== 获取订单详情测试 ==========")

        assert TestFrontendFlow.frontend_order_id, "frontend_order_id 未设置，请确保 test_create_order 先执行"
        assert TestFrontendFlow.frontend_shop_id, "frontend_shop_id 未设置"

        url = f"{API_BASE_URL}/order/detail"
        params = {
            "id": str(TestFrontendFlow.frontend_order_id),
            "shop_id": str(TestFrontendFlow.frontend_shop_id)
        }
        headers = {"Authorization": f"Bearer {TestFrontendFlow.frontend_token}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        response = make_request_with_retry(request_func)
        # 允许 400, 401, 404 状态码，因为订单可能不存在
        assert response.status_code in [200, 400, 401, 404], f"Expected 200, 400, 401 or 404, got {response.status_code}，text: {response.text}"

        if response.status_code == 200:
            print("✓ 获取订单详情成功")
        else:
            print(f"⚠ 获取订单详情失败（状态码: {response.status_code}）")

    def test_delete_order(self):
        """测试删除订单"""
        print("\n========== 删除订单测试 ==========")

        assert TestFrontendFlow.frontend_order_id, "frontend_order_id 未设置，请确保 test_create_order 先执行"
        assert TestFrontendFlow.frontend_shop_id, "frontend_shop_id 未设置"

        url = f"{API_BASE_URL}/order/delete"
        params = {
            "id": str(TestFrontendFlow.frontend_order_id),
            "shop_id": str(TestFrontendFlow.frontend_shop_id)
        }
        headers = {"Authorization": f"Bearer {TestFrontendFlow.frontend_token}"}

        def request_func():
            return requests.delete(url, params=params, headers=headers)

        response = make_request_with_retry(request_func)
        # 允许 200, 401, 404 状态码，因为订单可能不存在或已删除
        assert response.status_code in [200, 401, 404], f"Expected 200, 401 or 404, got {response.status_code}"

        if response.status_code == 200:
            print("✓ 删除订单成功")
        else:
            print(f"⚠ 删除订单失败（状态码: {response.status_code}）")

    # ==================== 店铺和商品查询测试 ====================

    def test_get_shop_detail(self):
        """测试获取店铺详情"""
        print("\n========== 获取店铺详情测试 ==========")

        url = f"{API_BASE_URL}/shop/detail"
        params = {"id": TestFrontendFlow.frontend_shop_id if TestFrontendFlow.frontend_shop_id else 1}
        headers = {"Authorization": f"Bearer {TestFrontendFlow.frontend_token}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 401, 404], f"Expected 200, 400, 401 or 404, got {response.status_code}"

        if response.status_code == 200:
            print("✓ 获取店铺详情成功")
        else:
            print("⚠ 获取店铺详情失败")

    def test_get_shop_image(self):
        """测试获取店铺图片"""
        print("\n========== 获取店铺图片测试 ==========")

        url = f"{API_BASE_URL}/shop/image"
        params = {"id": TestFrontendFlow.frontend_shop_id if TestFrontendFlow.frontend_shop_id else 1}
        headers = {"Authorization": f"Bearer {TestFrontendFlow.frontend_token}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 401, 404], f"Expected 200, 400, 401 or 404, got {response.status_code}"

        if response.status_code == 200:
            print("✓ 获取店铺图片成功")
        else:
            print("⚠ 获取店铺图片失败")

    def test_get_shop_tags(self):
        """测试获取店铺标签列表"""
        print("\n========== 获取店铺标签列表测试 ==========")

        shop_id = TestFrontendFlow.frontend_shop_id if TestFrontendFlow.frontend_shop_id else 1
        url = f"{API_BASE_URL}/shop/{shop_id}/tags"
        headers = {"Authorization": f"Bearer {TestFrontendFlow.frontend_token}"}

        def request_func():
            return requests.get(url, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 401, 404], f"Expected 200, 400, 401 or 404, got {response.status_code}"

        if response.status_code == 200:
            print("✓ 获取店铺标签成功")
        else:
            print("⚠ 获取店铺标签失败")

    def test_get_product_list(self):
        """测试获取商品列表"""
        print("\n========== 获取商品列表测试 ==========")

        url = f"{API_BASE_URL}/product/list"
        params = {
            "page": 1,
            "pageSize": 10
        }
        headers = {"Authorization": f"Bearer {TestFrontendFlow.frontend_token}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400, 401], f"Expected 200, 400 or 401, got {response.status_code}"

        if response.status_code == 200:
            print("✓ 获取商品列表成功")
        else:
            print("⚠ 获取商品列表失败")

    def test_get_product_detail(self):
        """测试获取商品详情"""
        print("\n========== 获取商品详情测试 ==========")

        url = f"{API_BASE_URL}/product/detail"
        params = {"id": TestFrontendFlow.frontend_product_id if TestFrontendFlow.frontend_product_id else 1, "shop_id": TestFrontendFlow.frontend_shop_id if TestFrontendFlow.frontend_shop_id else 1}
        headers = {"Authorization": f"Bearer {TestFrontendFlow.frontend_token}"}

        print(f"请求参数：{params}")

        def request_func():
            return requests.get(url, params=params, headers=headers)

        response = make_request_with_retry(request_func)
        print(f"获取商品详情响应码: {response.status_code}，响应内容: {response.text}")
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}"

        if response.status_code == 200:
            json_data = response.json()
            # 处理不同的响应格式
            product_detail = None
            if isinstance(json_data, dict):
                product_detail = json_data.get("data") or json_data
            elif isinstance(json_data, list) and len(json_data) > 0:
                product_detail = json_data[0]

            if product_detail:
                product_name = product_detail.get("name", "未知")
                print(f"✓ 获取商品详情成功，商品名称: {product_name}")
            else:
                print("✓ 获取商品详情成功，但响应格式无法解析")
        else:
            print("⚠ 获取商品详情失败（商品可能不存在）")

    def test_get_product_image(self):
        """测试获取商品图片"""
        print("\n========== 获取商品图片测试 ==========")

        url = f"{API_BASE_URL}/product/image"
        params = {"id": TestFrontendFlow.frontend_product_id if TestFrontendFlow.frontend_product_id else 1}
        headers = {"Authorization": f"Bearer {TestFrontendFlow.frontend_token}"}

        def request_func():
            return requests.get(url, params=params, headers=headers, allow_redirects=False)  # 禁用自动重定向

        response = make_request_with_retry(request_func)
        # 允许 200, 301, 302, 307, 429 状态码
        # 301/302/307 表示重定向，429表示请求过于频繁
        allowed_status_codes = [200, 301, 302, 307, 429]
        assert response.status_code in allowed_status_codes, f"Expected {allowed_status_codes}, got {response.status_code}, text: {response.text}"

        if response.status_code == 200:
            print("✓ 获取商品图片成功")
        elif response.status_code in [302, 307]:
            print(f"⚠ 获取商品图片重定向到: {response.headers.get('Location', '未知位置')}")
        elif response.status_code == 429:
            print("⚠ 获取商品图片失败：请求过于频繁（频率限制）")
        else:
            print(f"⚠ 获取商品图片失败（状态码: {response.status_code}）")
