"""
用户操作工具类 - 提供用户相关的业务操作函数
"""

import os
import requests
import sys
from pathlib import Path

# 添加当前目录到 sys.path，以便导入 conftest
sys.path.insert(0, str(Path(__file__).parent))

from conftest import API_BASE_URL, make_request_with_retry


def create_user(admin_token, name=None, password=None, user_type="delivery",
                phone=None, address=None):
    """创建用户

    Args:
        admin_token: 管理员令牌
        name: 用户名
        password: 密码
        user_type: 用户类型（delivery/customer等）
        phone: 手机号
        address: 地址

    Returns:
        user_id: 用户ID，失败返回None
    """
    if not name:
        name = f"Test User {os.urandom(4).hex()}"
    if not password:
        password = "Admin@123456"
    if not phone:
        phone = "13800138000"

    url = f"{API_BASE_URL}/admin/user/create"
    payload = {
        "name": name,
        "password": password,
        "type": user_type,
        "phone": phone,
        "address": address
    }
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.post(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"创建用户响应码: {response.status_code}，响应内容: {response.text}")
    if response.status_code == 200:
        data = response.json()
        return data.get("id") or data.get("user_id") or data.get("userId")
    return None


def get_user_list(admin_token, page=1, page_size=10):
    """获取用户列表

    Args:
        admin_token: 管理员令牌
        page: 页码
        page_size: 每页数量

    Returns:
        list: 用户列表
    """
    url = f"{API_BASE_URL}/admin/user/list"
    params = {"page": page, "pageSize": page_size}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        data = response.json()
        return data.get("data", data.get("users", []))
    return []


def get_user_simple_list(admin_token):
    """获取用户简单列表

    Args:
        admin_token: 管理员令牌

    Returns:
        list: 用户简单列表
    """
    url = f"{API_BASE_URL}/admin/user/simple-list"
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        json_data = response.json()
        # 处理不同的响应格式
        if isinstance(json_data, list):
            return json_data
        elif isinstance(json_data, dict):
            return json_data.get("data", [])
    return []


def get_user_detail(admin_token, user_id):
    """获取用户详情

    Args:
        admin_token: 管理员令牌
        user_id: 用户ID

    Returns:
        dict: 用户详情，失败返回None
    """
    url = f"{API_BASE_URL}/admin/user/detail"
    params = {"id": user_id}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        return response.json().get("data")
    return None


def update_user(admin_token, user_id, name=None, address=None):
    """更新用户信息

    Args:
        admin_token: 管理员令牌
        user_id: 用户ID
        name: 新的用户名
        address: 新的地址

    Returns:
        bool: 是否更新成功
    """
    url = f"{API_BASE_URL}/admin/user/update"
    payload = {"id": str(user_id)}
    if name:
        payload["name"] = name
    if address:
        payload["address"] = address

    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.put(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"更新用户响应码: {response.status_code}，响应内容: {response.text}")
    return response.status_code == 200


def delete_user(admin_token, user_id):
    """删除用户

    Args:
        admin_token: 管理员令牌
        user_id: 用户ID

    Returns:
        bool: 是否删除成功
    """
    url = f"{API_BASE_URL}/admin/user/delete"
    params = {"id": user_id}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.delete(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"删除用户响应码: {response.status_code}，响应内容: {response.text}")
    return response.status_code == 200
