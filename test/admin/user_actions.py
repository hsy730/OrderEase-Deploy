"""
用户操作工具类 - 提供用户相关的业务操作函数
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


def create_user(admin_token, name=None, password=None, user_type="delivery",
                phone=None, address=None):
    """创建用户

    Args:
        admin_token: 管理员令牌
        name: 用户名
        password: 密码
        user_type: 用户类型（delivery/pickup/system）
        phone: 手机号
        address: 地址

    Returns:
        user_id: 用户ID，失败返回None
    """
    # 如果没有提供参数，使用测试数据配置生成
    if not name and not phone:
        user_data = test_data.generate_user_data()
        name = user_data["username"]
        password = password or user_data["password"]
        phone = user_data["phone"]
    else:
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
        "role": "public_user",  # 用户角色：private_user 或 public_user
        "type": user_type,
        "phone": phone,
        "address": address
    }
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.post(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)

    if response.status_code == 200:
        # 使用 ResponseValidator 提取 ID
        validator = ResponseValidator(response)
        user_id = validator.extract_id()
        if user_id:
            # 验证返回的用户名是否匹配
            try:
                data = response.json()
                user_response = data.get("data", data)
                returned_name = user_response.get("name") or user_response.get("Name")
                if returned_name and returned_name == name:
                    print(f"[OK] 创建用户成功，ID: {user_id}, 名称: {returned_name}")
                else:
                    print(f"[WARN] 创建用户成功但名称不匹配，期望: {name}, 返回: {returned_name}")
            except:
                print(f"[OK] 创建用户成功，ID: {user_id}")
            return user_id
        else:
            print(f"[WARN] 创建用户成功但无法提取ID，响应: {response.text}")
            return None
    else:
        print(f"[FAIL] 创建用户失败，状态码: {response.status_code}, 响应: {response.text}")
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
        json_data = response.json()
        # 处理不同的响应格式 {"Total":x,"Page":x,"PageSize":x,"Data":[...]}
        result = json_data.get("Data", json_data.get("data", json_data.get("users", [])))
        users = result if isinstance(result, list) else []
        print(f"[OK] 获取用户列表成功，数量: {len(users)}")
        return users
    else:
        print(f"[FAIL] 获取用户列表失败，状态码: {response.status_code}, 响应: {response.text}")
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

    if response.status_code == 200:
        print(f"[OK] 更新用户成功，ID: {user_id}")
        return True
    else:
        print(f"[FAIL] 更新用户失败，ID: {user_id}, 状态码: {response.status_code}, 响应: {response.text}")
        return False


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

    if response.status_code == 200:
        print(f"[OK] 删除用户成功，ID: {user_id}")
        return True
    else:
        print(f"[FAIL] 删除用户失败，ID: {user_id}, 状态码: {response.status_code}, 响应: {response.text}")
        return False
