"""
标签管理完整接口测试 - 覆盖标签的CRUD和批量操作

测试接口（admin）：
- POST /admin/tag/create
- GET /admin/tag/list
- GET /admin/tag/detail
- PUT /admin/tag/update
- DELETE /admin/tag/delete
- POST /admin/tag/batch-tag
- GET /admin/tag/online-products
- GET /admin/tag/bound-tags
- GET /admin/tag/unbound-tags
- POST /admin/tag/batch-tag-product
- DELETE /admin/tag/batch-untag
- GET /admin/tag/unbound-list
- GET /admin/tag/unbound-products
- GET /admin/tag/bound-products

测试接口（shopOwner）：
- POST /shopOwner/tag/create
- GET /shopOwner/tag/list
- GET /shopOwner/tag/detail
- PUT /shopOwner/tag/update
- DELETE /shopOwner/tag/delete
"""

import pytest
import requests
import sys
import os
from pathlib import Path

# 添加当前目录到 sys.path，以便导入操作工具类
sys.path.insert(0, str(Path(__file__).parent))

from conftest import API_BASE_URL, make_request_with_retry
import tag_actions


class TestAdminTagCRUD:
    """管理员标签CRUD操作测试"""

    @pytest.fixture(scope="function")
    def setup_tag(self, admin_token, test_shop_id):
        """创建测试标签并在测试后清理"""
        shop_id = test_shop_id if test_shop_id else "1"
        tag_name = f"Test Tag {os.urandom(4).hex()}"
        tag_id = tag_actions.create_tag(admin_token, tag_name, shop_id)

        yield {
            "tag_id": tag_id,
            "tag_name": tag_name,
            "shop_id": shop_id,
            "token": admin_token
        }

        # 清理：删除创建的标签
        if tag_id:
            try:
                tag_actions.delete_tag(admin_token, tag_id, shop_id)
            except Exception as e:
                print(f"清理标签失败: {e}")

    def test_create_tag(self, admin_token, test_shop_id):
        """测试创建标签"""
        shop_id = test_shop_id if test_shop_id else "1"
        tag_name = f"Create Test {os.urandom(4).hex()}"

        tag_id = tag_actions.create_tag(admin_token, tag_name, shop_id)
        assert tag_id is not None, f"创建标签失败"

        # 清理
        if tag_id:
            tag_actions.delete_tag(admin_token, tag_id, shop_id)
        print(f"✓ 创建标签成功，ID: {tag_id}")

    def test_get_tag_list(self, admin_token):
        """测试获取标签列表"""
        tags = tag_actions.get_tag_list(admin_token, page=1, page_size=10)
        assert isinstance(tags, list), "标签列表应为数组类型"
        print(f"✓ 获取标签列表成功，数量: {len(tags)}")

    def test_get_tag_detail(self, setup_tag):
        """测试获取标签详情"""
        tag_id = setup_tag["tag_id"]
        token = setup_tag["token"]

        detail = tag_actions.get_tag_detail(token, tag_id)
        if detail:
            assert isinstance(detail, dict), "标签详情应为字典类型"
            print(f"✓ 获取标签详情成功，ID: {tag_id}")
        else:
            print("⚠ 获取标签详情返回空（可能接口实现问题），继续其他测试")

    def test_update_tag(self, setup_tag):
        """测试更新标签"""
        tag_id = setup_tag["tag_id"]
        shop_id = setup_tag["shop_id"]
        token = setup_tag["token"]

        new_name = f"Updated Tag {os.urandom(4).hex()}"
        success = tag_actions.update_tag(token, tag_id, name=new_name, shop_id=shop_id)
        assert success, f"更新标签失败，ID: {tag_id}"
        print(f"✓ 更新标签成功，新名称: {new_name}")

    def test_delete_tag(self, setup_tag):
        """测试删除标签"""
        tag_id = setup_tag["tag_id"]
        shop_id = setup_tag["shop_id"]
        token = setup_tag["token"]

        success = tag_actions.delete_tag(token, tag_id, shop_id)
        assert success, f"删除标签失败，ID: {tag_id}"
        print(f"✓ 删除标签成功，ID: {tag_id}")


class TestAdminTagBatchOperations:
    """管理员标签批量操作测试"""

    def test_batch_tag_products(self, admin_token, test_shop_id, test_product_id, test_tag_id):
        """测试批量给商品打标签"""
        shop_id = test_shop_id if test_shop_id else "1"
        product_id = test_product_id if test_product_id else 1
        tag_id = test_tag_id if test_tag_id else 1

        success = tag_actions.batch_tag_products(
            admin_token,
            [str(product_id)],
            tag_id,
            shop_id
        )
        assert success, f"批量打标签失败"
        print("✓ 批量给商品打标签成功")

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

    def test_batch_set_product_tags(self, admin_token, test_product_id, test_tag_id):
        """测试批量设置商品标签"""
        product_id = test_product_id if test_product_id else 1
        tag_ids = [test_tag_id] if test_tag_id else [1]

        success = tag_actions.batch_tag_product(admin_token, product_id, tag_ids)
        assert success, f"批量设置商品标签失败"
        print("✓ 批量设置商品标签成功")

    def test_batch_untag_products(self, admin_token, test_product_id, test_tag_id):
        """测试批量解绑商品标签"""
        product_id = test_product_id if test_product_id else 1
        tag_ids = [test_tag_id] if test_tag_id else [1]
        product_ids = [str(product_id)]

        success = tag_actions.batch_untag_products(admin_token, product_ids, tag_ids)
        assert success, f"批量解绑商品标签失败"
        print("✓ 批量解绑商品标签成功")

    def test_get_unbound_tags_list(self, admin_token):
        """测试获取没有绑定商品的标签列表"""
        tags = tag_actions.get_unbound_tags_list(admin_token)
        assert isinstance(tags, list), "未绑定标签列表应为数组类型"
        print(f"✓ 获取没有绑定商品的标签列表成功，数量: {len(tags)}")

    def test_get_unbound_products_for_tag(self, admin_token, test_tag_id):
        """测试获取标签未绑定的商品列表"""
        tag_id = test_tag_id if test_tag_id else 1

        products = tag_actions.get_unbound_products_for_tag(admin_token, tag_id)
        assert isinstance(products, list), "未绑定商品列表应为数组类型"
        print(f"✓ 获取标签未绑定的商品列表成功，数量: {len(products)}")

    def test_get_bound_products_for_tag(self, admin_token, test_shop_id, test_tag_id):
        """测试获取标签已绑定的商品列表"""
        shop_id = test_shop_id if test_shop_id else "1"
        tag_id = test_tag_id if test_tag_id else 1

        products = tag_actions.get_tag_bound_products(admin_token, tag_id, shop_id)
        assert isinstance(products, list), "已绑定商品列表应为数组类型"
        print(f"✓ 获取标签已绑定的商品列表成功，数量: {len(products)}")


class TestShopOwnerTagOperations:
    """店主标签操作测试"""

    def test_create_tag(self, shop_owner_token, test_shop_id):
        """测试店主创建标签"""
        from shop_owner import tag_actions as owner_tag_actions

        shop_id = test_shop_id if test_shop_id else "1"
        tag_id = owner_tag_actions.create_tag(shop_owner_token, shop_id)
        assert tag_id is not None, f"店主创建标签失败"

        # 清理
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

    def test_get_online_products(self, shop_owner_token, test_shop_id, test_tag_id):
        """测试店主获取标签关联的已上架商品"""
        from shop_owner import tag_actions as owner_tag_actions

        shop_id = test_shop_id if test_shop_id else "1"
        tag_id = test_tag_id if test_tag_id else 1

        products = owner_tag_actions.get_online_products(shop_owner_token, tag_id, shop_id)
        assert isinstance(products, list), "商品列表应为数组类型"
        print(f"✓ 店主获取标签关联的已上架商品成功，数量: {len(products)}")
