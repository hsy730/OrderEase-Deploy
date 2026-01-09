import os
import pytest
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080/api/order-ease/v1")

def make_request_with_retry(request_func, max_retries=10, initial_wait=1, backoff_factor=2):
    """
    执行请求，如果遇到429则等待后重试（最多重试max_retries次）
    
    Args:
        request_func: 请求函数
        max_retries: 最大重试次数
        initial_wait: 初始等待时间（秒）
        backoff_factor: 退避因子，每次重试等待时间乘以这个因子
    """
    retry_count = 0
    wait_time = initial_wait
    
    while True:
        response = request_func()
        if response.status_code == 429 and retry_count < max_retries:
            print(f"[WARN] 请求过于频繁（429），等待 {wait_time} 秒后重试（第 {retry_count + 1}/{max_retries} 次）")
            time.sleep(wait_time)
            retry_count += 1
            wait_time *= backoff_factor  # 指数退避
        else:
            if retry_count > 0:
                print(f"[OK] 重试完成，最终状态码: {response.status_code}")
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
    """商家令牌 fixture - 动态创建店铺并获取token"""
    import os
    import time
    
    # 先获取admin token
    admin_url = f"{API_BASE_URL}/login"
    admin_payload = {
        "username": "admin",
        "password": "Admin@123456"
    }
    
    def admin_request_func():
        return requests.post(admin_url, json=admin_payload)
    
    admin_response = make_request_with_retry(admin_request_func)
    if admin_response.status_code != 200:
        print(f"管理员登录失败: {admin_response.status_code}, {admin_response.text}")
        return ""

    admin_data = admin_response.json()
    admin_token_value = admin_data.get("token", "")
    if not admin_token_value:
        print("未能获取管理员token")
        return ""
    
    # 生成唯一的店主用户名
    unique_suffix = os.urandom(4).hex()
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
    shop_headers = {"Authorization": f"Bearer {admin_token_value}"}
    
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
    """测试商品ID fixture - 从数据库获取第一个商品ID，如果不存在则创建"""
    import os
    
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
    
    # 如果商品不存在，创建一个测试商品
    print(f"店铺 {test_shop_id} 中没有商品，创建测试商品")
    url = f"{API_BASE_URL}/admin/product/create"
    unique_suffix = os.urandom(4).hex()
    payload = {
        "shop_id": int(test_shop_id),
        "name": f"Test Product {unique_suffix}",
        "price": 100,
        "description": "Product created for testing",
        "stock": 100
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    def create_request_func():
        return requests.post(url, json=payload, headers=headers)
    
    create_response = make_request_with_retry(create_request_func)
    if create_response.status_code == 200:
        product_data = create_response.json()
        product_id = product_data.get("id") or product_data.get("product_id")
        print(f"成功创建测试商品，ID: {product_id}")
        return product_id
    
    print(f"创建测试商品失败: {create_response.status_code}, {create_response.text}")
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
    """商家店铺ID fixture - 获取第一个店铺ID"""
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
            # 返回最后一个店铺（刚创建的店铺）
            shop_id = shops[-1].get("id")
            print(f"获取到店铺ID: {shop_id}")
            return shop_id
    print("未能获取店铺ID")
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

@pytest.fixture(scope="function")
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
    # 使用随机生成的标签名，避免唯一约束冲突
    import random
    tag_name = f"Test Tag {random.randint(1000, 9999)}"
    payload = {
        "name": tag_name,
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


def pytest_collection_modifyitems(config, items):
    """
    调整测试执行顺序，确保测试按正确的业务顺序执行
    
    优先级顺序：
    1. 前端测试 (test_frontend_flow.py) - 需要有效的admin_token
    2. 商家业务流程测试 (test_business_flow.py) - 需要有效的admin_token和shop_owner_token
    3. 管理员业务流程测试 (admin/test_business_flow.py) - 需要有效的admin_token
    4. 认证测试 (test_auth_flow.py) - 会登出token，放在最后
    5. 未授权访问测试 (test_unauthorized.py) - 不依赖token，可以放在最后
    
    对于认证测试内部，确保按正确的业务顺序执行：
    1. 管理员登录
    2. 商家登录
    3. 刷新管理员令牌
    4. 刷新商家令牌
    5. 管理员登出
    6. 商家登出
    7. 临时令牌获取
    """
    # 定义文件优先级映射，数值越小优先级越高
    file_priority_map = {
        "test_frontend_flow.py": 0,           # 最先执行 - 前端业务流程
        "shop_owner/test_business_flow.py": 10, # 商家业务流程
        "admin/test_business_flow.py": 20,    # 管理员业务流程
        "test_auth_flow.py": 100,             # 最后执行 - 会登出token
        "test_unauthorized.py": 110,          # 最后执行 - 不依赖token
        "test_password_change_final.py": 120, # 最后执行 - 独立密码修改测试
        "test_shop_owner_password_change.py": 140  # 最后执行 - 独立密码修改测试
    }
    
    # 定义认证测试内部方法优先级映射
    auth_test_priority_map = {
        "test_universal_login_admin": 0,
        "test_universal_login_shop_owner": 1,
        "test_refresh_admin_token": 2,
        "test_refresh_shop_token": 3,
        "test_admin_logout": 4,
        "test_shop_owner_logout": 5,
        "test_get_temp_token": 6,
    }
    
    def get_test_priority(item):
        """获取测试项的优先级"""
        # 获取文件名
        file_path = str(item.fspath)
        
        # 获取测试方法名
        test_name = item.name
        
        # 首先按文件优先级排序
        file_priority = 50  # 默认优先级
        for filename, priority in file_priority_map.items():
            if filename in file_path:
                file_priority = priority
                break
        
        # 如果是认证测试，再按方法优先级排序
        if "test_auth_flow.py" in file_path and test_name in auth_test_priority_map:
            method_priority = auth_test_priority_map[test_name]
            # 组合优先级：文件优先级 + 方法优先级/1000
            return file_priority + method_priority / 1000.0
        
        return file_priority
    
    # 按优先级排序
    items.sort(key=get_test_priority)
    
    # 打印排序后的测试顺序（调试用）
    print("\n" + "="*80)
    print("测试执行顺序（按优先级排序）：")
    for i, item in enumerate(items[:15]):  # 显示前15个
        priority = get_test_priority(item)
        print(f"{i+1}. [{priority:.3f}] {item.nodeid}")
    if len(items) > 15:
        print(f"... 还有 {len(items)-15} 个测试")
    print("="*80 + "\n")

# 存储每个测试的开始时间
_test_start_times = {}

def pytest_runtest_setup(item):
    """在每个测试用例开始前记录开始时间"""
    _test_start_times[item.nodeid] = datetime.now()
    test_name = item.nodeid
    start_time = _test_start_times[item.nodeid].strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*80}")
    print(f"测试用例: {test_name}")
    print(f"开始时间: {start_time}")
    print(f"{'='*80}")

def pytest_runtest_teardown(item, nextitem):
    """在每个测试用例结束后记录结束时间并打印"""
    if item.nodeid in _test_start_times:
        start_time = _test_start_times[item.nodeid]
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        test_name = item.nodeid
        end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
        start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n{'='*80}")
        print(f"测试用例: {test_name}")
        print(f"开始时间: {start_time_str}")
        print(f"结束时间: {end_time_str}")
        print(f"执行耗时: {duration:.3f} 秒")
        print(f"{'='*80}\n")
        
        # 清理记录
        del _test_start_times[item.nodeid]
