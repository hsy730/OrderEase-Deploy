"""
商家密码修改最终测试 - 独立测试，最后执行

此测试文件确保最后执行，完整测试商家密码修改流程：
1. 管理员登录
2. 管理员创建店铺（自动创建店主账号）
3. 店主使用初始密码登录
4. 店主修改密码
5. 店主用新密码重新登录
6. 店主再次修改密码
7. 管理员删除店铺
8. 管理员登出

此测试不依赖任何 fixture，完全独立执行。
"""

import pytest
import requests
import sys
import os
from pathlib import Path

# 添加上级目录到 sys.path，以便导入 conftest
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import API_BASE_URL, make_request_with_retry


class TestShopOwnerPasswordChangeFinal:
    """商家密码修改最终测试类 - 最后执行的独立密码修改测试"""

    # 定义初始密码
    INITIAL_PASSWORD = "TestPassword@123"
    FIRST_NEW_PASSWORD = "NewShopOwner@123456"
    SECOND_NEW_PASSWORD = "AnotherShopOwner@123456"
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "Admin@123456"

    def test_z_complete_password_change_flow(self):
        """完整的商家密码修改流程测试（最后执行）

        测试步骤：
        1. 管理员登录
        2. 管理员创建店铺（自动创建店主账号）
        3. 店主使用初始密码登录
        4. 店主修改密码
        5. 店主用新密码重新登录
        6. 店主再次修改密码
        7. 管理员删除店铺
        8. 管理员登出
        """
        print("\n" + "="*80)
        print("完整的商家密码修改流程测试")
        print("="*80)

        # ==================== 步骤1: 管理员登录 ====================
        print("\n【步骤1】管理员登录...")
        admin_login_url = f"{API_BASE_URL}/login"
        admin_login_payload = {
            "username": self.ADMIN_USERNAME,
            "password": self.ADMIN_PASSWORD
        }

        def admin_login_request_func():
            return requests.post(admin_login_url, json=admin_login_payload)

        admin_login_response = make_request_with_retry(admin_login_request_func)
        assert admin_login_response.status_code == 200, f"管理员登录失败: {admin_login_response.status_code}, {admin_login_response.text}"

        admin_login_data = admin_login_response.json()
        admin_token = admin_login_data.get("token", "")
        assert admin_token, "未能获取管理员token"

        print(f"✓ 管理员登录成功，token: {admin_token[:20]}...")

        # ==================== 步骤2: 管理员创建店铺 ====================
        print("\n【步骤2】管理员创建店铺（自动创建店主账号）...")
        shop_owner_username = f"shop_owner_{os.urandom(4).hex()}"
        create_shop_url = f"{API_BASE_URL}/admin/shop/create"
        create_shop_payload = {
            "owner_username": shop_owner_username,
            "owner_password": self.INITIAL_PASSWORD,
            "name": f"Test Shop {os.urandom(4).hex()}",
            "contact_phone": "13800138000",
            "contact_email": f"shop_{os.urandom(4).hex()}@test.com",
            "description": "Shop created for password change testing",
            "valid_until": "2027-12-31T23:59:59Z"
        }
        shop_headers = {"Authorization": f"Bearer {admin_token}"}

        def create_shop_request_func():
            return requests.post(create_shop_url, json=create_shop_payload, headers=shop_headers)

        create_shop_response = make_request_with_retry(create_shop_request_func)
        assert create_shop_response.status_code == 200, f"创建店铺失败: {create_shop_response.status_code}, {create_shop_response.text}"

        create_shop_data = create_shop_response.json()
        shop_id = create_shop_data.get("id") or create_shop_data.get("shop_id") or create_shop_data.get("data", {}).get("id")
        assert shop_id, "未能获取店铺ID"

        print(f"✓ 创建店铺成功，店铺ID: {shop_id}，店主用户名: {shop_owner_username}")

        # ==================== 步骤3: 店主使用初始密码登录 ====================
        print("\n【步骤3】店主使用初始密码登录...")
        shop_owner_login_url = f"{API_BASE_URL}/login"
        shop_owner_login_payload = {
            "username": shop_owner_username,
            "password": self.INITIAL_PASSWORD
        }

        def shop_owner_login_request_func():
            return requests.post(shop_owner_login_url, json=shop_owner_login_payload)

        shop_owner_login_response = make_request_with_retry(shop_owner_login_request_func)
        assert shop_owner_login_response.status_code == 200, f"店主初始密码登录失败: {shop_owner_login_response.status_code}, {shop_owner_login_response.text}"

        shop_owner_login_data = shop_owner_login_response.json()
        shop_owner_token = shop_owner_login_data.get("token", "")
        assert shop_owner_token, "未能获取店主token"

        print(f"✓ 店主初始密码登录成功，token: {shop_owner_token[:20]}...")

        # ==================== 步骤4: 店主修改密码为第一个新密码 ====================
        print("\n【步骤4】店主修改密码为第一个新密码...")
        change_password_url = f"{API_BASE_URL}/shopOwner/change-password"
        change_password_headers = {"Authorization": f"Bearer {shop_owner_token}"}
        change_password_payload = {
            "old_password": self.INITIAL_PASSWORD,
            "new_password": self.FIRST_NEW_PASSWORD
        }

        def change_password_request_func():
            return requests.post(change_password_url, json=change_password_payload, headers=change_password_headers)

        change_password_response = make_request_with_retry(change_password_request_func)
        assert change_password_response.status_code == 200, f"修改密码失败: {change_password_response.status_code}, {change_password_response.text}"

        print(f"✓ 密码修改成功: {self.INITIAL_PASSWORD} -> {self.FIRST_NEW_PASSWORD}")

        # ==================== 步骤5: 店主使用第一个新密码重新登录 ====================
        print("\n【步骤5】店主使用第一个新密码重新登录...")
        shop_owner_login_payload = {
            "username": shop_owner_username,
            "password": self.FIRST_NEW_PASSWORD
        }

        def shop_owner_login_request_func():
            return requests.post(shop_owner_login_url, json=shop_owner_login_payload)

        shop_owner_login_response = make_request_with_retry(shop_owner_login_request_func)
        assert shop_owner_login_response.status_code == 200, f"店主第一个新密码登录失败: {shop_owner_login_response.status_code}, {shop_owner_login_response.text}"

        shop_owner_login_data = shop_owner_login_response.json()
        shop_owner_token = shop_owner_login_data.get("token", "")
        assert shop_owner_token, "未能获取店主token"

        print(f"✓ 店主第一个新密码登录成功，token: {shop_owner_token[:20]}...")

        # ==================== 步骤6: 店主修改密码为第二个新密码 ====================
        print("\n【步骤6】店主修改密码为第二个新密码...")
        change_password_headers = {"Authorization": f"Bearer {shop_owner_token}"}
        change_password_payload = {
            "old_password": self.FIRST_NEW_PASSWORD,
            "new_password": self.SECOND_NEW_PASSWORD
        }

        def change_password_request_func():
            return requests.post(change_password_url, json=change_password_payload, headers=change_password_headers)

        change_password_response = make_request_with_retry(change_password_request_func)
        assert change_password_response.status_code == 200, f"修改密码失败: {change_password_response.status_code}, {change_password_response.text}"

        print(f"✓ 密码修改成功: {self.FIRST_NEW_PASSWORD} -> {self.SECOND_NEW_PASSWORD}")

        # ==================== 步骤7: 管理员删除店铺 ====================
        print("\n【步骤7】管理员删除店铺...")
        delete_shop_url = f"{API_BASE_URL}/admin/shop/delete"
        delete_shop_params = {"shop_id": shop_id}
        delete_shop_headers = {"Authorization": f"Bearer {admin_token}"}

        def delete_shop_request_func():
            return requests.delete(delete_shop_url, params=delete_shop_params, headers=delete_shop_headers)

        delete_shop_response = make_request_with_retry(delete_shop_request_func)
        assert delete_shop_response.status_code == 200, f"删除店铺失败: {delete_shop_response.status_code}, {delete_shop_response.text}"

        print(f"✓ 删除店铺成功，店铺ID: {shop_id}")

        # ==================== 步骤8: 管理员登出 ====================
        print("\n【步骤8】管理员登出...")
        admin_logout_url = f"{API_BASE_URL}/admin/logout"
        admin_logout_headers = {"Authorization": f"Bearer {admin_token}"}

        def admin_logout_request_func():
            return requests.post(admin_logout_url, headers=admin_logout_headers)

        admin_logout_response = make_request_with_retry(admin_logout_request_func)
        assert admin_logout_response.status_code == 200, f"管理员登出失败: {admin_logout_response.status_code}, {admin_logout_response.text}"

        print(f"✓ 管理员登出成功")

        print("\n" + "="*80)
        print("完整的商家密码修改流程测试完成！")
        print("="*80)


    def test_zz_change_password_with_invalid_old_password(self):
        """测试商家使用错误的旧密码修改密码（最后执行）"""
        print("\n" + "="*80)
        print("测试商家使用错误的旧密码修改密码")
        print("="*80)

        # ==================== 管理员登录 ====================
        print("\n管理员登录...")
        admin_login_url = f"{API_BASE_URL}/login"
        admin_login_payload = {
            "username": self.ADMIN_USERNAME,
            "password": self.ADMIN_PASSWORD
        }

        def admin_login_request_func():
            return requests.post(admin_login_url, json=admin_login_payload)

        admin_login_response = make_request_with_retry(admin_login_request_func)
        assert admin_login_response.status_code == 200, f"管理员登录失败: {admin_login_response.status_code}, {admin_login_response.text}"

        admin_login_data = admin_login_response.json()
        admin_token = admin_login_data.get("token", "")
        assert admin_token, "未能获取管理员token"

        print(f"✓ 管理员登录成功")

        # ==================== 管理员创建店铺 ====================
        print("\n管理员创建店铺...")
        shop_owner_username = f"shop_owner_{os.urandom(4).hex()}"
        create_shop_url = f"{API_BASE_URL}/admin/shop/create"
        create_shop_payload = {
            "owner_username": shop_owner_username,
            "owner_password": self.INITIAL_PASSWORD,
            "name": f"Test Shop {os.urandom(4).hex()}",
            "contact_phone": "13800138000",
            "contact_email": f"shop_{os.urandom(4).hex()}@test.com",
            "description": "Shop created for invalid password test",
            "valid_until": "2027-12-31T23:59:59Z"
        }
        shop_headers = {"Authorization": f"Bearer {admin_token}"}

        def create_shop_request_func():
            return requests.post(create_shop_url, json=create_shop_payload, headers=shop_headers)

        create_shop_response = make_request_with_retry(create_shop_request_func)
        assert create_shop_response.status_code == 200, f"创建店铺失败: {create_shop_response.status_code}, {create_shop_response.text}"

        print(f"✓ 创建店铺成功，店主用户名: {shop_owner_username}")

        # ==================== 管理员登出 ====================
        print("\n管理员登出...")
        admin_logout_url = f"{API_BASE_URL}/admin/logout"
        admin_logout_headers = {"Authorization": f"Bearer {admin_token}"}

        def admin_logout_request_func():
            return requests.post(admin_logout_url, headers=admin_logout_headers)

        admin_logout_response = make_request_with_retry(admin_logout_request_func)
        assert admin_logout_response.status_code == 200, f"管理员登出失败: {admin_logout_response.status_code}, {admin_logout_response.text}"

        print(f"✓ 管理员登出成功")

        # ==================== 店主使用初始密码登录 ====================
        print("\n店主使用初始密码登录...")
        shop_owner_login_url = f"{API_BASE_URL}/login"
        shop_owner_login_payload = {
            "username": shop_owner_username,
            "password": self.INITIAL_PASSWORD
        }

        def shop_owner_login_request_func():
            return requests.post(shop_owner_login_url, json=shop_owner_login_payload)

        shop_owner_login_response = make_request_with_retry(shop_owner_login_request_func)
        assert shop_owner_login_response.status_code == 200, f"店主登录失败: {shop_owner_login_response.status_code}, {shop_owner_login_response.text}"

        shop_owner_login_data = shop_owner_login_response.json()
        shop_owner_token = shop_owner_login_data.get("token", "")
        assert shop_owner_token, "未能获取店主token"

        print(f"✓ 店主登录成功")

        # ==================== 尝试使用错误的旧密码修改密码 ====================
        print("\n尝试使用错误的旧密码修改密码...")
        change_password_url = f"{API_BASE_URL}/shopOwner/change-password"
        change_password_headers = {"Authorization": f"Bearer {shop_owner_token}"}
        change_password_payload = {
            "old_password": "WrongPassword123",
            "new_password": self.FIRST_NEW_PASSWORD
        }

        def change_password_request_func():
            return requests.post(change_password_url, json=change_password_payload, headers=change_password_headers)

        change_password_response = make_request_with_retry(change_password_request_func)
        assert change_password_response.status_code != 200, f"预期返回非200，实际返回: {change_password_response.status_code}, {change_password_response.text}"

        print("✓ 使用错误的旧密码时正确返回错误")

        # ==================== 验证原密码仍然有效 ====================
        print("\n验证原密码仍然有效...")
        shop_owner_login_payload = {
            "username": shop_owner_username,
            "password": self.INITIAL_PASSWORD
        }

        def shop_owner_login_request_func():
            return requests.post(shop_owner_login_url, json=shop_owner_login_payload)

        shop_owner_login_response = make_request_with_retry(shop_owner_login_request_func)
        assert shop_owner_login_response.status_code == 200, f"原密码验证失败: {shop_owner_login_response.status_code}, {shop_owner_login_response.text}"

        print("✓ 原密码仍然有效")

        print("\n" + "="*80)
        print("错误的旧密码修改密码测试完成！")
        print("="*80)
