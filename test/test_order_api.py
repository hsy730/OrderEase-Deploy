"""
测试创建订单和查询订单详情接口
"""
import requests
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conftest import API_BASE_URL, make_request_with_retry

def test_create_and_get_order():
    """测试创建订单后查询订单详情"""
    print("\n" + "="*60)
    print("开始测试：创建订单 + 查询订单详情")
    print("="*60)
    
    # 1. 登录获取token
    print("\n[1/6] 登录获取管理员token...")
    login_url = f"{API_BASE_URL}/login"
    login_payload = {"username": "admin", "password": "Admin@123456"}
    
    def login_request():
        return requests.post(login_url, json=login_payload)
    
    resp = make_request_with_retry(login_request)
    assert resp.status_code == 200, f"登录失败: {resp.status_code}"
    
    token = resp.json().get("token", "")
    print(f"✓ 登录成功，token: {token[:20]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 获取店铺列表
    print("\n[2/6] 获取店铺列表...")
    shop_list_url = f"{API_BASE_URL}/admin/shop/list"
    
    def shop_list_request():
        return requests.get(shop_list_url, params={"page": 1, "pageSize": 1}, headers=headers)
    
    resp = make_request_with_retry(shop_list_request)
    assert resp.status_code == 200, f"获取店铺列表失败: {resp.status_code}"
    
    data = resp.json()
    shops = data.get("data", data.get("shops", []))
    assert shops, "没有可用的店铺"
    
    shop_id = shops[0].get("id")
    print(f"✓ 获取到店铺ID: {shop_id}")
    
    # 3. 获取用户列表
    print("\n[3/6] 获取用户列表...")
    user_list_url = f"{API_BASE_URL}/admin/user/list"
    
    def user_list_request():
        return requests.get(user_list_url, params={"page": 1, "pageSize": 1}, headers=headers)
    
    resp = make_request_with_retry(user_list_request)
    assert resp.status_code == 200, f"获取用户列表失败: {resp.status_code}"
    
    data = resp.json()
    users = data.get("data", data.get("users", []))
    assert users, "没有可用的用户"
    
    user_id = users[0].get("id")
    print(f"✓ 获取到用户ID: {user_id}")
    
    # 4. 获取商品列表（如果没有则创建）
    print("\n[4/6] 获取商品列表...")
    product_list_url = f"{API_BASE_URL}/admin/product/list"
    
    def product_list_request():
        return requests.get(product_list_url, params={"page": 1, "pageSize": 1, "shop_id": str(shop_id)}, headers=headers)
    
    resp = make_request_with_retry(product_list_request)
    assert resp.status_code == 200, f"获取商品列表失败: {resp.status_code}"
    
    data = resp.json()
    products = data.get("data", data.get("products", []))
    
    if not products:
        print("  没有可用商品，正在创建测试商品...")
        create_product_url = f"{API_BASE_URL}/admin/product/create"
        import random
        product_payload = {
            "shop_id": str(shop_id),
            "name": f"测试商品_{random.randint(1000, 9999)}",
            "price": 100,
            "description": "测试商品描述",
            "stock": 100
        }
        
        def create_product_request():
            return requests.post(create_product_url, json=product_payload, headers=headers)
        
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
    
    # 5. 创建订单
    print("\n[5/6] 创建订单...")
    create_order_url = f"{API_BASE_URL}/admin/order/create"
    order_payload = {
        "shop_id": str(shop_id),
        "user_id": str(user_id),
        "items": [
            {
                "product_id": str(product_id),
                "quantity": 1,
                "price": product_price
            }
        ]
    }
    
    def create_order_request():
        return requests.post(create_order_url, json=order_payload, headers=headers)
    
    resp = make_request_with_retry(create_order_request)
    assert resp.status_code == 200, f"创建订单失败: {resp.status_code}, 响应: {resp.text}"
    
    data = resp.json()
    order_id = data.get("id") or data.get("order_id") or data.get("orderId")
    assert order_id, f"创建订单成功但无法获取订单ID，响应: {data}"
    
    print(f"✓ 创建订单成功，订单ID: {order_id}")
    
    # 6. 查询订单详情
    print("\n[6/6] 查询订单详情...")
    order_detail_url = f"{API_BASE_URL}/admin/order/detail"
    
    def order_detail_request():
        return requests.get(order_detail_url, params={"id": str(order_id), "shop_id": str(shop_id)}, headers=headers)
    
    resp = make_request_with_retry(order_detail_request)
    assert resp.status_code == 200, f"查询订单详情失败: {resp.status_code}, 响应: {resp.text}"
    
    order_detail = resp.json()
    
    # 验证订单详情
    assert isinstance(order_detail, dict), f"订单详情格式错误，期望字典类型，实际: {type(order_detail)}"
    assert "id" in order_detail, f"订单详情缺少id字段，实际响应: {order_detail}"
    
    result_order_id = order_detail.get("id")
    assert str(result_order_id) == str(order_id), f"订单ID不匹配，期望: {order_id}，实际: {result_order_id}"
    
    print(f"✓ 查询订单详情成功")
    print(f"  订单ID: {order_detail.get('id')}")
    print(f"  用户ID: {order_detail.get('user_id')}")
    print(f"  店铺ID: {order_detail.get('shop_id')}")
    print(f"  总价: {order_detail.get('total_price')}")
    print(f"  状态: {order_detail.get('status')}")
    print(f"  创建时间: {order_detail.get('created_at')}")
    
    print("\n" + "="*60)
    print("✓ 测试通过：创建订单和查询订单详情接口正常")
    print("="*60)

if __name__ == "__main__":
    try:
        success = test_create_and_get_order()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
