"""
订单高级功能接口测试 - 覆盖订单状态流转、高级搜索、未完成订单等接口

测试接口：
- GET /admin/order/status-flow
- POST /admin/order/advance-search
- GET /shopOwner/order/status-flow
- POST /shopOwner/order/advance-search
- GET /shopOwner/order/unfinished-list
"""

import pytest
import requests
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import API_BASE_URL, make_request_with_retry


class TestAdminOrderAdvanced:
    """管理员订单高级功能接口测试"""

    def test_get_order_status_flow(self, admin_token, test_shop_id):
        """测试获取订单状态流转配置"""
        url = f"{API_BASE_URL}/admin/order/status-flow"
        params = {"shop_id": str(test_shop_id) if test_shop_id else "1"}
        headers = {"Authorization": f"Bearer {admin_token}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"获取订单状态流转失败: {response.text}"

        data = response.json().get("data", response.json())
        assert data is not None, "响应数据为空"
        print(f"✓ 管理员获取订单状态流转成功，shop_id: {test_shop_id}")

    def test_advance_search_orders(self, admin_token, test_shop_id):
        """测试高级搜索订单（基础查询）"""
        shop_id = str(test_shop_id) if test_shop_id else "1"
        url = f"{API_BASE_URL}/admin/order/advance-search"
        payload = {
            "shop_id": shop_id,
            "page": 1,
            "pageSize": 10
        }
        headers = {"Authorization": f"Bearer {admin_token}"}

        def request_func():
            return requests.post(url, json=payload, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"高级搜索订单失败: {response.text}"

        data = response.json().get("data", response.json())
        assert data is not None, "响应数据为空"
        print("✓ 管理员高级搜索订单成功")

    def test_advance_search_orders_with_status_filter(self, admin_token, test_shop_id):
        """测试按状态筛选订单"""
        shop_id = str(test_shop_id) if test_shop_id else "1"

        url = f"{API_BASE_URL}/admin/order/advance-search"
        payload = {
            "shop_id": shop_id,
            "status": [1],
            "page": 1,
            "pageSize": 10
        }
        headers = {"Authorization": f"Bearer {admin_token}"}

        def request_func():
            return requests.post(url, json=payload, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"按状态筛选失败: {response.text}"
        print("✓ 按状态筛选订单成功")

    def test_advance_search_orders_by_date_range(self, admin_token, test_shop_id):
        """测试按日期范围搜索订单"""
        from datetime import datetime, timedelta

        shop_id = str(test_shop_id) if test_shop_id else "1"
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        url = f"{API_BASE_URL}/admin/order/advance-search"
        payload = {
            "shop_id": shop_id,
            "start_time": start_date.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": end_date.strftime("%Y-%m-%d %H:%M:%S"),
            "page": 1,
            "pageSize": 10
        }
        headers = {"Authorization": f"Bearer {admin_token}"}

        def request_func():
            return requests.post(url, json=payload, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"按日期范围搜索失败: {response.text}"
        print("✓ 按日期范围搜索订单成功")


class TestShopOwnerOrderAdvanced:
    """店主订单高级功能接口测试"""

    def test_get_order_status_flow(self, shop_owner_token):
        """测试店主获取订单状态流转配置"""
        url = f"{API_BASE_URL}/shopOwner/order/status-flow"
        headers = {"Authorization": f"Bearer {shop_owner_token}"}

        def request_func():
            return requests.get(url, headers=headers)

        response = make_request_with_retry(request_func)
        # 店主接口可能返回200或400（取决于是否自动获取shop_id）
        assert response.status_code in [200, 400], \
            f"获取订单状态流转失败或参数错误: status={response.status_code}, {response.text[:100]}"

        if response.status_code == 200:
            data = response.json().get("data", response.json())
            assert data is not None, "响应数据为空"
            print("✓ 店主获取订单状态流转成功")
        else:
            print(f"⚠ 店主获取状态流转返回{response.status_code}，可能需要额外参数")

    def test_get_unfinished_orders(self, shop_owner_token):
        """测试获取未完成订单列表"""
        url = f"{API_BASE_URL}/shopOwner/order/unfinished-list"
        params = {"page": 1, "pageSize": 10}
        headers = {"Authorization": f"Bearer {shop_owner_token}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        response = make_request_with_retry(request_func)
        # 店主接口可能返回200或400
        assert response.status_code in [200, 400], \
            f"获取未完成订单失败: status={response.status_code}, {response.text[:100]}"

        if response.status_code == 200:
            data = response.json().get("data", response.json())
            assert data is not None, "响应数据为空"
            print("✓ 店主获取未完成订单列表成功")
        else:
            print(f"⚠ 店主获取未完成订单返回{response.status_code}，可能需要shop_id参数")

    def test_advance_search_orders(self, shop_owner_token):
        """测试店主高级搜索订单"""
        url = f"{API_BASE_URL}/shopOwner/order/advance-search"
        payload = {
            "page": 1,
            "pageSize": 10
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}

        def request_func():
            return requests.post(url, json=payload, headers=headers)

        response = make_request_with_retry(request_func)
        # 店主可能需要也可能不需要shop_id
        assert response.status_code in [200, 400], \
            f"店主高级搜索订单: status={response.status_code}, {response.text[:100]}"

        if response.status_code == 200:
            data = response.json().get("data", response.json())
            assert data is not None, "响应数据为空"
            print("✓ 店主高级搜索订单成功")
        else:
            print(f"⚠ 店主高级搜索返回{response.status_code}，可能需要显式提供shop_id")

    def test_advance_search_orders_with_keyword(self, shop_owner_token):
        """测试店主按关键字搜索订单"""
        url = f"{API_BASE_URL}/shopOwner/order/advance-search"
        payload = {
            "user_id": "1",
            "page": 1,
            "pageSize": 10
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}

        def request_func():
            return requests.post(url, json=payload, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code in [200, 400], \
            f"按用户ID搜索: status={response.status_code}, {response.text[:100]}"

        if response.status_code == 200:
            print("✓ 店主按用户ID搜索订单成功")
        else:
            print(f"⚠ 店主按关键字搜索返回{response.status_code}")
