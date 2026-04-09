"""
数据看板统计接口测试 - 覆盖 admin 和 shopOwner 的 dashboard 接口

测试接口：
- GET /admin/dashboard/stats
- GET /shopOwner/dashboard/stats
"""

import pytest
import requests
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import API_BASE_URL, make_request_with_retry


class TestAdminDashboardStats:
    """管理员数据看板统计接口测试"""

    def test_get_dashboard_stats_with_shop_id(self, admin_token, test_shop_id):
        """测试获取指定店铺的数据看板统计"""
        url = f"{API_BASE_URL}/admin/dashboard/stats"
        params = {
            "shop_id": test_shop_id if test_shop_id else "1",
            "period": "week"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"获取dashboard统计失败: {response.text}"

        data = response.json().get("data", response.json())
        assert data is not None, "响应数据为空"

        # 验证响应包含必要的统计字段
        assert "orderStats" in data or "order_stats" in data, "缺少订单统计字段"
        assert "productStats" in data or "product_stats" in data, "缺少商品统计字段"
        assert "userStats" in data or "user_stats" in data, "缺少用户统计字段"
        print(f"✓ 管理员获取dashboard统计成功，shop_id: {test_shop_id}")

    def test_get_dashboard_stats_different_periods(self, admin_token, test_shop_id):
        """测试不同时间周期的统计数据"""
        periods = ["week", "month", "year"]
        shop_id = test_shop_id if test_shop_id else "1"

        for period in periods:
            url = f"{API_BASE_URL}/admin/dashboard/stats"
            params = {
                "shop_id": shop_id,
                "period": period
            }
            headers = {"Authorization": f"Bearer {admin_token}"}

            def request_func():
                return requests.get(url, params=params, headers=headers)

            response = make_request_with_retry(request_func)
            assert response.status_code == 200, f"获取{period}周期统计失败: {response.text}"
            print(f"✓ 获取{period}周期统计成功")

    def test_get_dashboard_stats_invalid_shop_id(self, admin_token):
        """测试使用无效的店铺ID"""
        url = f"{API_BASE_URL}/admin/dashboard/stats"
        params = {"shop_id": "invalid_id"}
        headers = {"Authorization": f"Bearer {admin_token}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 400, f"无效店铺ID应返回400，实际: {response.status_code}"
        print("✓ 无效店铺ID正确返回400错误")

    def test_get_dashboard_stats_nonexistent_shop(self, admin_token):
        """测试使用不存在的店铺ID"""
        url = f"{API_BASE_URL}/admin/dashboard/stats"
        params = {"shop_id": "999999999"}
        headers = {"Authorization": f"Bearer {admin_token}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 404, f"不存在的店铺应返回404，实际: {response.status_code}"
        print("✓ 不存在的店铺正确返回404错误")


class TestShopOwnerDashboardStats:
    """店主数据看板统计接口测试"""

    def test_get_dashboard_stats_without_shop_id(self, shop_owner_token):
        """测试店主获取dashboard统计（不需要shop_id参数）"""
        url = f"{API_BASE_URL}/shopOwner/dashboard/stats"
        params = {"period": "week"}
        headers = {"Authorization": f"Bearer {shop_owner_token}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"店主获取dashboard统计失败: {response.text}"

        data = response.json().get("data", response.json())
        assert data is not None, "响应数据为空"

        # 验证响应结构
        assert "orderStats" in data or "order_stats" in data, "缺少订单统计字段"
        print("✓ 店主获取dashboard统计成功")

    def test_get_dashboard_stats_monthly(self, shop_owner_token):
        """测试店主获取月度统计"""
        url = f"{API_BASE_URL}/shopOwner/dashboard/stats"
        params = {"period": "month"}
        headers = {"Authorization": f"Bearer {shop_owner_token}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"获取月度统计失败: {response.text}"
        print("✓ 店主获取月度统计成功")
