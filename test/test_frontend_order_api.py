"""
验证用户端前端订单列表接口返回的订单ID是否能正确用于查询详情接口
"""
import requests
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conftest import API_BASE_URL, make_request_with_retry


def test_frontend_order_list_and_detail():
    """测试前端订单列表接口返回的订单ID能否正确查询详情"""
    print("\n" + "="*70)
    print("开始测试：用户端前端订单列表 + 订单详情接口")
    print("="*70)
    
    # 1. 注册用户并登录获取token
    print("\n[1/7] 注册用户并登录...")
    import random
    username = f"test_user_{random.randint(1000, 9999)}"
    password = "Test@123456"
    
    # 注册
    register_url = f"{API_BASE_URL}/user/register"
    register_payload = {"username": username, "password": password}
    
    def register_request():
        return requests.post(register_url, json=register_payload)
    
    resp = make_request_with_retry(register_request)
    assert resp.status_code == 200, f"用户注册失败: {resp.status_code}"
    print(f"✓ 用户注册成功: {username}")
    
    # 登录
    login_url = f"{API_BASE_URL}/user/login"
    login_payload = {"username": username, "password": password}
    
    def login_request():
        return requests.post(login_url, json=login_payload)
    
    resp = make_request_with_retry(login_request)
    assert resp.status_code == 200, f"用户登录失败: {resp.status_code}"
    
    login_data = resp.json()
    token = login_data.get("token", "")
    user_info = login_data.get("user", {})
    user_id = user_info.get("id", "")
    print(f"✓ 用户登录成功，token: {token[:20]}...")
    print(f"  用户ID: {user_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 获取店铺列表（使用公开接口或管理接口）
    print("\n[2/7] 获取店铺列表...")
    # 先尝试使用管理后台接口获取店铺
    admin_login_url = f"{API_BASE_URL}/login"
    admin_payload = {"username": "admin", "password": "Admin@123456"}
    
    def admin_login_request():
        return requests.post(admin_login_url, json=admin_payload)
    
    resp = make_request_with_retry(admin_login_request)
    assert resp.status_code == 200, f"管理员登录失败: {resp.status_code}"
    
    admin_token = resp.json().get("token", "")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    shop_list_url = f"{API_BASE_URL}/admin/shop/list"
    
    def shop_list_request():
        return requests.get(shop_list_url, params={"page": 1, "pageSize": 1}, headers=admin_headers)
    
    resp = make_request_with_retry(shop_list_request)
    assert resp.status_code == 200, f"获取店铺列表失败: {resp.status_code}"
    
    data = resp.json()
    shops = data.get("data", data.get("shops", []))
    assert shops, "没有可用的店铺"
    
    shop_id = shops[0].get("id")
    print(f"✓ 获取到店铺ID: {shop_id}")
    
    # 3. 获取商品列表
    print("\n[3/7] 获取商品列表...")
    product_list_url = f"{API_BASE_URL}/product/list"
    
    def product_list_request():
        return requests.get(product_list_url, params={"page": 1, "pageSize": 1, "shop_id": str(shop_id)}, headers=headers)
    
    resp = make_request_with_retry(product_list_request)
    assert resp.status_code == 200, f"获取商品列表失败: {resp.status_code}, 响应: {resp.text}"
    
    data = resp.json()
    products = data.get("data", data.get("products", []))
    
    if not products:
        print("  没有可用商品，使用管理接口创建测试商品...")
        create_product_url = f"{API_BASE_URL}/admin/product/create"
        product_payload = {
            "shop_id": shop_id,  # 保持为字符串，不转换为int
            "name": f"前端测试商品_{random.randint(1000, 9999)}",
            "price": 100,
            "description": "前端测试商品描述",
            "stock": 100
        }
        
        def create_product_request():
            return requests.post(create_product_url, json=product_payload, headers=admin_headers)
        
        resp = make_request_with_retry(create_product_request)
        assert resp.status_code == 200, f"创建商品失败: {resp.status_code}, 响应: {resp.text}"
        
        product_data = resp.json()
        product_id = product_data.get("id") or product_data.get("product_id")
        product_price = 100
        print(f"✓ 创建测试商品成功，商品ID: {product_id}")
    else:
        product_id = products[0].get("id")
        product_price = products[0].get("price", 100)
        print(f"✓ 获取到商品ID: {product_id}, 价格: {product_price}")
    
    # 4. 创建订单（前端接口）
    print("\n[4/7] 使用前端接口创建订单...")
    create_order_url = f"{API_BASE_URL}/order/create"
    order_payload = {
        "shop_id": shop_id,  # 保持为字符串
        "user_id": user_id,  # 使用从登录响应获取的用户ID
        "items": [
            {
                "product_id": product_id,  # 保持为字符串
                "quantity": 1,
                "price": product_price,
                "options": []
            }
        ],
        "remark": "前端测试订单"
    }
    
    def create_order_request():
        return requests.post(create_order_url, json=order_payload, headers=headers)
    
    resp = make_request_with_retry(create_order_request)
    assert resp.status_code == 200, f"创建订单失败: {resp.status_code}, 响应: {resp.text}"
    
    data = resp.json()
    created_order_id = data.get("order_id") or data.get("id")
    print(f"✓ 创建订单成功，订单ID: {created_order_id}")
    
    # 5. 查询用户订单列表（前端接口）
    print("\n[5/7] 查询用户订单列表（前端接口）...")
    order_list_url = f"{API_BASE_URL}/order/user/list"
    
    def order_list_request():
        return requests.get(
            order_list_url, 
            params={"user_id": str(user_id), "shop_id": str(shop_id), "page": 1, "pageSize": 10}, 
            headers=headers
        )
    
    resp = make_request_with_retry(order_list_request)
    assert resp.status_code == 200, f"查询订单列表失败: {resp.status_code}, 响应: {resp.text}"
    
    data = resp.json()
    orders = data.get("data", [])
    assert orders, "订单列表为空"
    
    print(f"✓ 获取到 {len(orders)} 个订单")
    
    # 显示第一个订单的信息
    first_order = orders[0]
    list_order_id = first_order.get("id")
    print(f"\n  列表中的第一个订单:")
    print(f"    订单ID: {list_order_id} (类型: {type(list_order_id).__name__})")
    print(f"    用户ID: {first_order.get('user_id')}")
    print(f"    店铺ID: {first_order.get('shop_id')}")
    print(f"    总价: {first_order.get('total_price')}")
    print(f"    状态: {first_order.get('status')}")
    print(f"    创建时间: {first_order.get('created_at')}")
    
    # 6. 使用列表中的订单ID查询详情（前端接口）
    print("\n[6/7] 使用列表中的订单ID查询详情（前端接口）...")
    order_detail_url = f"{API_BASE_URL}/order/detail"
    
    def order_detail_request():
        return requests.get(
            order_detail_url, 
            params={"id": str(list_order_id), "shop_id": str(shop_id)}, 
            headers=headers
        )
    
    resp = make_request_with_retry(order_detail_request)
    assert resp.status_code == 200, f"查询订单详情失败: {resp.status_code}, 响应: {resp.text}"
    
    order_detail = resp.json()
    
    # 验证订单详情
    assert isinstance(order_detail, dict), f"订单详情格式错误，期望字典类型，实际: {type(order_detail)}"
    
    detail_order_id = order_detail.get("id")
    print(f"\n  查询到的订单详情:")
    print(f"    订单ID: {detail_order_id} (类型: {type(detail_order_id).__name__})")
    print(f"    用户ID: {order_detail.get('user_id')}")
    print(f"    店铺ID: {order_detail.get('shop_id')}")
    print(f"    总价: {order_detail.get('total_price')}")
    print(f"    状态: {order_detail.get('status')}")
    print(f"    创建时间: {order_detail.get('created_at')}")
    
    # 7. 验证订单ID是否匹配
    print("\n[7/7] 验证订单ID是否匹配...")
    
    # 转换ID为字符串进行比较
    list_id_str = str(list_order_id)
    detail_id_str = str(detail_order_id)
    
    assert list_id_str == detail_id_str, f"订单ID不匹配！列表中的ID: {list_id_str}, 详情的ID: {detail_id_str}"
    
    print(f"✓ 订单ID匹配成功: {list_id_str}")
    
    # 额外验证：确认是我们创建的订单
    if str(list_order_id) == str(created_order_id):
        print(f"✓ 验证通过：列表中的订单正是我们刚创建的订单")
    else:
        print(f"⚠ 注意：列表中的订单(ID: {list_order_id})与刚创建的订单(ID: {created_order_id})不同")
        print(f"  这可能是由于列表返回了其他历史订单")
    
    print("\n" + "="*70)
    print("✓ 测试通过：前端订单列表接口返回的订单ID可以正确查询详情")
    print("="*70)


if __name__ == "__main__":
    try:
        success = test_frontend_order_list_and_detail()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
