"""
标签操作工具类 - 提供标签相关的业务操作函数
"""

import os
import requests
import sys
from pathlib import Path

# 添加当前目录到 sys.path，以便导入 conftest
sys.path.insert(0, str(Path(__file__).parent))

from conftest import API_BASE_URL, make_request_with_retry


def create_tag(admin_token, name=None, shop_id=1):
    """创建标签

    Args:
        admin_token: 管理员令牌
        name: 标签名称
        shop_id: 店铺ID

    Returns:
        tag_id: 标签ID，失败返回None
    """
    if not name:
        name = f"Test Tag {os.urandom(4).hex()}"

    url = f"{API_BASE_URL}/admin/tag/create"
    payload = {
        "name": name,
        "shop_id": shop_id
    }
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.post(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"创建标签响应码: {response.status_code}，响应内容: {response.text}")
    if response.status_code == 200:
        data = response.json()
        return data.get("id") or data.get("tag_id") or data.get("tagId")
    return None


def batch_tag_products(admin_token, product_ids, tag_ids):
    """批量给商品打标签

    Args:
        admin_token: 管理员令牌
        product_ids: 商品ID列表
        tag_ids: 标签ID列表

    Returns:
        bool: 是否打标签成功
    """
    url = f"{API_BASE_URL}/admin/tag/batch-tag"
    payload = {
        "product_ids": product_ids,
        "tag_ids": tag_ids
    }
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.post(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"批量打标签响应码: {response.status_code}，响应内容: {response.text}")
    return response.status_code == 200


def get_bound_tags(admin_token, product_id, shop_id):
    """获取商品已绑定的标签

    Args:
        admin_token: 管理员令牌
        product_id: 商品ID
        shop_id: 店铺ID

    Returns:
        list: 已绑定的标签列表
    """
    url = f"{API_BASE_URL}/admin/tag/bound-tags"
    params = {"product_id": product_id, "shop_id": shop_id}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []


def get_online_products(admin_token, tag_id, shop_id):
    """获取标签关联的已上架商品

    Args:
        admin_token: 管理员令牌
        tag_id: 标签ID
        shop_id: 店铺ID

    Returns:
        list: 商品列表
    """
    url = f"{API_BASE_URL}/admin/tag/online-products"
    params = {"tag_id": tag_id, "shop_id": shop_id}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []


def get_unbound_tags(admin_token, product_id, shop_id):
    """获取商品未绑定的标签

    Args:
        admin_token: 管理员令牌
        product_id: 商品ID
        shop_id: 店铺ID

    Returns:
        list: 未绑定的标签列表
    """
    url = f"{API_BASE_URL}/admin/tag/unbound-tags"
    params = {"product_id": product_id, "shop_id": shop_id}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []
