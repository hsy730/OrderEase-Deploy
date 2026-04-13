"""
标签操作工具类 - 提供标签相关的业务操作函数
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


def create_tag(admin_token, name=None, shop_id="1"):
    """创建标签

    Args:
        admin_token: 管理员令牌
        name: 标签名称
        shop_id: 店铺ID

    Returns:
        tag_id: 标签ID，失败返回None
    """
    # 如果没有提供名称，使用测试数据配置生成
    if not name:
        tag_data = test_data.generate_tag_data(shop_id)
        name = tag_data["name"]

    url = f"{API_BASE_URL}/admin/tag/create"
    payload = {
        "name": name,
        "shop_id": str(shop_id)
    }
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.post(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)

    if response.status_code == 200:
        # 使用 ResponseValidator 提取 ID
        validator = ResponseValidator(response)
        tag_id = validator.extract_id()
        if tag_id:
            # 验证返回的标签名称是否匹配
            try:
                data = response.json()
                tag_response = data.get("data", data)
                returned_name = tag_response.get("name") or tag_response.get("Name")
                if returned_name and returned_name == name:
                    print(f"[OK] 创建标签成功，ID: {tag_id}, 名称: {returned_name}")
                else:
                    print(f"[WARN] 创建标签成功但名称不匹配，期望: {name}, 返回: {returned_name}")
            except:
                print(f"[OK] 创建标签成功，ID: {tag_id}")
            return tag_id
        else:
            print(f"[WARN] 创建标签成功但无法提取ID，响应: {response.text}")
            return None
    else:
        print(f"[FAIL] 创建标签失败，状态码: {response.status_code}, 响应: {response.text}")
        return None


def batch_tag_products(admin_token, product_ids, tag_id, shop_id):
    """批量给商品打标签

    Args:
        admin_token: 管理员令牌
        product_ids: 商品ID列表
        tag_id: 标签ID（单个）
        shop_id: 店铺ID

    Returns:
        bool: 是否打标签成功
    """
    url = f"{API_BASE_URL}/admin/tag/batch-tag"
    payload = {
        "product_ids": product_ids,
        "tag_id": tag_id,
        "shop_id": str(shop_id)
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
    params = {"product_id": product_id, "shop_id": str(shop_id)}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        data = response.json()
        # 响应格式: {"product_id": "xxx", "tags": [...]}
        return data.get("tags", [])
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
    params = {"tag_id": tag_id, "shop_id": str(shop_id)}
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
    params = {"product_id": product_id, "shop_id": str(shop_id)}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []


def get_tag_list(admin_token, shop_id=None, page=1, page_size=10):
    """获取标签列表

    Args:
        admin_token: 管理员令牌
        shop_id: 店铺ID（可选，如果提供则只返回该店铺的标签）
        page: 页码
        page_size: 每页数量

    Returns:
        list: 标签列表
    """
    url = f"{API_BASE_URL}/admin/tag/list"
    params = {"page": page, "pageSize": page_size}
    if shop_id:
        params["shop_id"] = str(shop_id)
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)

    if response.status_code == 200:
        data = response.json()
        # 处理不同的响应格式
        # 格式1: {"tags": [...], "total": 1}
        # 格式2: {"data": [...]}
        # 格式3: [...]
        if isinstance(data, dict):
            tags = data.get("tags", data.get("data", []))
        elif isinstance(data, list):
            tags = data
        else:
            tags = []
        print(f"[OK] 获取标签列表成功，数量: {len(tags) if isinstance(tags, list) else 0}")
        return tags
    else:
        print(f"[FAIL] 获取标签列表失败，状态码: {response.status_code}, 响应: {response.text}")
        return []


def get_tag_detail(admin_token, tag_id):
    """获取标签详情

    Args:
        admin_token: 管理员令牌
        tag_id: 标签ID

    Returns:
        dict: 标签详情，失败返回None
    """
    url = f"{API_BASE_URL}/admin/tag/detail"
    params = {"tagId": tag_id}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        return response.json().get("data")
    return None


def update_tag(admin_token, tag_id, name=None, shop_id=None):
    """更新标签信息

    Args:
        admin_token: 管理员令牌
        tag_id: 标签ID
        name: 新的标签名称
        shop_id: 店铺ID（必需）

    Returns:
        bool: 是否更新成功
    """
    url = f"{API_BASE_URL}/admin/tag/update"
    payload = {"id": tag_id}
    if name:
        payload["name"] = name
    if shop_id:
        payload["shop_id"] = str(shop_id)

    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.put(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)

    if response.status_code == 200:
        print(f"[OK] 更新标签成功，ID: {tag_id}")
        return True
    else:
        print(f"[FAIL] 更新标签失败，ID: {tag_id}, 状态码: {response.status_code}, 响应: {response.text}")
        return False


def delete_tag(admin_token, tag_id, shop_id=None):
    """删除标签

    Args:
        admin_token: 管理员令牌
        tag_id: 标签ID
        shop_id: 店铺ID（可选）

    Returns:
        bool: 是否删除成功
    """
    url = f"{API_BASE_URL}/admin/tag/delete"
    params = {"id": tag_id}
    if shop_id:
        params["shop_id"] = str(shop_id)
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.delete(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)

    if response.status_code == 200:
        print(f"[OK] 删除标签成功，ID: {tag_id}")
        return True
    else:
        print(f"[FAIL] 删除标签失败，ID: {tag_id}, 状态码: {response.status_code}, 响应: {response.text}")
        return False


def batch_tag_product(admin_token, product_id, tag_ids):
    """批量设置商品标签

    Args:
        admin_token: 管理员令牌
        product_id: 商品ID
        tag_ids: 标签ID列表

    Returns:
        bool: 是否设置成功
    """
    url = f"{API_BASE_URL}/admin/tag/batch-tag-product"
    payload = {
        "product_id": product_id,
        "tag_ids": tag_ids
    }
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.post(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"批量设置商品标签响应码: {response.status_code}，响应内容: {response.text}")
    return response.status_code == 200


def batch_untag_products(admin_token, product_ids, tag_ids):
    """批量解绑商品标签

    Args:
        admin_token: 管理员令牌
        product_ids: 商品ID列表
        tag_ids: 标签ID列表

    Returns:
        bool: 是否解绑成功
    """
    url = f"{API_BASE_URL}/admin/tag/batch-untag"
    payload = {
        "product_ids": product_ids,
        "tag_ids": tag_ids
    }
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.delete(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"批量解绑商品标签响应码: {response.status_code}，响应内容: {response.text}")
    return response.status_code == 200


def get_unbound_tags_list(admin_token):
    """获取没有绑定商品的标签列表

    Args:
        admin_token: 管理员令牌

    Returns:
        list: 未绑定商品的标签列表
    """
    url = f"{API_BASE_URL}/admin/tag/unbound-list"
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []


def get_unbound_products_for_tag(admin_token, tag_id):
    """获取标签未绑定的商品列表

    Args:
        admin_token: 管理员令牌
        tag_id: 标签ID

    Returns:
        list: 未绑定的商品列表
    """
    url = f"{API_BASE_URL}/admin/tag/unbound-products"
    params = {"tagId": tag_id}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []


def get_tag_bound_products(admin_token, tag_id, shop_id):
    """获取标签已绑定的商品列表（管理端）

    Args:
        admin_token: 管理员令牌
        tag_id: 标签ID
        shop_id: 店铺ID

    Returns:
        list: 已绑定的商品列表
    """
    url = f"{API_BASE_URL}/admin/tag/bound-products"
    params = {"tag_id": tag_id, "shop_id": str(shop_id)}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []


def get_tag_bound_products_frontend(frontend_token, tag_id, shop_id):
    """获取标签已绑定的商品列表（客户端）

    Args:
        frontend_token: 前端用户令牌
        tag_id: 标签ID
        shop_id: 店铺ID

    Returns:
        list: 已绑定的商品列表（仅 online 状态）
    """
    url = f"{API_BASE_URL}/tag/bound-products"
    params = {"tag_id": tag_id, "shop_id": str(shop_id)}
    headers = {"Authorization": f"Bearer {frontend_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []
