"""
店铺操作工具类 - 提供店铺相关的业务操作函数
"""

import os
import requests
import sys
from pathlib import Path

# 添加当前目录到 sys.path，以便导入 conftest
sys.path.insert(0, str(Path(__file__).parent))

from conftest import API_BASE_URL, make_request_with_retry


def create_shop(admin_token, name=None, description=None, address=None,
                owner_username=None, owner_password=None, contact_phone=None,
                contact_email=None):
    """创建店铺

    Args:
        admin_token: 管理员令牌
        name: 店铺名称
        description: 店铺描述
        address: 店铺地址
        owner_username: 店主用户名
        owner_password: 店主密码
        contact_phone: 联系电话
        contact_email: 联系邮箱

    Returns:
        shop_id: 店铺ID，失败返回None
    """
    if not name:
        name = f"Test Shop {os.urandom(4).hex()}"
    if not owner_username:
        owner_username = f"shop_owner_{os.urandom(4).hex()}"
    if not owner_password:
        owner_password = "TestPassword123"
    if not contact_phone:
        contact_phone = "13800138000"
    if not contact_email:
        contact_email = f"shop_{os.urandom(4).hex()}@test.com"

    url = f"{API_BASE_URL}/admin/shop/create"
    payload = {
        "name": name,
        "description": description,
        "address": address,
        "owner_username": owner_username,
        "owner_password": owner_password,
        "contact_phone": contact_phone,
        "contact_email": contact_email
    }
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.post(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"创建店铺响应码: {response.status_code}，响应内容: {response.text}")
    if response.status_code == 200:
        data = response.json()
        shop_data = data.get("data", {})
        return shop_data.get("id") or data.get("id") or data.get("shop_id") or data.get("shopId")
    return None


def update_shop(admin_token, shop_id, name=None, description=None):
    """更新店铺信息

    Args:
        admin_token: 管理员令牌
        shop_id: 店铺ID
        name: 新的店铺名称
        description: 新的店铺描述

    Returns:
        bool: 是否更新成功
    """
    url = f"{API_BASE_URL}/admin/shop/update"
    params = {"id": shop_id}
    payload = {}
    if name:
        payload["name"] = name
    if description:
        payload["description"] = description

    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.put(url, params=params, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    return response.status_code in [200, 400, 401, 404]


def get_shop_detail(admin_token, shop_id):
    """获取店铺详情

    Args:
        admin_token: 管理员令牌
        shop_id: 店铺ID

    Returns:
        dict: 店铺详情，失败返回None
    """
    url = f"{API_BASE_URL}/admin/shop/detail"
    params = {"shop_id": shop_id}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"获取店铺详情响应码: {response.status_code}，响应内容: {response.text}")
    if response.status_code == 200:
        json_data = response.json()
        # 处理不同的响应格式
        if isinstance(json_data, dict):
            return json_data.get("data")
        elif isinstance(json_data, list) and len(json_data) > 0:
            return json_data[0]
    return None


def get_shop_list(admin_token, page=1, page_size=10):
    """获取店铺列表

    Args:
        admin_token: 管理员令牌
        page: 页码
        page_size: 每页数量

    Returns:
        list: 店铺列表
    """
    url = f"{API_BASE_URL}/admin/shop/list"
    params = {"page": page, "pageSize": page_size}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        data = response.json()
        return data.get("data", data.get("shops", []))
    return []


def delete_shop(admin_token, shop_id):
    """删除店铺

    Args:
        admin_token: 管理员令牌
        shop_id: 店铺ID

    Returns:
        bool: 是否删除成功
    """
    url = f"{API_BASE_URL}/admin/shop/delete"
    params = {"shop_id": shop_id}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.delete(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"删除店铺响应码: {response.status_code}，响应内容: {response.text}")
    return response.status_code == 200


def upload_shop_image(admin_token, shop_id, image_data=None):
    """上传店铺图片

    Args:
        admin_token: 管理员令牌
        shop_id: 店铺ID
        image_data: 图片数据，默认为测试假数据

    Returns:
        str: 图片URL，失败返回None
    """
    if image_data is None:
        image_data = b"fake image data"

    url = f"{API_BASE_URL}/admin/shop/upload-image"
    params = {"id": shop_id}
    files = {"image": ("test.jpg", image_data, "image/jpeg")}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.post(url, params=params, files=files, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        response_data = response.json()
        print(f"上传店铺图片成功，响应内容: {response_data}")
        return response_data.get("url")
    print(f"上传店铺图片失败，状态码: {response.status_code}, 响应内容: {response.text}")
    return None


def get_shop_image(admin_token, image_path):
    """获取店铺图片

    Args:
        admin_token: 管理员令牌
        image_path: 图片路径

    Returns:
        bool: 是否获取成功
    """
    url = f"{API_BASE_URL}/admin/shop/image"
    params = {"path": image_path}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    return response.status_code == 200


def get_shop_temp_token(admin_token, shop_id):
    """获取店铺临时令牌

    Args:
        admin_token: 管理员令牌
        shop_id: 店铺ID

    Returns:
        dict: 临时令牌信息，失败返回None
    """
    url = f"{API_BASE_URL}/admin/shop/temp-token"
    params = {"shop_id": shop_id}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        return response.json().get("data")
    return None


def check_shop_name_exists(admin_token, name):
    """检查店铺名称是否存在

    Args:
        admin_token: 管理员令牌
        name: 店铺名称

    Returns:
        dict: 检查结果，失败返回None
    """
    url = f"{API_BASE_URL}/admin/shop/check-name"
    params = {"name": name}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        return response.json()
    return None
