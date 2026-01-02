import pytest
import requests

from conftest import API_BASE_URL, make_request_with_retry


class TestShopOwnerBase:
    """商家基础功能测试"""

    def test_change_shop_password(self, shop_owner_token):
        """测试修改商家密码"""
        url = f"{API_BASE_URL}/shopOwner/change-password"
        payload = {
            "old_password": "Admin@123456",
            "new_password": "Admin@123456"
        }
        headers = {"Authorization": f"Bearer {shop_owner_token}"}
        
        def request_func():
            return requests.post(url, json=payload, headers=headers)
        
        response = make_request_with_retry(request_func)
        print(f"修改密码响应状态码: {response.status_code}, 响应内容: {response.text}")
        assert response.status_code == 200
