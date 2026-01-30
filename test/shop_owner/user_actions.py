"""
商家用户操作工具类 - 提供用户相关的业务操作函数
"""

import os
import requests
import sys
from pathlib import Path

# 添加当前目录到 sys.path，以便导入 conftest
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import API_BASE_URL, make_request_with_retry
from utils.response_validator import ResponseValidator
from config.test_data import test_data


def create_user(shop_owner_token, name=None, password=None, user_type="delivery", phone=None, address="Test address"):
    """创建用户

    Args:
        shop_owner_token: 商家令牌
        name: 用户名称，如果为None则生成随机名称
        password: 密码，如果为None则使用测试数据配置
        user_type: 用户类型，默认"delivery"
        phone: 电话，如果为None则使用测试数据配置
        address: 地址

    Returns:
        user_id: 用户ID，失败返回None
    """
    # 使用测试数据配置生成数据
    user_data = test_data.generate_user_data()
    if name is None:
        name = user_data["name"]
    if password is None:
        password = user_data["password"]
    if phone is None:
        phone = user_data["phone"]

    url = f"{API_BASE_URL}/shopOwner/user/create"
    payload = {
        "name": name,
        "password": password,
        "type": user_type,
        "phone": phone,
        "address": address
    }
    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.post(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    validator = ResponseValidator(response)
    if response.status_code == 200:
        user_id = validator.extract_id()
        print(f"[OK] 创建用户成功，名称: {name}, ID: {user_id}")
        return user_id
    print(f"[FAIL] 创建用户失败，状态码: {response.status_code}, 响应: {response.text}")
    return None


def get_user_list(shop_owner_token, page=1, page_size=10):
    """获取用户列表

    Args:
        shop_owner_token: 商家令牌
        page: 页码
        page_size: 每页数量

    Returns:
        list: 用户列表
    """
    url = f"{API_BASE_URL}/shopOwner/user/list"
    params = {
        "page": page,
        "pageSize": page_size
    }
    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        data = response.json()
        return data.get("data", data.get("users", []))
    return []


def get_user_simple_list(shop_owner_token):
    """获取用户简单列表

    Args:
        shop_owner_token: 商家令牌

    Returns:
        list: 用户简单列表
    """
    url = f"{API_BASE_URL}/shopOwner/user/simple-list"
    headers = {"Authorization": f"Bearer {shop_owner_token}"}
 
    def request_func():
        return requests.get(url, headers=headers)
 
    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        data = response.json()
        # API返回的是数组，不是字典
        if isinstance(data, list):
            return data
        return data.get("data", data.get("users", []))
    return []


def get_user_detail(shop_owner_token, user_id):
    """获取用户详情

    Args:
        shop_owner_token: 商家令牌
        user_id: 用户ID

    Returns:
        dict: 用户详情，失败返回None
    """
    url = f"{API_BASE_URL}/shopOwner/user/detail"
    params = {"id": user_id}
    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        return response.json()
    return None


def update_user(shop_owner_token, user_id, name="Updated User Name", address="Updated address"):
    """更新用户信息

    Args:
        shop_owner_token: 商家令牌
        user_id: 用户ID
        name: 新名称
        address: 新地址

    Returns:
        bool: 成功返回True，失败返回False
    """
    url = f"{API_BASE_URL}/shopOwner/user/update"
    payload = {
        "id": user_id,
        "name": name,
        "address": address
    }
    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.put(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        print(f"[OK] 更新用户成功，ID: {user_id}, 新名称: {name}")
        return True
    print(f"[FAIL] 更新用户失败，ID: {user_id}, 状态码: {response.status_code}, 响应: {response.text}")
    return False