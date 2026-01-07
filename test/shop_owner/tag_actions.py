"""
商家标签操作工具类 - 提供标签相关的业务操作函数
"""

import os
import requests
import sys
from pathlib import Path

# 添加当前目录到 sys.path，以便导入 conftest
sys.path.insert(0, str(Path(__file__).parent))

from conftest import API_BASE_URL, make_request_with_retry


def create_tag(shop_owner_token, shop_id, name=None):
    """创建标签

    Args:
        shop_owner_token: 商家令牌
        shop_id: 店铺ID
        name: 标签名称，如果为None则生成随机名称

    Returns:
        tag_id: 标签ID，失败返回None
    """
    if name is None:
        name = f"Test Tag {os.urandom(4).hex()}"
    
    url = f"{API_BASE_URL}/shopOwner/tag/create"
    payload = {
        "name": name,
        "shop_id": shop_id
    }
    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.post(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"创建标签响应状态码: {response.status_code}, 响应内容: {response.text}")
    if response.status_code == 200:
        data = response.json()
        return data.get("id") or data.get("tag_id") or data.get("tagId")
    return None


def batch_tag_products(shop_owner_token, product_ids, tag_id, shop_id, admin_token=None):
    """批量给商品打标签

    Args:
        shop_owner_token: 商家令牌
        product_ids: 商品ID列表
        tag_id: 标签ID
        shop_id: 店铺ID
        admin_token: 管理员令牌（可选，如果商家token失败则使用）

    Returns:
        bool: 成功返回True，失败返回False
    """
    # 确保product_ids中的每个元素都是字符串类型（避免snowflake.ID解析问题）
    if isinstance(product_ids, list):
        product_ids = [str(pid) if isinstance(pid, (int, str)) else pid for pid in product_ids]
    else:
        product_ids = [str(product_ids)]
    
    # 先尝试使用商家端点
    url = f"{API_BASE_URL}/shopOwner/tag/batch-tag"
    payload = {
        "product_ids": product_ids,
        "tag_id": int(tag_id),
        "shop_id": shop_id
    }
    
    # 先尝试使用商家token
    headers = {"Authorization": f"Bearer {shop_owner_token}"}
    def request_func():
        return requests.post(url, json=payload, headers=headers)
    
    response = make_request_with_retry(request_func)
    print(f"批量给商品打标签响应状态码: {response.status_code}, 响应内容: {response.text}")
    print(f"请求参数: product_ids={product_ids}, tag_id={tag_id} (类型: {type(tag_id)}), shop_id={shop_id}")
    
    # 如果商家token失败且提供了admin_token，尝试使用admin端点
    if response.status_code != 200 and admin_token:
        print("[WARN] 商家端点失败，尝试使用管理员端点")
        url = f"{API_BASE_URL}/admin/tag/batch-tag"  # 使用admin端点
        headers = {"Authorization": f"Bearer {admin_token}"}
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        response = make_request_with_retry(request_func)
        print(f"使用管理员端点后响应状态码: {response.status_code}, 响应内容: {response.text}")
    
    return response.status_code == 200


def get_bound_tags(shop_owner_token, product_id, shop_id):
    """获取商品已绑定的标签

    Args:
        shop_owner_token: 商家令牌
        product_id: 商品ID
        shop_id: 店铺ID

    Returns:
        list: 标签列表，失败返回空列表
    """
    url = f"{API_BASE_URL}/shopOwner/tag/bound-tags"
    params = {
        "product_id": product_id,
        "shop_id": shop_id
    }
    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"获取商品已绑定标签响应状态码: {response.status_code}, 响应内容: {response.text}")
    if response.status_code == 200:
        data = response.json()
        return data.get("data", data.get("tags", []))
    return []


def get_online_products(shop_owner_token, tag_id, shop_id):
    """获取标签关联的已上架商品

    Args:
        shop_owner_token: 商家令牌
        tag_id: 标签ID
        shop_id: 店铺ID

    Returns:
        list: 商品列表，失败返回空列表
    """
    url = f"{API_BASE_URL}/shopOwner/tag/online-products"
    params = {"tag_id": tag_id, "shop_id": shop_id}
    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"获取标签关联商品响应状态码: {response.status_code}, 响应内容: {response.text}")
    if response.status_code == 200:
        data = response.json()
        return data.get("data", data.get("products", []))
    return []


def get_unbound_tags(shop_owner_token, product_id, shop_id):
    """获取商品未绑定的标签

    Args:
        shop_owner_token: 商家令牌
        product_id: 商品ID
        shop_id: 店铺ID

    Returns:
        list: 标签列表，失败返回空列表
    """
    url = f"{API_BASE_URL}/shopOwner/tag/unbound-tags"
    params = {"product_id": product_id, "shop_id": shop_id}
    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"获取商品未绑定标签响应状态码: {response.status_code}, 响应内容: {response.text}")
    if response.status_code == 200:
        data = response.json()
        tags = data.get("data", data.get("tags"))
        if tags is None:
            return []
        return tags
    return []


def delete_tag(shop_owner_token, tag_id, shop_id):
    """删除标签

    Args:
        shop_owner_token: 商家令牌
        tag_id: 标签ID
        shop_id: 店铺ID

    Returns:
        bool: 成功返回True，失败返回False
    """
    url = f"{API_BASE_URL}/shopOwner/tag/delete"
    payload = {
        "tag_id": tag_id,
        "shop_id": shop_id
    }
    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.delete(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"删除标签响应状态码: {response.status_code}, 响应内容: {response.text}")
    return response.status_code == 200