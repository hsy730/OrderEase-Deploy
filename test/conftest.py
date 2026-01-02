import os
import pytest
import requests
import time
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080/api/order-ease/v1")

def make_request_with_retry(request_func, max_retries=3):
    """执行请求，如果遇到429则等待0.5秒后重试"""
    retry_count = 0
    while True:
        response = request_func()
        if response.status_code == 429 and retry_count < max_retries:
            time.sleep(0.2)
            retry_count += 1
        else:
            return response

def assert_response_status(response, expected_status, message=None):
    """断言响应状态码，失败时打印详细信息"""
    if message is None:
        message = f"Expected {expected_status}, got {response.status_code}"
    
    if response.status_code not in expected_status if isinstance(expected_status, list) else response.status_code != expected_status:
        error_details = {
            "status_code": response.status_code,
            "expected_status": expected_status,
            "response_body": response.text,
            "url": response.url if hasattr(response, 'url') else 'N/A'
        }
        pytest.fail(f"{message}\n\nResponse Details:\n{error_details}")
    
    return response

@pytest.fixture(scope="session")
def api_base_url():
    """API 基础 URL fixture"""
    return API_BASE_URL

@pytest.fixture(scope="session")
def admin_token():
    """管理员令牌 fixture - 通过登录获取真实token"""
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

@pytest.fixture(scope="session")
def shop_owner_token():
    """商家令牌 fixture - 通过登录获取真实token"""
    url = f"{API_BASE_URL}/login"
    payload = {
        "username": "shop1",
        "password": "Admin@123456"
    }
    
    def request_func():
        return requests.post(url, json=payload)
    
    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        data = response.json()
        return data.get("token", "")
    return ""

@pytest.fixture(scope="session")
def user_token():
    """用户令牌 fixture - 通过登录获取真实token"""
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

@pytest.fixture(scope="session")
def test_token():
    """测试令牌 fixture (已废弃，使用admin_token、shop_owner_token或user_token)"""
    return "test_token"

@pytest.fixture(scope="session")
def http_client():
    """HTTP 客户端 fixture"""
    return requests.Session()

@pytest.fixture(scope="session")
def test_shop_id(admin_token):
    """测试店铺ID fixture - 从数据库获取第一个店铺ID"""
    url = f"{API_BASE_URL}/admin/shop/list"
    params = {
        "page": 1,
        "pageSize": 1
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    def request_func():
        return requests.get(url, params=params, headers=headers)
    
    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        data = response.json()
        shops = data.get("data", data.get("shops", []))
        if shops and len(shops) > 0:
            return shops[0].get("id")
    return None

@pytest.fixture(scope="session")
def test_product_id(admin_token, test_shop_id):
    """测试商品ID fixture - 从数据库获取第一个商品ID"""
    url = f"{API_BASE_URL}/admin/product/list"
    params = {
        "page": 1,
        "pageSize": 1,
        "shop_id": str(test_shop_id)
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    def request_func():
        return requests.get(url, params=params, headers=headers)
    
    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        data = response.json()
        products = data.get("data", data.get("products", []))
        if products and len(products) > 0:
            return products[0].get("id")
    return None

@pytest.fixture(scope="session")
def test_user_id(admin_token):
    """测试用户ID fixture - 从数据库获取第一个用户ID"""
    url = f"{API_BASE_URL}/admin/user/list"
    params = {
        "page": 1,
        "pageSize": 1
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    def request_func():
        return requests.get(url, params=params, headers=headers)
    
    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        data = response.json()
        users = data.get("data", data.get("users", []))
        if users and len(users) > 0:
            return str(users[0].get("id"))
    return None

@pytest.fixture(scope="session")
def shop_owner_shop_id(admin_token):
    """商家店铺ID fixture - 从数据库获取商家的店铺ID"""
    url = f"{API_BASE_URL}/admin/shop/list"
    params = {
        "page": 1,
        "pageSize": 10
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    def request_func():
        return requests.get(url, params=params, headers=headers)
    
    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        data = response.json()
        shops = data.get("data", data.get("shops", []))
        if shops and len(shops) > 0:
            for shop in shops:
                if shop.get("owner_username") == "shop1":
                    return shop.get("id")
    return None

@pytest.fixture(scope="session")
def shop_owner_user_id(admin_token):
    """商家用户ID fixture - 从数据库获取第一个用户ID"""
    url = f"{API_BASE_URL}/admin/user/list"
    params = {
        "page": 1,
        "pageSize": 1
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    def request_func():
        return requests.get(url, params=params, headers=headers)
    
    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        data = response.json()
        users = data.get("data", data.get("users", []))
        if users and len(users) > 0:
            return users[0].get("id")
    return None

@pytest.fixture(scope="session")
def shop_owner_product_id(admin_token, shop_owner_shop_id):
    """商家商品ID fixture - 从数据库获取第一个商品ID"""
    url = f"{API_BASE_URL}/admin/product/list"
    params = {
        "page": 1,
        "pageSize": 1,
        "shop_id": str(shop_owner_shop_id)
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    def request_func():
        return requests.get(url, params=params, headers=headers)
    
    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        data = response.json()
        products = data.get("data", data.get("products", []))
        if products and len(products) > 0:
            return products[0].get("id")
    return None

@pytest.fixture(scope="session")
def test_tag_id(admin_token, test_shop_id):
    """测试标签ID fixture - 从数据库获取第一个标签ID"""
    url = f"{API_BASE_URL}/admin/tag/list"
    params = {
        "page": 1,
        "pageSize": 1
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    def request_func():
        return requests.get(url, params=params, headers=headers)
    
    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        data = response.json()
        tags = data.get("data", data.get("tags", []))
        if tags and len(tags) > 0:
            return tags[0].get("id")
    return None

@pytest.fixture(scope="session")
def test_order_id(admin_token, test_shop_id):
    """测试订单ID fixture - 从数据库获取第一个订单ID"""
    url = f"{API_BASE_URL}/admin/order/list"
    params = {
        "page": 1,
        "pageSize": 1,
        "shop_id": str(test_shop_id)
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    def request_func():
        return requests.get(url, params=params, headers=headers)
    
    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        data = response.json()
        orders = data.get("data", data.get("orders", []))
        if orders and len(orders) > 0:
            return orders[0].get("id")
    return None

@pytest.fixture(scope="session")
def shop_owner_order_id(shop_owner_token, shop_owner_shop_id, shop_owner_user_id, shop_owner_product_id):
    """商家订单ID fixture - 创建测试订单"""
    if not shop_owner_shop_id or not shop_owner_user_id or not shop_owner_product_id:
        return None
        
    url = f"{API_BASE_URL}/shopOwner/order/create"
    payload = {
        "shop_id": int(shop_owner_shop_id),
        "user_id": str(shop_owner_user_id),
        "items": [
            {
                "product_id": str(shop_owner_product_id),
                "quantity": 1,
                "price": 100
            }
        ]
    }
    headers = {"Authorization": f"Bearer {shop_owner_token}"}
    
    def request_func():
        return requests.post(url, json=payload, headers=headers)
    
    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        data = response.json()
        return data.get("order_id") or data.get("id")
    return None

@pytest.fixture(scope="session")
def shop_owner_tag_id(shop_owner_token, shop_owner_shop_id):
    """商家标签ID fixture - 创建测试标签"""
    if not shop_owner_shop_id:
        return None
        
    url = f"{API_BASE_URL}/shopOwner/tag/create"
    payload = {
        "name": "Test Tag",
        "shop_id": shop_owner_shop_id
    }
    headers = {"Authorization": f"Bearer {shop_owner_token}"}
    
    def request_func():
        return requests.post(url, json=payload, headers=headers)
    
    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        data = response.json()
        return data.get("id") or data.get("tag_id") or data.get("tagId")
    return None
