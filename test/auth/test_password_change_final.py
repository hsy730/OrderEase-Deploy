"""
管理员密码修改最终测试 - 独立测试，最后执行

此测试文件确保最后执行，完整测试密码修改流程：
1. 重新登录
2. 修改密码
3. 用新密码重新登录
4. 再次修改密码
5. 还原为初始密码

此测试不依赖任何 fixture，完全独立执行。
"""

import pytest
import requests
import sys
from pathlib import Path

# 添加上级目录到 sys.path，以便导入 conftest
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import API_BASE_URL, make_request_with_retry


class TestPasswordChangeFinal:
    """管理员密码修改最终测试类 - 最后执行的独立密码修改测试"""

    # 定义初始密码
    INITIAL_PASSWORD = "Admin@123456"
    FIRST_NEW_PASSWORD = "NewAdmin@123456"
    SECOND_NEW_PASSWORD = "AnotherAdmin@123456"
    USERNAME = "admin"

    def test_complete_password_change_flow(self):
        """完整的密码修改流程测试
        
        测试步骤：
        1. 使用初始密码登录
        2. 修改密码为第一个新密码
        3. 使用第一个新密码重新登录
        4. 修改密码为第二个新密码
        5. 使用第二个新密码重新登录
        6. 还原为初始密码
        7. 使用初始密码验证登录成功
        """
        print("\n" + "="*80)
        print("完整的密码修改流程测试")
        print("="*80)

        # ==================== 步骤1: 使用初始密码登录 ====================
        print("\n【步骤1】使用初始密码登录...")
        login_url = f"{API_BASE_URL}/login"
        login_payload = {
            "username": self.USERNAME,
            "password": self.INITIAL_PASSWORD
        }

        def login_request_func():
            return requests.post(login_url, json=login_payload)

        login_response = make_request_with_retry(login_request_func)
        assert login_response.status_code == 200, f"初始密码登录失败: {login_response.status_code}, {login_response.text}"

        login_data = login_response.json()
        token = login_data.get("token", "")
        assert token, "未能获取token"

        print(f"✓ 初始密码登录成功，token: {token[:20]}...")

        # ==================== 步骤2: 修改密码为第一个新密码 ====================
        print("\n【步骤2】修改密码为第一个新密码...")
        change_password_url = f"{API_BASE_URL}/admin/change-password"
        headers = {"Authorization": f"Bearer {token}"}
        change_payload = {
            "old_password": self.INITIAL_PASSWORD,
            "new_password": self.FIRST_NEW_PASSWORD
        }

        def change_request_func():
            return requests.post(change_password_url, json=change_payload, headers=headers)

        change_response = make_request_with_retry(change_request_func)
        assert change_response.status_code == 200, f"修改密码失败: {change_response.status_code}, {change_response.text}"

        print(f"✓ 密码修改成功: {self.INITIAL_PASSWORD} -> {self.FIRST_NEW_PASSWORD}")

        # ==================== 步骤3: 使用第一个新密码重新登录 ====================
        print("\n【步骤3】使用第一个新密码重新登录...")
        login_payload = {
            "username": self.USERNAME,
            "password": self.FIRST_NEW_PASSWORD
        }

        def login_request_func():
            return requests.post(login_url, json=login_payload)

        login_response = make_request_with_retry(login_request_func)
        assert login_response.status_code == 200, f"第一个新密码登录失败: {login_response.status_code}, {login_response.text}"

        login_data = login_response.json()
        token = login_data.get("token", "")
        assert token, "未能获取token"

        print(f"✓ 第一个新密码登录成功，token: {token[:20]}...")

        # ==================== 步骤4: 修改密码为第二个新密码 ====================
        print("\n【步骤4】修改密码为第二个新密码...")
        headers = {"Authorization": f"Bearer {token}"}
        change_payload = {
            "old_password": self.FIRST_NEW_PASSWORD,
            "new_password": self.SECOND_NEW_PASSWORD
        }

        def change_request_func():
            return requests.post(change_password_url, json=change_payload, headers=headers)

        change_response = make_request_with_retry(change_request_func)
        assert change_response.status_code == 200, f"修改密码失败: {change_response.status_code}, {change_response.text}"

        print(f"✓ 密码修改成功: {self.FIRST_NEW_PASSWORD} -> {self.SECOND_NEW_PASSWORD}")

        # ==================== 步骤5: 使用第二个新密码重新登录 ====================
        print("\n【步骤5】使用第二个新密码重新登录...")
        login_payload = {
            "username": self.USERNAME,
            "password": self.SECOND_NEW_PASSWORD
        }

        def login_request_func():
            return requests.post(login_url, json=login_payload)

        login_response = make_request_with_retry(login_request_func)
        assert login_response.status_code == 200, f"第二个新密码登录失败: {login_response.status_code}, {login_response.text}"

        login_data = login_response.json()
        token = login_data.get("token", "")
        assert token, "未能获取token"

        print(f"✓ 第二个新密码登录成功，token: {token[:20]}...")

        # ==================== 步骤6: 还原为初始密码 ====================
        print("\n【步骤6】还原为初始密码...")
        headers = {"Authorization": f"Bearer {token}"}
        change_payload = {
            "old_password": self.SECOND_NEW_PASSWORD,
            "new_password": self.INITIAL_PASSWORD
        }

        def change_request_func():
            return requests.post(change_password_url, json=change_payload, headers=headers)

        change_response = make_request_with_retry(change_request_func)
        assert change_response.status_code == 200, f"还原密码失败: {change_response.status_code}, {change_response.text}"

        print(f"✓ 密码还原成功: {self.SECOND_NEW_PASSWORD} -> {self.INITIAL_PASSWORD}")

        # ==================== 步骤7: 使用初始密码验证登录成功 ====================
        print("\n【步骤7】使用初始密码验证登录成功...")
        login_payload = {
            "username": self.USERNAME,
            "password": self.INITIAL_PASSWORD
        }

        def login_request_func():
            return requests.post(login_url, json=login_payload)

        login_response = make_request_with_retry(login_request_func)
        assert login_response.status_code == 200, f"初始密码验证登录失败: {login_response.status_code}, {login_response.text}"

        print(f"✓ 初始密码验证登录成功")

        print("\n" + "="*80)
        print("完整的密码修改流程测试完成！")
        print("="*80)

    def test_change_password_with_invalid_old_password(self):
        """测试使用错误的旧密码修改密码"""
        print("\n" + "="*80)
        print("测试使用错误的旧密码修改密码")
        print("="*80)

        # 首先登录获取 token
        print("\n使用初始密码登录...")
        login_url = f"{API_BASE_URL}/login"
        login_payload = {
            "username": self.USERNAME,
            "password": self.INITIAL_PASSWORD
        }

        def login_request_func():
            return requests.post(login_url, json=login_payload)

        login_response = make_request_with_retry(login_request_func)
        assert login_response.status_code == 200, f"登录失败: {login_response.status_code}, {login_response.text}"

        login_data = login_response.json()
        token = login_data.get("token", "")
        assert token, "未能获取token"

        print(f"✓ 登录成功，token: {token[:20]}...")

        # 尝试使用错误的旧密码修改密码
        print("\n尝试使用错误的旧密码修改密码...")
        change_password_url = f"{API_BASE_URL}/admin/change-password"
        headers = {"Authorization": f"Bearer {token}"}
        change_payload = {
            "old_password": "WrongPassword123",
            "new_password": self.FIRST_NEW_PASSWORD
        }

        def change_request_func():
            return requests.post(change_password_url, json=change_payload, headers=headers)

        change_response = make_request_with_retry(change_request_func)
        assert change_response.status_code != 200, f"预期返回非200，实际返回: {change_response.status_code}, {change_response.text}"

        print("✓ 使用错误的旧密码时正确返回400错误")

        # 验证原密码仍然有效
        print("\n验证原密码仍然有效...")
        login_payload = {
            "username": self.USERNAME,
            "password": self.INITIAL_PASSWORD
        }

        def login_request_func():
            return requests.post(login_url, json=login_payload)

        login_response = make_request_with_retry(login_request_func)
        assert login_response.status_code == 200, f"原密码验证失败: {login_response.status_code}, {login_response.text}"

        print("✓ 原密码仍然有效")

        print("\n" + "="*80)
        print("错误的旧密码修改密码测试完成！")
        print("="*80)
