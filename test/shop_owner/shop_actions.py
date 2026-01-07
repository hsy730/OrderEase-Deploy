"""
商家店铺操作工具类 - 提供店铺相关的业务操作函数
"""

import requests
import sys
from pathlib import Path

# 添加当前目录到 sys.path，以便导入 conftest
sys.path.insert(0, str(Path(__file__).parent))

from conftest import API_BASE_URL, make_request_with_retry


def get_shop_detail(shop_owner_token, shop_id):
    """获取店铺详情

    Args:
        shop_owner_token: 商家令牌
        shop_id: 店铺ID

    Returns:
        dict: 店铺详情，失败返回None
    """
    url = f"{API_BASE_URL}/shopOwner/shop/detail"
    headers = {"Authorization": f"Bearer {shop_owner_token}"}
    params = {"shop_id": shop_id}

    def request_func():
        return requests.get(url, headers=headers, params=params)

    response = make_request_with_retry(request_func)
    print(f"获取店铺详情响应状态码: {response.status_code}, 响应内容: {response.text}")
    if response.status_code == 200:
        return response.json()
    return None


def get_shop_image(shop_owner_token, shop_id):
    """获取店铺图片

    Args:
        shop_owner_token: 商家令牌
        shop_id: 店铺ID

    Returns:
        bool: 成功返回True，失败返回False
    """
    url = f"{API_BASE_URL}/shopOwner/shop/image"
    headers = {"Authorization": f"Bearer {shop_owner_token}"}
    params = {"shop_id": shop_id}

    def request_func():
        return requests.get(url, headers=headers, params=params)

    response = make_request_with_retry(request_func)
    print(f"获取店铺图片响应状态码: {response.status_code}, 响应内容: {response.text}")
    return response.status_code == 200


def update_shop(shop_owner_token, shop_id, name="Updated Shop Name", description="Updated description", owner_username="shop1"):
    """更新店铺信息

    Args:
        shop_owner_token: 商家令牌
        shop_id: 店铺ID
        name: 新名称
        description: 新描述
        owner_username: 店主用户名

    Returns:
        bool: 成功返回True，失败返回False
    """
    url = f"{API_BASE_URL}/shopOwner/shop/update"
    payload = {
        "id": shop_id,
        "name": name,
        "description": description,
        "owner_username": owner_username
    }
    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.put(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"更新店铺响应状态码: {response.status_code}, 响应内容: {response.text}")
    return response.status_code == 200


def update_order_status_flow(shop_owner_token, shop_id):
    """更新订单状态流转

    Args:
        shop_owner_token: 商家令牌
        shop_id: 店铺ID

    Returns:
        bool: 成功返回True，失败返回False
    """
    url = f"{API_BASE_URL}/shopOwner/shop/update-order-status-flow"
    payload = {
        "shop_id": shop_id,
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

    return response.status_code == 200


def change_shop_password(shop_owner_token, shop_id, old_password="Admin@123456", new_password="Admin@123456"):
    """修改商家密码

    Args:
        shop_owner_token: 商家令牌
        shop_id: 店铺ID
        old_password: 旧密码
        new_password: 新密码

    Returns:
        bool: 成功返回True，失败返回False
    """
    print(f"店铺ID: {shop_id}, 类型: {type(shop_id)}")
    
    # 直接修改密码
    url = f"{API_BASE_URL}/shopOwner/change-password"
    payload = {
        "old_password": old_password,
        "new_password": new_password
    }
    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.post(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"修改密码响应状态码: {response.status_code}, 响应内容: {response.text}")
    return response.status_code == 200