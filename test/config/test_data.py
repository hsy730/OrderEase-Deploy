"""
测试数据配置模块 - 统一管理所有测试数据
"""

import os
from typing import Dict, Any


class TestDataConfig:
    """测试数据配置类 - 单例模式"""

    __test__ = False  # 告诉 pytest 不要将此类作为测试类收集

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """初始化默认测试数据"""
        # 认证数据
        self.ADMIN_CREDENTIALS = {
            "username": "admin",
            "password": "Admin@123456"
        }

        self.DEFAULT_PASSWORD = "TestPassword123"
        self.VALID_PASSWORD_PATTERN = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,20}$"

        # 用户数据
        self.VALID_PHONE = "13800138000"
        self.PHONE_PATTERN = r"^1[3-9]\d{9}$"

        # 店铺数据
        self.DEFAULT_SHOP = {
            "name_template": "Test Shop {suffix}",
            "description": "Shop created for testing",
            "address": "Test Address",
            "valid_until": "2027-12-31T23:59:59Z"
        }

        # 商品数据
        self.DEFAULT_PRODUCT = {
            "name_template": "Test Product {suffix}",
            "description": "Product created for testing",
            "price": 100,
            "stock": 100
        }

        # 订单数据
        self.DEFAULT_ORDER = {
            "quantity": 1,
            "price": 100
        }

        # 分页数据
        self.DEFAULT_PAGINATION = {
            "page": 1,
            "page_size": 10
        }

    def generate_unique_suffix(self) -> str:
        """生成唯一后缀

        Returns:
            唯一的后缀字符串
        """
        return os.urandom(4).hex()

    def get_admin_credentials(self) -> Dict[str, str]:
        """获取管理员凭据

        Returns:
            管理员用户名和密码字典
        """
        return self.ADMIN_CREDENTIALS.copy()

    def generate_shop_data(self, **overrides) -> Dict[str, Any]:
        """生成店铺测试数据

        Args:
            **overrides: 覆盖默认值的字段

        Returns:
            店铺数据字典
        """
        suffix = self.generate_unique_suffix()
        data = {
            "name": self.DEFAULT_SHOP["name_template"].format(suffix=suffix),
            "description": self.DEFAULT_SHOP["description"],
            "address": self.DEFAULT_SHOP["address"],
            "owner_username": f"shop_owner_{suffix}",
            "owner_password": self.DEFAULT_PASSWORD,
            "contact_phone": self.VALID_PHONE,
            "contact_email": f"shop_{suffix}@test.com"
        }
        data.update(overrides)
        return data

    def generate_product_data(self, shop_id, **overrides) -> Dict[str, Any]:
        """生成商品测试数据

        Args:
            shop_id: 店铺ID
            **overrides: 覆盖默认值的字段

        Returns:
            商品数据字典
        """
        suffix = self.generate_unique_suffix()
        data = {
            "shop_id": str(shop_id),
            "name": self.DEFAULT_PRODUCT["name_template"].format(suffix=suffix),
            "description": self.DEFAULT_PRODUCT["description"],
            "price": self.DEFAULT_PRODUCT["price"],
            "stock": self.DEFAULT_PRODUCT["stock"]
        }
        data.update(overrides)
        return data

    def generate_order_data(self, shop_id, user_id, product_id, **overrides) -> Dict[str, Any]:
        """生成订单测试数据

        Args:
            shop_id: 店铺ID
            user_id: 用户ID
            product_id: 商品ID
            **overrides: 覆盖默认值的字段

        Returns:
            订单数据字典
        """
        data = {
            "shop_id": str(shop_id),
            "user_id": str(user_id),
            "items": [{
                "product_id": str(product_id),
                "quantity": self.DEFAULT_ORDER["quantity"],
                "price": self.DEFAULT_ORDER["price"]
            }]
        }
        data.update(overrides)
        return data

    def generate_user_data(self, **overrides) -> Dict[str, Any]:
        """生成用户测试数据

        Args:
            **overrides: 覆盖默认值的字段

        Returns:
            用户数据字典
        """
        suffix = self.generate_unique_suffix()
        data = {
            "username": f"user_{suffix}",
            "password": self.DEFAULT_PASSWORD,
            "phone": f"13{suffix[:9]}",
            "role": "public_user"
        }
        data.update(overrides)
        return data

    def generate_tag_data(self, shop_id, **overrides) -> Dict[str, Any]:
        """生成标签测试数据

        Args:
            shop_id: 店铺ID
            **overrides: 覆盖默认值的字段

        Returns:
            标签数据字典
        """
        suffix = self.generate_unique_suffix()
        data = {
            "shop_id": str(shop_id),
            "name": f"Test Tag {suffix}",
            "color": "#FF5733"
        }
        data.update(overrides)
        return data


# 全局实例
test_data = TestDataConfig()
