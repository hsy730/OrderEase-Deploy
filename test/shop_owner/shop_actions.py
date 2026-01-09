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


def upload_shop_image(shop_owner_token, shop_id, image_path=None):
    """上传店铺图片

    Args:
        shop_owner_token: 商家令牌
        shop_id: 店铺ID
        image_path: 图片文件路径，默认为test.png

    Returns:
        str: 图片URL，失败返回None
    """
    if image_path is None:
        # 默认使用test.png
        image_path = Path(__file__).parent.parent / "test.png"

    # 读取图片文件
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
    except FileNotFoundError:
        print(f"图片文件不存在: {image_path}")
        return None

    url = f"{API_BASE_URL}/shopOwner/shop/upload-image"
    params = {"id": shop_id}
    files = {"image": ("test.png", image_data, "image/png")}
    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.post(url, params=params, files=files, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        response_data = response.json()
        print(f"上传店铺图片成功，响应内容: {response_data}")
        return response_data.get("url")
    print(f"上传店铺图片失败，状态码: {response.status_code}, 响应内容: {response.text}")
    return None


def get_shop_image(shop_owner_token, shop_id):
    """获取店铺图片

    Args:
        shop_owner_token: 商家令牌
        shop_id: 店铺ID

    Returns:
        bool: 成功返回True，失败返回False
    """
    # 先获取店铺详情，获取图片路径
    detail_url = f"{API_BASE_URL}/shopOwner/shop/detail"
    headers = {"Authorization": f"Bearer {shop_owner_token}"}
    params = {"shop_id": shop_id}

    def detail_func():
        return requests.get(detail_url, headers=headers, params=params)

    detail_response = make_request_with_retry(detail_func)
    if detail_response.status_code != 200:
        print(f"获取店铺详情失败，无法获取图片路径，状态码: {detail_response.status_code}")
        return False

    detail_data = detail_response.json()
    # 处理不同的响应格式
    shop_detail = detail_data.get("data") if isinstance(detail_data, dict) else detail_data
    if shop_detail is None:
        shop_detail = detail_data

    image_url = shop_detail.get("image_url") if isinstance(shop_detail, dict) else None

    # 如果没有图片，先上传图片
    if not image_url:
        print("店铺没有设置图片，正在上传图片...")
        image_url = upload_shop_image(shop_owner_token, shop_id)
        if not image_url:
            print("上传图片失败")
            return False
        print(f"图片上传成功，URL: {image_url}")

    # 获取店铺图片
    url = f"{API_BASE_URL}/shopOwner/shop/image"
    params = {"path": image_url}

    def request_func():
        return requests.get(url, headers=headers, params=params)

    response = make_request_with_retry(request_func)
    print(f"获取店铺图片响应状态码: {response.status_code}")
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


def get_shop_temp_token(shop_owner_token, shop_id):
    """获取店铺临时令牌

    Args:
        shop_owner_token: 商家令牌
        shop_id: 店铺ID

    Returns:
        dict: 包含临时令牌的响应数据，失败返回None
        格式: {"shop_id": int, "token": str, "expires_at": str}
    """
    url = f"{API_BASE_URL}/shopOwner/shop/temp-token"
    headers = {"Authorization": f"Bearer {shop_owner_token}"}
    params = {"shop_id": shop_id}

    def request_func():
        return requests.get(url, headers=headers, params=params)

    response = make_request_with_retry(request_func)
    print(f"获取店铺临时令牌响应状态码: {response.status_code}, 响应内容: {response.text}")
    if response.status_code == 200:
        return response.json()
    return None


def temp_login(shop_id, temp_token):
    """使用临时令牌登录

    Args:
        shop_id: 店铺ID
        temp_token: 临时令牌（6位数字）

    Returns:
        dict: 登录成功的响应数据，失败返回None
        格式: {"role": str, "user_info": dict, "token": str, "expiredAt": int}
    """
    url = f"{API_BASE_URL}/shop/temp-login"
    payload = {
        "shop_id": shop_id,
        "token": temp_token
    }

    def request_func():
        return requests.post(url, json=payload)

    response = make_request_with_retry(request_func)
    print(f"临时令牌登录响应状态码: {response.status_code}, 响应内容: {response.text}")
    if response.status_code == 200:
        return response.json()
    return None