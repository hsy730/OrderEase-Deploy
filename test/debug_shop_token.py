#!/usr/bin/env python3
"""
调试商家token认证问题
"""
import os
import sys
import requests
import time
import json

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from conftest import make_request_with_retry

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080/api/order-ease/v1")

def get_admin_token():
    """获取管理员token"""
    url = f"{API_BASE_URL}/login"
    payload = {
        "username": "admin",
        "password": "Admin@123456"
    }
    
    def request_func():
        return requests.post(url, json=payload)
    
    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        data = response.json()
        return data.get("token", "")
    return ""

def create_shop_and_get_token():
    """创建店铺并获取店主token"""
    import os
    import time
    
    # 先获取admin token
    admin_token = get_admin_token()
    if not admin_token:
        print("管理员登录失败")
        return ""
    
    # 生成唯一的店主用户名
    import secrets
    unique_suffix = secrets.token_hex(4)
    owner_username = f"shop_owner_{unique_suffix}"
    
    # 创建店铺（会自动创建店主用户）
    shop_url = f"{API_BASE_URL}/admin/shop/create"
    shop_payload = {
        "owner_username": owner_username,
        "owner_password": "Admin@123456",
        "name": f"Test Shop {unique_suffix}",
        "contact_phone": "13800138000",
        "contact_email": f"test_{unique_suffix}@example.com",
        "description": "Shop created for testing",
        "valid_until": "2027-12-31T23:59:59Z"
    }
    shop_headers = {"Authorization": f"Bearer {admin_token}"}
    
    def shop_request_func():
        return requests.post(shop_url, json=shop_payload, headers=shop_headers)
    
    shop_response = make_request_with_retry(shop_request_func)
    if shop_response.status_code != 200:
        print(f"创建店铺失败: {shop_response.status_code}, {shop_response.text}")
        return ""
    
    shop_data = shop_response.json()
    print(f"成功创建店铺: {shop_data}")
    
    # 等待系统处理
    time.sleep(1)
    
    # 使用店主账号登录获取token
    login_url = f"{API_BASE_URL}/login"
    login_payload = {
        "username": owner_username,
        "password": "Admin@123456"
    }
    
    def login_request_func():
        return requests.post(login_url, json=login_payload)
    
    login_response = make_request_with_retry(login_request_func)
    if login_response.status_code != 200:
        print(f"店主登录失败: {login_response.status_code}, {login_response.text}")
        return ""
    
    login_data = login_response.json()
    token = login_data.get("token", "")
    print(f"成功获取店主token: {owner_username}")
    return token

def test_shop_owner_api(shop_owner_token, shop_id=None):
    """测试商家API"""
    if not shop_owner_token:
        print("商家token为空")
        return
    
    headers = {"Authorization": f"Bearer {shop_owner_token}"}
    
    print(f"\n测试商家API:")
    print(f"Token: {shop_owner_token[:50]}...")
    
    # 测试获取店铺详情（需要shop_id参数）
    url = f"{API_BASE_URL}/shopOwner/shop/detail"
    params = {}
    if shop_id:
        params["shop_id"] = shop_id
    
    print(f"\n1. 获取店铺详情:")
    print(f"URL: {url}")
    print(f"参数: {params}")
    
    def request_func():
        return requests.get(url, headers=headers, params=params)
    
    response = make_request_with_retry(request_func)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
    
    # 测试获取商品列表（需要shop_id参数）
    url = f"{API_BASE_URL}/shopOwner/product/list"
    params = {"page": 1, "pageSize": 10}
    if shop_id:
        params["shop_id"] = shop_id
    
    print(f"\n2. 获取商品列表:")
    print(f"URL: {url}")
    print(f"参数: {params}")
    
    def product_request_func():
        return requests.get(url, params=params, headers=headers)
    
    product_response = make_request_with_retry(product_request_func)
    print(f"状态码: {product_response.status_code}")
    print(f"响应: {product_response.text}")
    
    # 测试获取临时令牌（需要shop_id参数）
    url = f"{API_BASE_URL}/shopOwner/shop/temp-token"
    params = {}
    if shop_id:
        params["shop_id"] = shop_id
    
    print(f"\n3. 获取临时令牌:")
    print(f"URL: {url}")
    print(f"参数: {params}")
    
    def temp_token_request_func():
        return requests.get(url, headers=headers, params=params)
    
    temp_token_response = make_request_with_retry(temp_token_request_func)
    print(f"状态码: {temp_token_response.status_code}")
    print(f"响应: {temp_token_response.text}")

def decode_jwt(token):
    """解码JWT token（仅用于调试）"""
    import base64
    import json
    
    if not token:
        return None
    
    parts = token.split('.')
    if len(parts) != 3:
        return None
    
    # 解码payload部分
    payload = parts[1]
    # 添加padding
    padding = 4 - len(payload) % 4
    if padding != 4:
        payload += '=' * padding
    
    try:
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except:
        return None

def main():
    print("=" * 80)
    print("调试商家token认证问题")
    print("=" * 80)
    
    # 1. 获取商家token
    print("\n1. 获取商家token...")
    shop_owner_token = create_shop_and_get_token()
    if not shop_owner_token:
        print("获取商家token失败")
        return
    
    # 2. 解码token查看claims
    print("\n2. 解码token查看claims...")
    claims = decode_jwt(shop_owner_token)
    if claims:
        print(f"Claims: {json.dumps(claims, indent=2, ensure_ascii=False)}")
        username = claims.get('username', '')
        user_id = claims.get('user_id', '')
        print(f"用户名: {username}")
        print(f"用户ID: {user_id}")
        print(f"用户名是否为'admin': {username == 'admin'}")
    else:
        print("无法解码token")
    
    # 从claims中获取shop_id（用户ID就是shop_id？）
    shop_id = claims.get('user_id') if claims else None
    print(f"\n从claims中获取的shop_id: {shop_id}")
    
    # 3. 测试商家API
    print("\n3. 测试商家API...")
    test_shop_owner_api(shop_owner_token, shop_id)
    
    # 4. 测试管理员API（应该失败）
    print("\n4. 测试管理员API（应该失败）...")
    admin_url = f"{API_BASE_URL}/admin/shop/list"
    headers = {"Authorization": f"Bearer {shop_owner_token}"}
    
    def admin_request_func():
        return requests.get(admin_url, headers=headers)
    
    admin_response = make_request_with_retry(admin_request_func)
    print(f"管理员API状态码: {admin_response.status_code}")
    print(f"管理员API响应: {admin_response.text}")

if __name__ == "__main__":
    main()