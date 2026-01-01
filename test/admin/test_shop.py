import os
import pytest
import requests

from conftest import API_BASE_URL


class TestAdminShopAPI:
    """管理员店铺管理接口测试"""

    def test_create_shop(self):
        """测试创建店铺"""
        url = f"{API_BASE_URL}/admin/shop/create"
        payload = {
            "name": f"Test Shop {os.urandom(4).hex()}",
            "description": "Test shop description",
            "address": "Test address"
        }
        headers = {"Authorization": "Bearer test_token"}
        response = requests.post(url, json=payload, headers=headers)
        assert response.status_code in [200, 400, 401, 429]

    def test_update_shop(self):
        """测试更新店铺信息"""
        url = f"{API_BASE_URL}/admin/shop/update"
        payload = {
            "id": "1",
            "name": "Updated Shop Name",
            "description": "Updated description"
        }
        headers = {"Authorization": "Bearer test_token"}
        response = requests.put(url, json=payload, headers=headers)
        assert response.status_code in [200, 400, 401, 404, 429]

    def test_get_shop_detail(self):
        """测试获取店铺详情"""
        url = f"{API_BASE_URL}/admin/shop/detail"
        params = {"shop_id": "1"}
        headers = {"Authorization": "Bearer test_token"}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code in [200, 400, 401, 404, 429]

    def test_get_shop_list(self):
        """测试获取店铺列表"""
        url = f"{API_BASE_URL}/admin/shop/list"
        params = {
            "page": 1,
            "page_size": 10
        }
        headers = {"Authorization": "Bearer test_token"}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code == 200

    def test_delete_shop(self):
        """测试删除店铺"""
        url = f"{API_BASE_URL}/admin/shop/delete"
        params = {"shop_id": "999"}
        headers = {"Authorization": "Bearer test_token"}
        response = requests.delete(url, params=params, headers=headers)
        assert response.status_code == 200

    def test_upload_shop_image(self):
        """测试上传店铺图片"""
        url = f"{API_BASE_URL}/admin/shop/upload-image"
        files = {"image": ("test.jpg", b"fake image data", "image/jpeg")}
        headers = {"Authorization": "Bearer test_token"}
        response = requests.post(url, files=files, headers=headers)
        assert response.status_code == 200

    def test_check_shop_name_exists(self):
        """测试检查店铺名称是否存在"""
        url = f"{API_BASE_URL}/admin/shop/check-name"
        params = {"name": "test shop"}
        headers = {"Authorization": "Bearer test_token"}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code == 200

    def test_get_shop_image(self):
        """测试获取店铺图片"""
        url = f"{API_BASE_URL}/admin/shop/image"
        params = {"shop_id": "1"}
        headers = {"Authorization": "Bearer test_token"}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code == 200

    def test_get_shop_temp_token(self):
        """测试获取店铺临时令牌"""
        url = f"{API_BASE_URL}/admin/shop/temp-token"
        params = {"shop_id": "1"}
        headers = {"Authorization": "Bearer test_token"}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code == 200

    def test_update_order_status_flow(self):
        """测试更新订单状态流转"""
        url = f"{API_BASE_URL}/admin/shop/update-order-status-flow"
        payload = {
            "shop_id": 1,
            "order_status_flow": {
                "statuses": [
                    {
                        "value": 1,
                        "label": "pending",
                        "type": "normal",
                        "isFinal": False,
                        "actions": [
                            {
                                "name": "accept",
                                "nextStatus": 2,
                                "nextStatusLabel": "processing"
                            }
                        ]
                    }
                ]
            }
        }
        headers = {"Authorization": "Bearer test_token"}
        response = requests.put(url, json=payload, headers=headers)
        assert response.status_code == 200
