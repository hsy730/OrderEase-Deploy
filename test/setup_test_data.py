import requests
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conftest import API_BASE_URL, make_request_with_retry

def setup_test_data():
    """初始化测试数据"""
    print("开始初始化测试数据...")
    
    # 1. 管理员登录获取token
    print("\n1. 管理员登录...")
    admin_token = get_admin_token()
    if not admin_token:
        print("❌ 管理员登录失败")
        return False
    print("✓ 管理员登录成功")
    
    # 2. 创建testuser前端用户
    print("\n2. 创建testuser前端用户...")
    testuser_id = create_frontend_user(admin_token)
    if not testuser_id:
        print("❌ 创建testuser用户失败")
        return False
    print(f"✓ testuser用户创建成功，ID: {testuser_id}")
    
    # 3. 创建测试店铺（同时创建shop1商家用户）
    print("\n3. 创建测试店铺（同时创建shop1商家用户）...")
    shop_id = create_test_shop(admin_token)
    if not shop_id:
        print("❌ 创建测试店铺失败")
        return False
    print(f"✓ 测试店铺创建成功，ID: {shop_id}")
    
    # 4. 创建测试商品
    print("\n4. 创建测试商品...")
    product_id = create_test_product(admin_token, shop_id)
    if not product_id:
        print("❌ 创建测试商品失败")
        return False
    print(f"✓ 测试商品创建成功，ID: {product_id}")
    
    print("\n✅ 测试数据初始化完成！")
    print(f"\n测试数据摘要:")
    print(f"  - shop1商家用户: 已创建（通过店铺创建）")
    print(f"  - testuser用户ID: {testuser_id}")
    print(f"  - 测试店铺ID: {shop_id}")
    print(f"  - 测试商品ID: {product_id}")
    
    return True

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

def create_frontend_user(admin_token):
    """创建testuser前端用户（通过自主注册）"""
    url = f"{API_BASE_URL}/user/register"
    payload = {
        "username": "testuser",
        "password": "Admin1"
    }
    
    def request_func():
        return requests.post(url, json=payload)
    
    response = make_request_with_retry(request_func)
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    if response.status_code == 200:
        data = response.json()
        user = data.get("user", {})
        return user.get("id") or data.get("id") or data.get("user_id") or data.get("userId")
    elif response.status_code == 409 and "用户名已存在" in response.text:
        print("  用户已存在，继续...")
        return "existing_user"
    return None

def create_test_shop(admin_token):
    """创建测试店铺"""
    url = f"{API_BASE_URL}/admin/shop/create"
    payload = {
        "name": "Test Shop",
        "owner_username": "shop1",
        "owner_password": "Admin@123456",
        "contact_phone": "13900139001",
        "contact_email": "shop1@test.com",
        "description": "Test shop for testing",
        "address": "Test shop address"
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    def request_func():
        return requests.post(url, json=payload, headers=headers)
    
    response = make_request_with_retry(request_func)
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    if response.status_code == 200:
        data = response.json()
        shop_data = data.get("data", {})
        return shop_data.get("id") or data.get("id") or data.get("shop_id") or data.get("shopId")
    elif response.status_code == 409:
        print("  店铺已存在，尝试获取已存在的店铺...")
        return get_existing_shop(admin_token)
    return None

def get_existing_shop(admin_token):
    """获取已存在的店铺"""
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
            return shops[0].get("id")
    return None

def create_test_product(admin_token, shop_id):
    """创建测试商品"""
    url = f"{API_BASE_URL}/admin/product/create"
    payload = {
        "shop_id": shop_id,
        "name": "Test Product",
        "price": 100,
        "description": "Test product description"
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    def request_func():
        return requests.post(url, json=payload, headers=headers)
    
    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        data = response.json()
        return data.get("id") or data.get("product_id") or data.get("productId")
    return None

if __name__ == "__main__":
    success = setup_test_data()
    sys.exit(0 if success else 1)
