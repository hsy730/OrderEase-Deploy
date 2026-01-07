# 该文件已被重构到 test_business_flow.py 中，仅保留用于参考，不再作为测试执行
__test__ = False

import pytest
import requests

from conftest import API_BASE_URL


class TestAdminBase:
    """管理员基础功能测试"""

    def test_change_admin_password(self):
        """测试修改管理员密码"""
        url = f"{API_BASE_URL}/admin/change-password"
        payload = {
            "old_password": "Admin@123456",
            "new_password": "Admin@123456"
        }
        headers = {"Authorization": "Bearer test_token"}
        response = requests.post(url, json=payload, headers=headers)
        assert response.status_code in [200, 400, 401, 429]
