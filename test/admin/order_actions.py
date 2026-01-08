"""
订单操作工具类 - 提供订单相关的业务操作函数
"""

import requests
import sys
from pathlib import Path

# 添加当前目录到 sys.path，以便导入 conftest
sys.path.insert(0, str(Path(__file__).parent))

from conftest import API_BASE_URL, make_request_with_retry


def create_order(admin_token, shop_id, user_id, items):
    """创建订单

    Args:
        admin_token: 管理员令牌
        shop_id: 店铺ID
        user_id: 用户ID
        items: 订单项列表，格式: [{"product_id": "xxx", "quantity": 1, "price": 100}]

    Returns:
        order_id: 订单ID，失败返回None
    """
    url = f"{API_BASE_URL}/admin/order/create"
    payload = {
        "shop_id": int(shop_id),
        "user_id": str(user_id),
        "items": items
    }
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.post(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"创建订单响应码: {response.status_code}，响应内容: {response.text}")
    if response.status_code == 200:
        data = response.json()
        return data.get("order_id") or data.get("id") or data.get("orderId")
    return None


def get_order_list(admin_token, shop_id=None, page=1, page_size=10):
    """获取订单列表

    Args:
        admin_token: 管理员令牌
        shop_id: 店铺ID（可选）
        page: 页码
        page_size: 每页数量

    Returns:
        list: 订单列表
    """
    url = f"{API_BASE_URL}/admin/order/list"
    params = {"page": page, "pageSize": page_size}
    if shop_id:
        params["shop_id"] = str(shop_id)

    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        data = response.json()
        return data.get("data", data.get("orders", []))
    return []


def get_order_detail(admin_token, order_id, shop_id):
    """获取订单详情

    Args:
        admin_token: 管理员令牌
        order_id: 订单ID
        shop_id: 店铺ID

    Returns:
        dict: 订单详情，失败返回None
    """
    url = f"{API_BASE_URL}/admin/order/detail"
    params = {"id": str(order_id), "shop_id": str(shop_id)}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"获取订单详情响应码: {response.status_code}，响应内容: {response.text}")
    if response.status_code == 200:
        json_data = response.json()
        # 处理不同的响应格式
        if isinstance(json_data, dict):
            return json_data.get("data")
        elif isinstance(json_data, list) and len(json_data) > 0:
            return json_data[0]
    return None


def update_order(admin_token, order_id, shop_id, user_id=None, total_price=None,
                 status=None, remark=None, items=None):
    """更新订单信息

    Args:
        admin_token: 管理员令牌
        order_id: 订单ID
        shop_id: 店铺ID
        user_id: 用户ID
        total_price: 总价
        status: 订单状态
        remark: 备注
        items: 订单项列表

    Returns:
        bool: 是否更新成功
    """
    url = f"{API_BASE_URL}/admin/order/update"
    params = {"id": str(order_id), "shop_id": str(shop_id)}
    payload = {"id": str(order_id)}
    if user_id:
        payload["user_id"] = str(user_id)
    if shop_id:
        payload["shop_id"] = int(shop_id)
    if total_price:
        payload["total_price"] = total_price
    if status is not None:
        payload["status"] = status
    if remark:
        payload["remark"] = remark
    if items:
        payload["items"] = items

    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.put(url, params=params, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"更新订单响应码: {response.status_code}，响应内容: {response.text}")
    return response.status_code == 200


def toggle_order_status(admin_token, order_id, shop_id, next_status):
    """切换订单状态

    Args:
        admin_token: 管理员令牌
        order_id: 订单ID
        shop_id: 店铺ID
        next_status: 下一个状态

    Returns:
        bool: 是否切换成功
    """
    url = f"{API_BASE_URL}/admin/order/toggle-status"
    payload = {
        "id": str(order_id),
        "shop_id": int(shop_id),
        "next_status": next_status
    }
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.put(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    return response.status_code == 200


def delete_order(admin_token, order_id, shop_id):
    """删除订单

    Args:
        admin_token: 管理员令牌
        order_id: 订单ID
        shop_id: 店铺ID

    Returns:
        bool: 是否删除成功
    """
    url = f"{API_BASE_URL}/admin/order/delete"
    params = {"id": str(order_id), "shop_id": str(shop_id)}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.delete(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"删除订单响应码: {response.status_code}，响应内容: {response.text}")
    return response.status_code == 200


def get_order_status_flow(admin_token, order_id, shop_id):
    """获取订单状态流转

    Args:
        admin_token: 管理员令牌
        order_id: 订单ID
        shop_id: 店铺ID

    Returns:
        dict: 订单状态流转信息，失败返回None
    """
    url = f"{API_BASE_URL}/admin/order/status-flow"
    params = {"orderId": str(order_id), "shopId": str(shop_id)}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"获取订单状态流转响应码: {response.status_code}，响应内容: {response.text}")
    if response.status_code == 200:
        return response.json().get("data")
    return None


def advance_search_order(admin_token, shop_id=None, user_id=None, status=None, 
                         start_date=None, end_date=None, page=1, page_size=10):
    """高级搜索订单

    Args:
        admin_token: 管理员令牌
        shop_id: 店铺ID（可选）
        user_id: 用户ID（可选）
        status: 订单状态（可选）
        start_date: 开始日期（可选）
        end_date: 结束日期（可选）
        page: 页码
        page_size: 每页数量

    Returns:
        dict: 搜索结果，失败返回None
    """
    url = f"{API_BASE_URL}/admin/order/advance-search"
    payload = {
        "page": page,
        "pageSize": page_size
    }
    
    if shop_id:
        payload["shop_id"] = str(shop_id)
    if user_id:
        payload["user_id"] = str(user_id)
    if status is not None:
        payload["status"] = status
    if start_date:
        payload["start_date"] = start_date
    if end_date:
        payload["end_date"] = end_date
    
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.post(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"高级搜索订单响应码: {response.status_code}，响应内容: {response.text}")
    if response.status_code == 200:
        return response.json()
    return None
