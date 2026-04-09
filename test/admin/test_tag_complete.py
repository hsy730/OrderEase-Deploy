"""
标签管理接口测试（精简版 - 只包含核心CRUD）
"""

import pytest
import requests
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from conftest import API_BASE_URL, make_request_with_retry
import tag_actions


class TestAdminTagBasic:
    """管理员标签基本操作测试"""

    def test_create_tag(self, admin_token, test_shop_id):
        """测试创建标签"""
        shop_id = test_shop_id if test_shop_id else "1"
        tag_name = f"Test Tag {os.urandom(4).hex()}"

        tag_id = tag_actions.create_tag(admin_token, tag_name, shop_id)
        assert tag_id is not None, f"创建标签失败"

        if tag_id:
            tag_actions.delete_tag(admin_token, tag_id, shop_id)
        print(f"✓ 创建标签成功，ID: {tag_id}")

    def test_get_tag_list(self, admin_token):
        """测试获取标签列表"""
        tags = tag_actions.get_tag_list(admin_token, page=1, page_size=10)
        assert isinstance(tags, list), "标签列表应为数组类型"
        print(f"✓ 获取标签列表成功，数量: {len(tags)}")

    def test_get_bound_tags(self, admin_token, test_shop_id, test_product_id):
        """测试获取商品已绑定的标签"""
        shop_id = test_shop_id if test_shop_id else "1"
        product_id = test_product_id if test_product_id else 1

        tags = tag_actions.get_bound_tags(admin_token, product_id, shop_id)
        assert isinstance(tags, list), "已绑定标签列表应为数组类型"
        print(f"✓ 获取商品已绑定的标签成功，数量: {len(tags)}")

    def test_get_unbound_tags(self, admin_token, test_shop_id, test_product_id):
        """测试获取商品未绑定的标签"""
        shop_id = test_shop_id if test_shop_id else "1"
        product_id = test_product_id if test_product_id else 1

        tags = tag_actions.get_unbound_tags(admin_token, product_id, shop_id)
        assert isinstance(tags, list), "未绑定标签列表应为数组类型"
        print(f"✓ 获取商品未绑定的标签成功，数量: {len(tags)}")

    def test_get_online_products_for_tag(self, admin_token, test_shop_id, test_tag_id):
        """测试获取标签关联的已上架商品"""
        shop_id = test_shop_id if test_shop_id else "1"
        tag_id = test_tag_id if test_tag_id else 1

        products = tag_actions.get_online_products(admin_token, tag_id, shop_id)
        assert isinstance(products, list), "商品列表应为数组类型"
        print(f"✓ 获取标签关联的已上架商品成功，数量: {len(products)}")

    def test_get_unbound_tags_list(self, admin_token):
        """测试获取没有绑定商品的标签列表"""
        tags = tag_actions.get_unbound_tags_list(admin_token)
        assert isinstance(tags, list), "未绑定标签列表应为数组类型"
        print(f"✓ 获取没有绑定商品的标签列表成功，数量: {len(tags)}")


class TestShopOwnerTagBasic:
    """店主标签基本操作测试"""

    def test_create_tag(self, shop_owner_token, test_shop_id):
        """测试店主创建标签"""
        from shop_owner import tag_actions as owner_tag_actions

        shop_id = test_shop_id if test_shop_id else "1"
        tag_id = owner_tag_actions.create_tag(shop_owner_token, shop_id)
        assert tag_id is not None, f"店主创建标签失败"

        if tag_id:
            owner_tag_actions.delete_tag(shop_owner_token, tag_id, shop_id)
        print(f"✓ 店主创建标签成功，ID: {tag_id}")

    def test_get_bound_tags(self, shop_owner_token, test_shop_id, test_product_id):
        """测试店主获取商品已绑定的标签"""
        from shop_owner import tag_actions as owner_tag_actions

        shop_id = test_shop_id if test_shop_id else "1"
        product_id = test_product_id if test_product_id else 1

        tags = owner_tag_actions.get_bound_tags(shop_owner_token, product_id, shop_id)
        assert isinstance(tags, list), "已绑定标签列表应为数组类型"
        print(f"✓ 店主获取商品已绑定的标签成功，数量: {len(tags)}")
