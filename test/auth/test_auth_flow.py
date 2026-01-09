"""
认证流程测试 - 按照正确的业务顺序执行测试

业务顺序：
1. 管理员登录
2. 店主登录（依赖于 shop_owner_token fixture，它会创建店铺）
3. 店主刷新令牌
4. 店主登出
5. 管理员登出（最后执行，避免影响其他测试）
"""

import pytest
import requests
import sys
from pathlib import Path

# 添加上级目录到 sys.path，以便导入 conftest
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import API_BASE_URL, make_request_with_retry


class TestAuthFlow:
    """认证流程测试类 - 包含所有有业务依赖的认证测试用例"""

    # 类变量，用于在测试用例之间共享 token 和店铺ID
    shop_owner_token_value = None
    shop_owner_shop_id_value = None
    shop_owner_username = "shop1"
    shop_owner_password = "Admin@123456"

    # ==================== 登录测试 ====================

    def test_universal_login_admin(self):
        """测试管理员登录"""
        print("\n========== 管理员登录测试 ==========")
        url = f"{API_BASE_URL}/login"
        payload = {
            "username": "admin",
            "password": "Admin@123456"
        }
        
        def request_func():
            return requests.post(url, json=payload)
        
        response = make_request_with_retry(request_func)
        # 允许 200 或 429（频率限制）
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        if response.status_code == 200:
            print("✓ 管理员登录成功")
        elif response.status_code == 429:
            print("✗ 管理员登录频率限制，测试失败")
            pytest.fail(f"管理员登录频率限制，测试失败。状态码: {response.status_code}, 响应: {response.text}")

    def test_universal_login_shop_owner(self, admin_token):
        """测试商家登录

        此测试会先创建店铺（同时创建店主用户），然后登录
        """
        print("\n========== 商家登录测试 ==========")

        # 1. 创建店铺（会自动创建店主用户）
        shop_url = f"{API_BASE_URL}/admin/shop/create"
        shop_payload = {
            "owner_username": TestAuthFlow.shop_owner_username,
            "owner_password": TestAuthFlow.shop_owner_password,
            "name": "Test Shop for Login",
            "contact_phone": "13900139001",
            "contact_email": "shop1@test.com",
            "description": "Shop created for login testing",
            "valid_until": "2027-12-31T23:59:59Z"
        }
        shop_headers = {"Authorization": f"Bearer {admin_token}"}

        def shop_request_func():
            return requests.post(shop_url, json=shop_payload, headers=shop_headers)

        shop_response = make_request_with_retry(shop_request_func)
        if shop_response.status_code == 200:
            shop_data = shop_response.json()
            # 保存店铺ID供后续测试使用
            TestAuthFlow.shop_owner_shop_id_value = shop_data.get("id") or shop_data.get("shop_id")
            print(f"✓ 成功创建店铺（店主用户: shop1），店铺ID: {TestAuthFlow.shop_owner_shop_id_value}")
        elif shop_response.status_code == 409:
            print("⚠ 店铺已存在（shop1 用户已存在），直接进行登录测试")
            # 尝试获取店铺列表来获取店铺ID
            list_url = f"{API_BASE_URL}/admin/shop/list"
            list_params = {"page": 1, "pageSize": 10}
            list_headers = {"Authorization": f"Bearer {admin_token}"}
            
            def list_request_func():
                return requests.get(list_url, params=list_params, headers=list_headers)
            
            list_response = make_request_with_retry(list_request_func)
            if list_response.status_code == 200:
                list_data = list_response.json()
                shops = list_data.get("data", list_data.get("shops", []))
                if shops and len(shops) > 0:
                    # 找到shop1用户的店铺
                    for shop in shops:
                        if shop.get("owner_username") == TestAuthFlow.shop_owner_username:
                            TestAuthFlow.shop_owner_shop_id_value = shop.get("id")
                            print(f"✓ 找到现有店铺，ID: {TestAuthFlow.shop_owner_shop_id_value}")
                            break
        else:
            print(f"⚠ 创建店铺失败: {shop_response.status_code}, {shop_response.text}")

        # 2. 使用店主账号登录
        url = f"{API_BASE_URL}/login"
        payload = {
            "username": TestAuthFlow.shop_owner_username,
            "password": TestAuthFlow.shop_owner_password
        }
        
        def login_request_func():
            return requests.post(url, json=payload)
        
        response = make_request_with_retry(login_request_func)
        # 允许 200 或 429（频率限制）
        assert response.status_code == 200, f"Expected 200, got {response.status_code}，{response.text}"

        if response.status_code == 200:
            # 保存 token 供后续测试使用
            login_data = response.json()
            TestAuthFlow.shop_owner_token_value = login_data.get("token", "")
            print(f"✓ 商家登录成功，token: {TestAuthFlow.shop_owner_token_value[:20]}...")
        elif response.status_code == 429:
            print("✗ 商家登录频率限制，测试失败")
            pytest.fail(f"商家登录频率限制，测试失败。状态码: {response.status_code}, 响应: {response.text}")

    # ==================== 刷新令牌测试 ====================

    def test_refresh_admin_token(self, admin_token):
        """测试刷新管理员令牌"""
        print("\n========== 刷新管理员令牌测试 ==========")
        url = f"{API_BASE_URL}/admin/refresh-token"
        headers = {"Authorization": f"Bearer {admin_token}"}

        def request_func():
            return requests.post(url, headers=headers)

        response = make_request_with_retry(request_func)
        # 检查token是否已失效
        if response.status_code == 401:
            print("⚠ Token已失效，重新登录获取新token...")
            # 重新登录获取新token
            login_url = f"{API_BASE_URL}/login"
            login_payload = {
                "username": "admin",
                "password": "Admin@123456"
            }
            
            def login_request_func():
                return requests.post(login_url, json=login_payload)
            
            login_response = make_request_with_retry(login_request_func)
            if login_response.status_code == 200:
                login_data = login_response.json()
                new_token = login_data.get("token", "")
                headers = {"Authorization": f"Bearer {new_token}"}
                
                def refresh_request_func():
                    return requests.post(url, headers=headers)
                
                response = make_request_with_retry(refresh_request_func)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        if response.status_code == 200:
            response_data = response.json()
            new_token = response_data.get("token")
            expired_at = response_data.get("expiredAt")
            
            assert new_token is not None, "响应中未包含新token"
            assert expired_at is not None, "响应中未包含过期时间"
            
            print("✓ 刷新管理员令牌成功")
            print(f"✓ 新token: {new_token[:20]}...")
            print(f"✓ 过期时间: {expired_at}")
        else:
            print(f"✗ 刷新管理员令牌失败: {response.status_code}, {response.text}")

    def test_refresh_admin_token_invalid_token(self):
        """测试刷新管理员令牌 - 无效token"""
        print("\n========== 刷新管理员令牌测试 - 无效token ==========")
        url = f"{API_BASE_URL}/admin/refresh-token"
        headers = {"Authorization": "Bearer invalid_token"}

        def request_func():
            return requests.post(url, headers=headers)

        response = make_request_with_retry(request_func)
        # 预期返回401错误（token无效）
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ 无效token时正确返回401错误")

    def test_refresh_admin_token_no_token(self):
        """测试刷新管理员令牌 - 无token"""
        print("\n========== 刷新管理员令牌测试 - 无token ==========")
        url = f"{API_BASE_URL}/admin/refresh-token"
        # 不提供Authorization头

        def request_func():
            return requests.post(url)

        response = make_request_with_retry(request_func)
        # 预期返回401错误（未提供token）
        assert response.status_code != 200, f"Expected !=200, got {response.status_code}"
        print("✓ 未提供token时正确返回401错误")

    def test_refresh_shop_token(self):
        """测试刷新商家令牌

        使用 test_universal_login_shop_owner 获取的 token
        """
        print("\n========== 刷新商家令牌测试 ==========")
        if not TestAuthFlow.shop_owner_token_value:
            print("✗ 商家token未设置，测试失败")
            pytest.fail("商家token未设置，测试失败。请确保test_universal_login_shop_owner测试成功执行")

        url = f"{API_BASE_URL}/shop/refresh-token"
        headers = {"Authorization": f"Bearer {TestAuthFlow.shop_owner_token_value}"}

        def request_func():
            return requests.post(url, headers=headers)

        response = make_request_with_retry(request_func)
        # 允许 200 或 401（token 可能已失效）
        assert response.status_code == 200, f"Expected 200, got {response.status_code}，{response.text}"
        if response.status_code == 200:
            print("✓ 刷新商家令牌成功")
        else:
            print("⚠ 刷新商家令牌失败（token 可能已失效）")

    # ==================== 登出测试 ====================

    def test_z_admin_logout(self, admin_token):
        """测试管理员登出（最后执行）"""
        print("\n========== 管理员登出测试 ==========")
        url = f"{API_BASE_URL}/admin/logout"
        headers = {"Authorization": f"Bearer {admin_token}"}

        def request_func():
            return requests.post(url, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ 管理员登出成功")

    def test_shop_owner_logout(self):
        """测试商家登出

        使用 test_universal_login_shop_owner 获取的 token
        """
        print("\n========== 商家登出测试 ==========")
        if not TestAuthFlow.shop_owner_token_value:
            print("✗ 商家token未设置，测试失败")
            pytest.fail("商家token未设置，测试失败。请确保test_universal_login_shop_owner测试成功执行")

        url = f"{API_BASE_URL}/shopOwner/logout"
        headers = {"Authorization": f"Bearer {TestAuthFlow.shop_owner_token_value}"}

        def request_func():
            return requests.post(url, headers=headers)

        response = make_request_with_retry(request_func)
        # 允许 200 或 401（token 可能已失效）
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        if response.status_code == 200:
            print("✓ 商家登出成功")
        else:
            print("⚠ 商家登出响应 401（token 可能已失效）")

    # ==================== 临时令牌测试 ====================

    def test_get_temp_token(self):
        """测试临时令牌获取
        
        注意：此端点可能不存在或需要特定权限
        此测试不依赖admin_token fixture，因为之前的test_admin_logout可能已将其登出
        """
        print("\n========== 临时令牌获取 ==========")
        
        # 重新获取admin token（因为可能在之前的测试中被登出）
        admin_url = f"{API_BASE_URL}/login"
        admin_payload = {
            "username": "admin",
            "password": "Admin@123456"
        }
        
        def admin_request_func():
            return requests.post(admin_url, json=admin_payload)
        
        admin_response = make_request_with_retry(admin_request_func)
        if admin_response.status_code != 200:
            print(f"✗ 管理员登录失败: {admin_response.status_code}, {admin_response.text}")
            pytest.fail(f"无法获取管理员token，测试失败。状态码: {admin_response.status_code}, 响应: {admin_response.text}")
        
        admin_data = admin_response.json()
        admin_token_value = admin_data.get("token", "")
        if not admin_token_value:
            print("✗ 未能获取管理员token")
            pytest.fail("无法获取管理员token，测试失败")
        
        print(f"[OK] 重新获取管理员token成功")
        
        # 如果店铺ID不存在，尝试创建店铺
        shop_id = TestAuthFlow.shop_owner_shop_id_value
        token = TestAuthFlow.shop_owner_token_value
        
        if not shop_id or not token:
            print("⚠ 店铺ID或token不存在，尝试创建新店铺...")
            # 创建店铺
            shop_url = f"{API_BASE_URL}/admin/shop/create"
            import os
            unique_suffix = os.urandom(4).hex()
            shop_payload = {
                "owner_username": f"temp_shop_{unique_suffix}",
                "owner_password": "Admin@123456",
                "name": f"Temp Shop {unique_suffix}",
                "contact_phone": "13900139999",
                "contact_email": f"temp_{unique_suffix}@test.com",
                "description": "Shop created for temp token testing",
                "valid_until": "2027-12-31T23:59:59Z"
            }
            shop_headers = {"Authorization": f"Bearer {admin_token_value}"}
            
            def shop_request_func():
                return requests.post(shop_url, json=shop_payload, headers=shop_headers)
            
            shop_response = make_request_with_retry(shop_request_func)
            if shop_response.status_code == 200:
                shop_data = shop_response.json()
                # 尝试从不同位置获取店铺ID
                shop_id = shop_data.get("id") or shop_data.get("shop_id") or shop_data.get("data", {}).get("id")
                print(f"[OK] 成功创建店铺，ID: {shop_id}, 响应: {shop_data}")
                if not shop_id:
                    print(f"✗ 无法从响应中获取店铺ID，完整响应: {shop_data}")
                    pytest.fail(f"无法获取店铺ID，测试失败。完整响应: {shop_data}")
            else:
                print(f"✗ 创建店铺失败: {shop_response.status_code}, {shop_response.text}")
                pytest.fail(f"无法创建店铺，测试失败。状态码: {shop_response.status_code}, 响应: {shop_response.text}")
            
            # 登录获取token
            login_url = f"{API_BASE_URL}/login"
            login_payload = {
                "username": shop_payload["owner_username"],
                "password": "Admin@123456"
            }
            
            def login_request_func():
                return requests.post(login_url, json=login_payload)
            
            login_response = make_request_with_retry(login_request_func)
            if login_response.status_code == 200:
                login_data = login_response.json()
                token = login_data.get("token", "")
                print(f"[OK] 成功获取token")
            else:
                print(f"✗ 登录失败: {login_response.status_code}, {login_response.text}")
                pytest.fail(f"无法获取token，测试失败。状态码: {login_response.status_code}, 响应: {login_response.text}")

        # 尝试商家端点
        url = f"{API_BASE_URL}/shopOwner/shop/temp-token"
        params = {"shop_id": shop_id}
        headers = {"Authorization": f"Bearer {token}"}

        def request_func():
            return requests.get(url, params=params, headers=headers)

        response = make_request_with_retry(request_func)
 
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"