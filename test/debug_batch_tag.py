"""
调试批量给商品打标签的JSON序列化问题
"""
import os
import sys
import requests
import json
from pathlib import Path

# 添加当前目录到 sys.path
sys.path.insert(0, str(Path(__file__).parent))

from conftest import API_BASE_URL, make_request_with_retry

def main():
    # 获取管理员token
    login_url = f"{API_BASE_URL}/login"
    login_payload = {
        "username": "admin",
        "password": "Admin@123456"
    }
    login_response = requests.post(login_url, json=login_payload)
    if login_response.status_code != 200:
        print(f"管理员登录失败: {login_response.status_code}, {login_response.text}")
        return
    admin_token = login_response.json().get("token", "")
    print(f"[OK] 管理员登录成功")

    # 创建店铺
    unique_suffix = os.urandom(4).hex()
    owner_username = f"shop_owner_{unique_suffix}"
    shop_url = f"{API_BASE_URL}/admin/shop/create"
    shop_payload = {
        "name": f"Test Shop {unique_suffix}",
        "owner_username": owner_username,
        "owner_password": "Admin@123456",
        "contact_phone": "13800138000",
        "contact_email": f"test_{unique_suffix}@example.com",
        "description": "Test shop description",
        "valid_until": "2027-12-31T23:59:59Z"
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    shop_response = requests.post(shop_url, json=shop_payload, headers=headers)
    if shop_response.status_code != 200:
        print(f"创建店铺失败: {shop_response.status_code}, {shop_response.text}")
        return
    shop_data = shop_response.json()
    shop_id = shop_data.get("id") or shop_data.get("data", {}).get("id")
    print(f"[OK] 创建店铺成功，ID: {shop_id}")

    # 获取店主token
    time.sleep(2)
    login_url = f"{API_BASE_URL}/login"
    login_payload = {
        "username": owner_username,
        "password": "Admin@123456"
    }
    login_response = requests.post(login_url, json=login_payload)
    if login_response.status_code != 200:
        print(f"店主登录失败: {login_response.status_code}, {login_response.text}")
        return
    shop_owner_token = login_response.json().get("token", "")
    print(f"[OK] 店主登录成功")

    # 创建商品
    product_url = f"{API_BASE_URL}/admin/product/create"
    product_payload = {
        "shop_id": shop_id,
        "name": f"Test Product {unique_suffix}",
        "description": "Test product description",
        "price": 100,
        "stock": 100
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    product_response = requests.post(product_url, json=product_payload, headers=headers)
    if product_response.status_code != 200:
        print(f"创建商品失败: {product_response.status_code}, {product_response.text}")
        return
    product_data = product_response.json()
    product_id = product_data.get("id") or product_data.get("data", {}).get("id")
    print(f"[OK] 创建商品成功，ID: {product_id}, 类型: {type(product_id)}")

    # 创建标签
    tag_url = f"{API_BASE_URL}/shopOwner/tag/create"
    tag_payload = {
        "name": f"Test Tag {unique_suffix}",
        "shop_id": shop_id
    }
    headers = {"Authorization": f"Bearer {shop_owner_token}"}
    tag_response = requests.post(tag_url, json=tag_payload, headers=headers)
    if tag_response.status_code != 200:
        print(f"创建标签失败: {tag_response.status_code}, {tag_response.text}")
        return
    tag_data = tag_response.json()
    tag_id = tag_data.get("id") or tag_data.get("data", {}).get("id")
    print(f"[OK] 创建标签成功，ID: {tag_id}")

    # 测试批量给商品打标签 - 使用整数类型
    print("\n===== 测试批量给商品打标签（整数类型） =====")
    batch_url = f"{API_BASE_URL}/shopOwner/tag/batch-tag"
    
    # 方法1：直接使用整数类型的product_id
    print(f"product_id原始值: {product_id}, 类型: {type(product_id)}")
    print(f"product_id转int: {int(product_id)}, 类型: {type(int(product_id))}")
    
    payload1 = {
        "product_ids": [int(product_id)],  # 确保是整数类型
        "tag_id": int(tag_id),
        "shop_id": shop_id
    }
    print(f"请求payload: {json.dumps(payload1, indent=2)}")
    print(f"product_ids类型: {type(payload1['product_ids'])}")
    print(f"product_ids[0]类型: {type(payload1['product_ids'][0])}")
    
    headers = {"Authorization": f"Bearer {shop_owner_token}"}
    batch_response = requests.post(batch_url, json=payload1, headers=headers)
    print(f"响应状态码: {batch_response.status_code}")
    print(f"响应内容: {batch_response.text}")

    # 方法2：使用管理员token
    print("\n===== 测试批量给商品打标签（管理员token） =====")
    headers = {"Authorization": f"Bearer {admin_token}"}
    batch_response = requests.post(batch_url, json=payload1, headers=headers)
    print(f"响应状态码: {batch_response.status_code}")
    print(f"响应内容: {batch_response.text}")

if __name__ == "__main__":
    import time
    main()
