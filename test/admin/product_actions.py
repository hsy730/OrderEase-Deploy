"""
商品操作工具类 - 提供商品相关的业务操作函数
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


def create_product(admin_token, shop_id, name=None, price=100, description=None, stock=None):
    """创建商品

    Args:
        admin_token: 管理员令牌
        shop_id: 店铺ID
        name: 商品名称
        price: 商品价格
        description: 商品描述
        stock: 商品库存

    Returns:
        product_id: 商品ID，失败返回None
    """
    # 如果没有提供名称，使用测试数据配置生成
    if not name:
        product_data = test_data.generate_product_data(shop_id)
        name = product_data["name"]
        description = description or product_data["description"]
        price = price or product_data["price"]
        stock = stock if stock is not None else product_data["stock"]
    else:
        if stock is None:
            stock = 100

    url = f"{API_BASE_URL}/admin/product/create"
    payload = {
        "shop_id": str(shop_id),
        "name": name,
        "price": price,
        "description": description,
        "stock": stock
    }

    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.post(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)

    if response.status_code == 200:
        # 使用 ResponseValidator 提取 ID
        validator = ResponseValidator(response)
        product_id = validator.extract_id()
        if product_id:
            # 验证返回的商品名称是否匹配
            try:
                data = response.json()
                product_response = data.get("data", data)
                returned_name = product_response.get("name") or product_response.get("Name")
                if returned_name and returned_name == name:
                    print(f"✓ 创建商品成功，ID: {product_id}, 名称: {returned_name}")
                else:
                    print(f"⚠ 创建商品成功但名称不匹配，期望: {name}, 返回: {returned_name}")
            except:
                print(f"✓ 创建商品成功，ID: {product_id}")
            return product_id
        else:
            print(f"⚠ 创建商品成功但无法提取ID，响应: {response.text}")
            return None
    else:
        print(f"✗ 创建商品失败，状态码: {response.status_code}, 响应: {response.text}")
        return None


def get_product_list(admin_token, shop_id=None, page=1, page_size=10):
    """获取商品列表

    Args:
        admin_token: 管理员令牌
        shop_id: 店铺ID（可选）
        page: 页码
        page_size: 每页数量

    Returns:
        list: 商品列表
    """
    url = f"{API_BASE_URL}/admin/product/list"
    params = {"page": page, "pageSize": page_size}
    if shop_id:
        params["shop_id"] = str(shop_id)

    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)

    if response.status_code == 200:
        data = response.json()
        products = data.get("data", data.get("products", []))
        print(f"✓ 获取商品列表成功，数量: {len(products) if isinstance(products, list) else 0}")
        return products
    else:
        print(f"✗ 获取商品列表失败，状态码: {response.status_code}, 响应: {response.text}")
        return []


def get_product_detail(admin_token, product_id, shop_id):
    """获取商品详情

    Args:
        admin_token: 管理员令牌
        product_id: 商品ID
        shop_id: 店铺ID

    Returns:
        dict: 商品详情，失败返回None
    """
    url = f"{API_BASE_URL}/admin/product/detail"
    params = {"id": product_id, "shop_id": shop_id}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)

    if response.status_code == 200:
        json_data = response.json()
        print(f"获取商品详情响应数据: {json_data}")
        # 处理不同的响应格式
        if isinstance(json_data, dict):
            result = json_data.get("data")
            if result:
                print(f"✓ 获取商品详情成功: {result.get('name') if isinstance(result, dict) else result}")
                return result
            # 如果响应直接包含id字段，直接返回整个对象
            elif "id" in json_data:
                print(f"✓ 获取商品详情成功（直接格式）: {json_data.get('name')}")
                return json_data
        elif isinstance(json_data, list) and len(json_data) > 0:
            print(f"✓ 获取商品详情成功: {json_data[0]}")
            return json_data[0]
    else:
        print(f"✗ 获取商品详情失败，状态码: {response.status_code}, 响应: {response.text}")
    return None


def update_product(admin_token, product_id, shop_id, name=None, price=None):
    """更新商品信息

    Args:
        admin_token: 管理员令牌
        product_id: 商品ID
        shop_id: 店铺ID
        name: 新的商品名称
        price: 新的商品价格

    Returns:
        bool: 是否更新成功
    """
    url = f"{API_BASE_URL}/admin/product/update"
    params = {"id": product_id, "shop_id": shop_id}
    payload = {}
    if name:
        payload["name"] = name
    if price:
        payload["price"] = price

    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.put(url, params=params, json=payload, headers=headers)

    response = make_request_with_retry(request_func)

    if response.status_code == 200:
        print(f"✓ 更新商品成功，ID: {product_id}")
        return True
    else:
        print(f"✗ 更新商品失败，ID: {product_id}, 状态码: {response.status_code}, 响应: {response.text}")
        return False


def delete_product(admin_token, product_id, shop_id):
    """删除商品

    Args:
        admin_token: 管理员令牌
        product_id: 商品ID
        shop_id: 店铺ID

    Returns:
        bool: 是否删除成功
    """
    url = f"{API_BASE_URL}/admin/product/delete"
    params = {"id": product_id, "shop_id": shop_id}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.delete(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)

    if response.status_code == 200:
        print(f"✓ 删除商品成功，ID: {product_id}")
        return True
    else:
        print(f"✗ 删除商品失败，ID: {product_id}, 状态码: {response.status_code}, 响应: {response.text}")
        return False


def upload_product_image(admin_token, product_id, shop_id, image_data=None):
    """上传商品图片

    Args:
        admin_token: 管理员令牌
        product_id: 商品ID
        shop_id: 店铺ID
        image_data: 图片数据，默认为测试假数据

    Returns:
        str: 图片URL，失败返回None
    """
    if image_data is None:
        image_data = b"fake image data"

    url = f"{API_BASE_URL}/admin/product/upload-image"
    params = {"id": product_id, "shop_id": shop_id}
    files = {"image": ("test.jpg", image_data, "image/jpeg")}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.post(url, params=params, files=files, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        response_data = response.json()
        print(f"上传商品图片成功，响应内容: {response_data}")
        return response_data.get("url")
    print(f"上传商品图片失败，状态码: {response.status_code}, 响应内容: {response.text}")
    return None


def get_product_image(admin_token, image_path, shop_id):
    """获取商品图片

    Args:
        admin_token: 管理员令牌
        image_path: 图片路径
        shop_id: 店铺ID

    Returns:
        bool: 是否获取成功
    """
    url = f"{API_BASE_URL}/admin/product/image"
    params = {"path": image_path, "shop_id": shop_id}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    return response.status_code == 200


def toggle_product_status(admin_token, product_id, shop_id, status="online"):
    """切换商品状态

    Args:
        admin_token: 管理员令牌
        product_id: 商品ID
        shop_id: 店铺ID
        status: 状态（online/offline）

    Returns:
        bool: 是否切换成功
    """
    url = f"{API_BASE_URL}/admin/product/toggle-status"
    payload = {
        "id": str(product_id),
        "status": status,
        "shop_id": shop_id
    }
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.put(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    return response.status_code == 200
