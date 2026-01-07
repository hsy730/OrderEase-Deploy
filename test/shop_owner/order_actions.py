"""
商家订单操作工具类 - 提供订单相关的业务操作函数
"""

import requests
import sys
from pathlib import Path

# 添加当前目录到 sys.path，以便导入 conftest
sys.path.insert(0, str(Path(__file__).parent))

from conftest import API_BASE_URL, make_request_with_retry, assert_response_status


def create_order(shop_owner_token, shop_id, user_id, items):
    """创建订单

    Args:
        shop_owner_token: 商家令牌
        shop_id: 店铺ID
        user_id: 用户ID
        items: 订单项列表，格式: [{"product_id": "xxx", "quantity": 1, "price": 100}]

    Returns:
        order_id: 订单ID，失败返回None
    """
    url = f"{API_BASE_URL}/shopOwner/order/create"
    payload = {
        "shop_id": shop_id,
        "user_id": user_id,
        "items": items
    }
    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.post(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"创建订单响应状态码: {response.status_code}, 响应内容: {response.text}")
    if response.status_code == 200:
        data = response.json()
        return data.get("order_id") or data.get("id") or data.get("orderId")
    return None


def get_order_list(shop_owner_token, shop_id=None, page=1, page_size=10):
    """获取订单列表

    Args:
        shop_owner_token: 商家令牌
        shop_id: 店铺ID（可选）
        page: 页码
        page_size: 每页数量

    Returns:
        list: 订单列表
    """
    url = f"{API_BASE_URL}/shopOwner/order/list"
    params = {"page": page, "pageSize": page_size}
    if shop_id:
        params["shop_id"] = str(shop_id)

    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        data = response.json()
        return data.get("data", data.get("orders", []))
    return []


def get_order_detail(shop_owner_token, order_id, shop_id):
    """获取订单详情

    Args:
        shop_owner_token: 商家令牌
        order_id: 订单ID
        shop_id: 店铺ID

    Returns:
        dict: 订单详情，失败返回None
    """
    url = f"{API_BASE_URL}/shopOwner/order/detail"
    params = {
        "id": order_id,
        "shop_id": int(shop_id) if shop_id else 1
    }
    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"获取订单详情响应状态码: {response.status_code}, 响应内容: {response.text}")
    if response.status_code == 200:
        return response.json()
    return None


def update_order(shop_owner_token, order_id, shop_id, user_id, items):
    """更新订单信息

    Args:
        shop_owner_token: 商家令牌
        order_id: 订单ID
        shop_id: 店铺ID
        user_id: 用户ID
        items: 订单项列表

    Returns:
        bool: 成功返回True，失败返回False
    """
    url = f"{API_BASE_URL}/shopOwner/order/update"
    params = {"id": order_id}
    payload = {
        "shop_id": int(shop_id) if shop_id else 1,
        "user_id": user_id,
        "items": items
    }
    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.put(url, params=params, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"更新订单响应状态码: {response.status_code}, 响应内容: {response.text}")
    return response.status_code == 200


def toggle_order_status(shop_owner_token, order_id, shop_id, next_status=10):
    """切换订单状态

    Args:
        shop_owner_token: 商家令牌
        order_id: 订单ID
        shop_id: 店铺ID
        next_status: 下一个状态值，默认10

    Returns:
        bool: 成功返回True，失败返回False
    """
    url = f"{API_BASE_URL}/shopOwner/order/toggle-status"
    payload = {
        "id": order_id,
        "shop_id": int(shop_id) if shop_id else 1,
        "next_status": next_status
    }
    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    print(f"切换订单状态请求参数: {payload}")

    def request_func():
        return requests.put(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"切换订单状态响应状态码: {response.status_code}, 响应内容: {response.text}")
    return response.status_code == 200


def delete_order(shop_owner_token, order_id, shop_id):
    """删除订单

    Args:
        shop_owner_token: 商家令牌
        order_id: 订单ID
        shop_id: 店铺ID

    Returns:
        bool: 成功返回True，失败返回False
    """
    url = f"{API_BASE_URL}/shopOwner/order/delete"
    params = {
        "id": order_id,
        "shop_id": int(shop_id) if shop_id else 1
    }
    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.delete(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"删除订单响应状态码: {response.status_code}, 响应内容: {response.text}")
    return response.status_code == 200