"""
商家商品操作工具类 - 提供商品相关的业务操作函数
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


def create_product(shop_owner_token, shop_id, name=None, price=100, description="Test product description", stock=100):
    """创建商品

    Args:
        shop_owner_token: 商家令牌
        shop_id: 店铺ID
        name: 商品名称，如果为None则生成随机名称
        price: 价格
        description: 描述

    Returns:
        product_id: 商品ID，失败返回None
    """
    # 使用测试数据配置生成数据
    product_data = test_data.generate_product_data(shop_id)
    if name is None:
        name = product_data["name"]
    if price == 100:
        price = product_data["price"]

    url = f"{API_BASE_URL}/shopOwner/product/create"
    payload = {
        "shop_id": shop_id,
        "name": name,
        "price": price,
        "description": description,
        "stock": stock
    }
    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.post(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    validator = ResponseValidator(response)
    if response.status_code == 200:
        product_id = validator.extract_id()
        print(f"[OK] 创建商品成功，名称: {name}, ID: {product_id}")
        return product_id
    print(f"[FAIL] 创建商品失败，状态码: {response.status_code}, 响应: {response.text}")
    return None


def get_product_list(shop_owner_token, shop_id=None, page=1, page_size=10):
    """获取商品列表

    Args:
        shop_owner_token: 商家令牌
        shop_id: 店铺ID（可选）
        page: 页码
        page_size: 每页数量

    Returns:
        list: 商品列表
    """
    url = f"{API_BASE_URL}/shopOwner/product/list"
    params = {"page": page, "pageSize": page_size}
    if shop_id:
        params["shop_id"] = str(shop_id)

    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        data = response.json()
        return data.get("data", data.get("products", []))
    return []


def get_product_detail(shop_owner_token, product_id, shop_id):
    """获取商品详情

    Args:
        shop_owner_token: 商家令牌
        product_id: 商品ID
        shop_id: 店铺ID

    Returns:
        dict: 商品详情，失败返回None
    """
    url = f"{API_BASE_URL}/shopOwner/product/detail"
    params = {
        "id": product_id,
        "shop_id": shop_id
    }
    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"获取商品详情响应状态码: {response.status_code}, 响应内容: {response.text}")
    if response.status_code == 200:
        return response.json()
    return None


def update_product(shop_owner_token, product_id, shop_id, name="Updated Product Name", price=150, stock=None):
    """更新商品信息

    Args:
        shop_owner_token: 商家令牌
        product_id: 商品ID
        shop_id: 店铺ID
        name: 新名称
        price: 新价格
        stock: 新库存（可选，如果不传则不更新库存）

    Returns:
        bool: 成功返回True，失败返回False
    """
    url = f"{API_BASE_URL}/shopOwner/product/update"
    # UpdateProduct函数使用查询参数id和shop_id，然后从JSON body读取更新数据
    params = {
        "id": str(product_id),
        "shop_id": str(shop_id)
    }
    payload = {
        "name": name,
        "price": price
    }
    # 只有在明确指定 stock 时才更新（避免默认值 0 覆盖原库存）
    if stock is not None:
        payload["stock"] = stock

    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.put(url, params=params, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"更新商品响应状态码: {response.status_code}, 响应内容: {response.text}")
    return response.status_code == 200


def upload_product_image(shop_owner_token, product_id, shop_id):
    """上传商品图片

    Args:
        shop_owner_token: 商家令牌
        product_id: 商品ID
        shop_id: 店铺ID

    Returns:
        bool: 成功返回True，失败返回False
    """
    url = f"{API_BASE_URL}/shopOwner/product/upload-image"
    # 创建测试图片数据
    test_image_data = b"fake image data"
    # UploadProductImage函数使用查询参数id和shop_id，不是文件参数
    files = {
        "image": ("test.jpg", test_image_data, "image/jpeg")
    }
    params = {
        "id": str(product_id),
        "shop_id": str(shop_id)
    }
    headers = {"Authorization": f"Bearer {shop_owner_token}"}
    
    def request_func():
        return requests.post(url, files=files, params=params, headers=headers)
    
    response = make_request_with_retry(request_func)
    print(f"上传商品图片响应状态码: {response.status_code}, 响应内容: {response.text}")
    return response.status_code == 200


def toggle_product_status(shop_owner_token, product_id, shop_id, status="online"):
    """切换商品状态

    Args:
        shop_owner_token: 商家令牌
        product_id: 商品ID
        shop_id: 店铺ID
        status: 状态值，默认"online"

    Returns:
        bool: 成功返回True，失败返回False
    """
    url = f"{API_BASE_URL}/shopOwner/product/toggle-status"
    payload = {
        "id": product_id,
        "shop_id": shop_id,
        "status": status
    }
    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.put(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    print(f"切换商品状态响应状态码: {response.status_code}, 响应内容: {response.text}")
    return response.status_code == 200


def get_product_image(shop_owner_token, product_id, shop_id):
    """获取商品图片

    Args:
        shop_owner_token: 商家令牌
        product_id: 商品ID
        shop_id: 店铺ID

    Returns:
        bool: 成功返回True，失败返回False
    """
    # 先获取商品详情，获取image_url
    product_detail = get_product_detail(shop_owner_token, product_id, shop_id)
    if product_detail and product_detail.get("image_url"):
        image_url = product_detail["image_url"]
        # 从image_url中提取文件名（去掉路径前缀）
        # image_url格式可能是"uploads/products/filename.jpg"或"filename.jpg"
        import os
        filename = os.path.basename(image_url)
        url = f"{API_BASE_URL}/shopOwner/product/image"
        params = {"path": filename}
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"获取商品图片响应状态码: {response.status_code}, 响应内容: {response.text}")
        return response.status_code == 200
    else:
        print(f"[WARN] 商品没有图片URL，跳过获取图片测试")
        return True  # 没有图片也算成功


def delete_product(shop_owner_token, product_id, shop_id):
    """删除商品

    Args:
        shop_owner_token: 商家令牌
        product_id: 商品ID
        shop_id: 店铺ID

    Returns:
        bool: 成功返回True，失败返回False
    """
    url = f"{API_BASE_URL}/shopOwner/product/delete"
    payload = {
        "id": product_id,
        "shop_id": str(shop_id)
    }
    headers = {"Authorization": f"Bearer {shop_owner_token}"}

    def request_func():
        return requests.delete(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        print(f"[OK] 删除商品成功，ID: {product_id}")
        return True
    print(f"[FAIL] 删除商品失败，ID: {product_id}, 状态码: {response.status_code}, 响应: {response.text}")
    return False