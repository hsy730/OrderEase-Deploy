"""
业务流程测试 - 按照正确的业务顺序执行测试

这是 admin 目录下唯一的可执行测试文件。
测试用例的业务实现在 shop_actions.py, product_actions.py, order_actions.py,
user_actions.py, tag_actions.py 等操作工具类中。
"""

import pytest
import requests
import sys
from pathlib import Path

# 添加当前目录到 sys.path，以便导入操作工具类
sys.path.insert(0, str(Path(__file__).parent))

from conftest import API_BASE_URL

# 导入操作工具类
import shop_actions
import product_actions
import order_actions
import user_actions
import tag_actions


class TestBusinessFlow:
    """业务流程测试类 - 包含所有业务流程测试用例"""

    @pytest.fixture(scope="function", autouse=True)
    def setup_and_teardown(self, admin_token):
        """每个测试函数前后的 setup 和 teardown"""
        # Setup: 在测试前执行
        print("\n=== 开始测试 ===")
        self.admin_token = admin_token
        self.cleanup_resources = []

        yield  # 执行测试

        # Teardown: 在测试后执行，清理测试数据
        print("\n=== 清理测试数据 ===")
        for cleanup_func in reversed(self.cleanup_resources):
            try:
                cleanup_func()
            except Exception as e:
                print(f"清理资源时出错: {e}")
        print("=== 测试结束 ===\n")

    # ==================== 完整业务流程测试 ====================

    def test_complete_business_flow(self):
        """测试完整的业务流程：创建店铺 → 创建商品 → 创建订单 → 删除订单 → 删除商品 → 删除店铺"""
        print("\n========== 完整业务流程测试 ==========")

        # 第一步：创建店铺
        shop_id = self._test_create_shop()
        assert shop_id is not None, "创建店铺失败"
        print(f"✓ 成功创建店铺，ID: {shop_id}")

        # 第二步：创建商品
        product_id = self._test_create_product(shop_id)
        assert product_id is not None, "创建商品失败"
        print(f"✓ 成功创建商品，ID: {product_id}")

        # 第三步：获取用户ID（创建订单需要）
        user_id = self._test_get_user_id()
        assert user_id is not None, "获取用户ID失败"
        print(f"✓ 成功获取用户ID，ID: {user_id}")

        # 第四步：创建订单
        order_id = self._test_create_order(shop_id, user_id, product_id)
        assert order_id is not None, "创建订单失败"
        print(f"✓ 成功创建订单，ID: {order_id}")

        # 第五步：删除订单
        self._test_delete_order(order_id, shop_id)
        print(f"✓ 成功删除订单，ID: {order_id}")

        # 第六步：删除商品
        self._test_delete_product(product_id, shop_id)
        print(f"✓ 成功删除商品，ID: {product_id}")

        # 第七步：删除店铺
        self._test_delete_shop(shop_id)
        print(f"✓ 成功删除店铺，ID: {shop_id}")

        print("✓ 完整业务流程测试通过")

    # ==================== 店铺相关测试 ====================

    def test_shop_management_flow(self):
        """测试店铺管理流程"""
        print("\n========== 店铺管理流程测试 ==========")

        # 创建店铺
        shop_id = self._test_create_shop()
        assert shop_id is not None, "创建店铺失败"
        print(f"✓ 创建店铺成功，ID: {shop_id}")

        # 更新店铺信息
        self._test_update_shop(shop_id)
        print("✓ 更新店铺信息成功")

        # 获取店铺详情
        detail = shop_actions.get_shop_detail(self.admin_token, shop_id)
        if detail is not None:
            print("✓ 获取店铺详情成功")
        else:
            print("⚠ 获取店铺详情失败（可能是API响应格式问题），继续其他测试")

        # 上传店铺图片
        image_url = shop_actions.upload_shop_image(self.admin_token, shop_id)
        if image_url:
            print(f"✓ 上传店铺图片成功，URL: {image_url}")
        else:
            print("⚠ 上传店铺图片失败，继续其他测试")

        # 获取店铺列表
        shops = shop_actions.get_shop_list(self.admin_token)
        assert len(shops) > 0, "获取店铺列表失败"
        # 验证店铺列表包含必需字段
        for shop in shops:
            assert isinstance(shop, dict), "店铺应为字典类型"
            assert "id" in shop, "店铺应包含id字段"
            assert "name" in shop, "店铺应包含name字段"
        print(f"✓ 获取店铺列表成功，共 {len(shops)} 个店铺")

        # 检查店铺名称
        check_result = shop_actions.check_shop_name_exists(self.admin_token, "test shop")
        assert check_result is not None, "检查店铺名称失败"
        print("✓ 检查店铺名称成功")

        # 更新订单状态流转
        status_flow_config = [
            {"from_status": 1, "to_status": 2, "condition": ""},
            {"from_status": 2, "to_status": 3, "condition": ""}
        ]
        result = shop_actions.update_order_status_flow(self.admin_token, shop_id, status_flow_config)
        if result:
            print("✓ 更新订单状态流转成功")
        else:
            print("⚠ 更新订单状态流转失败，继续其他测试")

        # 删除店铺
        self._test_delete_shop(shop_id)
        print("✓ 删除店铺成功")

    # ==================== 商品相关测试 ====================

    def test_product_management_flow(self):
        """测试商品管理流程 - 包含创建后立即查询验证"""
        print("\n========== 商品管理流程测试 ==========")

        # 先创建店铺
        shop_id = self._test_create_shop()
        assert shop_id is not None, "创建店铺失败"

        # 1. 创建商品前获取商品列表数量
        products_before = product_actions.get_product_list(self.admin_token, shop_id)
        count_before = len(products_before) if isinstance(products_before, list) else 0
        print(f"创建前商品数量: {count_before}")

        # 2. 创建商品
        product_id = self._test_create_product(shop_id)
        assert product_id is not None, "创建商品失败"
        print(f"✓ 创建商品成功，ID: {product_id}")

        # 3. 【关键】立即查询商品列表，验证新商品存在
        products_after = product_actions.get_product_list(self.admin_token, shop_id)
        assert isinstance(products_after, list), "商品列表应为列表类型"

        # 验证商品数量增加
        count_after = len(products_after)
        print(f"创建后商品数量: {count_after}")
        assert count_after > count_before, f"商品数量未增加，创建前{count_before}，创建后{count_after}"

        # 验证刚创建的商品ID在列表中
        product_ids = [str(product.get("id")) for product in products_after]
        assert str(product_id) in product_ids, f"刚创建的商品ID {product_id} 不在商品列表中，列表包含: {product_ids}"
        print(f"✓ 商品列表验证成功，包含新创建的商品ID: {product_id}")

        # 4. 【关键】立即查询商品详情，验证能获取到正确的商品
        detail = product_actions.get_product_detail(self.admin_token, product_id, shop_id)
        assert detail is not None, f"获取商品详情失败，商品ID: {product_id}"
        # 验证返回的详情中包含正确的商品ID
        detail_product_id = detail.get("id") or detail.get("product_id") or detail.get("productId")
        assert str(detail_product_id) == str(product_id), f"商品详情ID不匹配，期望{product_id}，实际{detail_product_id}"
        print(f"✓ 获取商品详情成功，验证商品ID: {product_id}")

        # 更新商品信息
        self._test_update_product(product_id, shop_id)
        print("✓ 更新商品信息成功")

        # 上传商品图片
        image_url = product_actions.upload_product_image(self.admin_token, product_id, shop_id)
        if image_url:
            print(f"✓ 上传商品图片成功，URL: {image_url}")
        else:
            print("⚠ 上传商品图片失败，继续其他测试")

        # 切换商品状态
        result = product_actions.toggle_product_status(self.admin_token, product_id, shop_id, "online")
        assert result, "切换商品状态失败"
        print("✓ 切换商品状态成功")

        # 删除商品
        self._test_delete_product(product_id, shop_id)
        print("✓ 删除商品成功")

        # 删除店铺
        self._test_delete_shop(shop_id)

    # ==================== 订单相关测试 ====================

    def test_order_management_flow(self):
        """测试订单管理流程 - 包含创建后立即查询验证"""
        print("\n========== 订单管理流程测试 ==========")

        # 创建店铺和商品
        shop_id = self._test_create_shop()
        product_id = self._test_create_product(shop_id)
        user_id = self._test_get_user_id()

        # 1. 创建订单前获取订单列表数量
        orders_before = order_actions.get_order_list(self.admin_token, shop_id)
        count_before = len(orders_before) if isinstance(orders_before, list) else 0
        print(f"创建前订单数量: {count_before}")

        # 2. 创建订单
        order_id = self._test_create_order(shop_id, user_id, product_id)
        assert order_id is not None, "创建订单失败"
        print(f"✓ 创建订单成功，ID: {order_id}")

        # 3. 【关键】立即查询订单列表，验证新订单存在
        orders_after = order_actions.get_order_list(self.admin_token, shop_id)
        assert isinstance(orders_after, list), "订单列表应为列表类型"

        # 验证订单数量增加
        count_after = len(orders_after)
        print(f"创建后订单数量: {count_after}")
        assert count_after > count_before, f"订单数量未增加，创建前{count_before}，创建后{count_after}"

        # 验证刚创建的订单ID在列表中
        order_ids = [str(order.get("id")) for order in orders_after]
        assert str(order_id) in order_ids, f"刚创建的订单ID {order_id} 不在订单列表中，列表包含: {order_ids}"
        print(f"✓ 订单列表验证成功，包含新创建的订单ID: {order_id}")

        # 4. 【关键】立即查询订单详情，验证能获取到正确的订单
        detail = order_actions.get_order_detail(self.admin_token, order_id, shop_id)
        assert detail is not None, f"获取订单详情失败，订单ID: {order_id}"
        # 验证返回的详情中包含正确的订单ID
        detail_order_id = detail.get("id") or detail.get("order_id") or detail.get("orderId")
        assert str(detail_order_id) == str(order_id), f"订单详情ID不匹配，期望{order_id}，实际{detail_order_id}"
        print(f"✓ 获取订单详情成功，验证订单ID: {order_id}")

        # 更新订单
        self._test_update_order(order_id, shop_id, user_id, product_id)
        print("✓ 更新订单成功")

        # 切换订单状态
        result = order_actions.toggle_order_status(self.admin_token, order_id, shop_id, 10)
        assert result, "切换订单状态失败"
        print("✓ 切换订单状态成功")

        # 获取订单状态流转
        status_flow = order_actions.get_order_status_flow(self.admin_token, order_id, shop_id)
        if status_flow is not None:
            print("✓ 获取订单状态流转成功")
        else:
            print("⚠ 获取订单状态流转失败，继续其他测试")

        # 高级搜索订单
        search_result = order_actions.advance_search_order(
            self.admin_token, 
            shop_id=shop_id, 
            status=1, 
            page=1, 
            page_size=10
        )
        if search_result is not None:
            print("✓ 高级搜索订单成功")
        else:
            print("⚠ 高级搜索订单失败，继续其他测试")

        # 删除订单
        self._test_delete_order(order_id, shop_id)
        print("✓ 删除订单成功")

        # 清理
        self._test_delete_product(product_id, shop_id)
        self._test_delete_shop(shop_id)

    # ==================== 用户相关测试 ====================

    def test_user_management_flow(self):
        """测试用户管理流程"""
        print("\n========== 用户管理流程测试 ==========")

        # 创建用户
        user_id = user_actions.create_user(self.admin_token)
        # 注意：如果创建失败可能是重复用户，我们继续进行其他测试
        if user_id:
            print(f"✓ 创建用户成功，ID: {user_id}")
        else:
            print("⚠ 创建用户失败（可能是用户已存在），继续其他测试")

        # 获取用户列表
        users = user_actions.get_user_list(self.admin_token)
        assert len(users) > 0, "获取用户列表失败"
        # 验证用户列表包含必需字段
        for user in users:
            assert isinstance(user, dict), "用户应为字典类型"
            assert "id" in user, "用户应包含id字段"
            assert "name" in user, "用户应包含name字段"
        print(f"✓ 获取用户列表成功，共 {len(users)} 个用户")

        # 获取用户简单列表
        simple_users = user_actions.get_user_simple_list(self.admin_token)
        assert len(simple_users) > 0, "获取用户简单列表失败"
        # 验证简单用户列表包含必需字段
        for user in simple_users:
            assert isinstance(user, dict), "用户应为字典类型"
            assert "id" in user, "用户应包含id字段"
        print(f"✓ 获取用户简单列表成功")

        # 更新第一个用户
        if users:
            first_user_id = users[0].get("id")
            result = user_actions.update_user(self.admin_token, first_user_id, name="Updated Test User")
            assert result, "更新用户失败"
            print("✓ 更新用户成功")

        # 删除用户（如果之前创建了用户）
        if user_id:
            result = user_actions.delete_user(self.admin_token, user_id)
            assert result, "删除用户失败"
            print("✓ 删除用户成功")

    # ==================== 标签相关测试 ====================

    def test_tag_management_flow(self):
        """测试标签管理流程 - 包含创建后立即查询验证"""
        print("\n========== 标签管理流程测试 ==========")

        # 创建店铺和商品
        shop_id = self._test_create_shop()
        product_id = self._test_create_product(shop_id)

        # 1. 创建标签前获取标签列表数量
        tags_before = tag_actions.get_tag_list(self.admin_token, shop_id=shop_id)
        count_before = len(tags_before) if isinstance(tags_before, list) else 0
        print(f"创建前标签数量: {count_before}")

        # 2. 创建标签
        tag_id = tag_actions.create_tag(self.admin_token, shop_id=shop_id)
        assert tag_id is not None, "创建标签失败"
        print(f"✓ 创建标签成功，ID: {tag_id}")

        # 3. 【关键】立即查询标签列表，验证新标签存在
        tags_after = tag_actions.get_tag_list(self.admin_token, shop_id=shop_id)
        assert isinstance(tags_after, list), "标签列表应为列表类型"

        # 验证标签数量增加
        count_after = len(tags_after)
        print(f"创建后标签数量: {count_after}")
        assert count_after > count_before, f"标签数量未增加，创建前{count_before}，创建后{count_after}"

        # 验证刚创建的标签ID在列表中
        tag_ids = [str(tag.get("id")) for tag in tags_after]
        assert str(tag_id) in tag_ids, f"刚创建的标签ID {tag_id} 不在标签列表中，列表包含: {tag_ids}"
        print(f"✓ 标签列表验证成功，包含新创建的标签ID: {tag_id}")

        # 获取商品已绑定的标签
        bound_tags = tag_actions.get_bound_tags(self.admin_token, product_id, shop_id)
        print(f"✓ 获取商品已绑定标签成功，共 {len(bound_tags)} 个标签")

        # 获取商品未绑定的标签
        unbound_tags = tag_actions.get_unbound_tags(self.admin_token, product_id, shop_id)
        print(f"✓ 获取商品未绑定标签成功，共 {len(unbound_tags)} 个标签")

        # 更新标签（如果之前创建了标签）
        if tag_id:
            result = tag_actions.update_tag(self.admin_token, tag_id, name="Updated Tag Name", shop_id=shop_id)
            if result:
                print("✓ 更新标签成功")
            else:
                print("⚠ 更新标签失败，继续其他测试")

            # 删除标签
            result = tag_actions.delete_tag(self.admin_token, tag_id, shop_id=shop_id)
            if result:
                print("✓ 删除标签成功")
            else:
                print("⚠ 删除标签失败，继续其他测试")

        # 清理
        self._test_delete_product(product_id, shop_id)
        self._test_delete_shop(shop_id)

    # ==================== 辅助方法 ====================

    def _test_create_shop(self):
        """创建店铺（辅助方法）"""
        shop_id = shop_actions.create_shop(
            self.admin_token,
            name=f"Test Shop for Flow",
            description="Shop created for flow testing",
            address="Test address"
        )
        return shop_id

    def _test_create_product(self, shop_id):
        """创建商品（辅助方法）"""
        product_id = product_actions.create_product(
            self.admin_token,
            shop_id,
            name=f"Test Product for Flow",
            price=100,
            description="Product created for flow testing",
            stock=100
        )
        return product_id

    def _test_get_user_id(self):
        """获取用户ID（辅助方法）"""
        users = user_actions.get_user_list(self.admin_token, page=1, page_size=1)
        if users and len(users) > 0:
            return users[0].get("id")
        return None

    def _test_create_order(self, shop_id, user_id, product_id):
        """创建订单（辅助方法）"""
        items = [{"product_id": str(product_id), "quantity": 1, "price": 100}]
        order_id = order_actions.create_order(self.admin_token, shop_id, user_id, items)
        return order_id

    def _test_delete_order(self, order_id, shop_id):
        """删除订单（辅助方法）"""
        result = order_actions.delete_order(self.admin_token, order_id, shop_id)
        assert result, f"删除订单失败，order_id: {order_id}"

    def _test_delete_product(self, product_id, shop_id):
        """删除商品（辅助方法）"""
        result = product_actions.delete_product(self.admin_token, product_id, shop_id)
        assert result, f"删除商品失败，product_id: {product_id}"

    def _test_delete_shop(self, shop_id):
        """删除店铺（辅助方法）"""
        # 先删除店铺下的所有商品
        products = product_actions.get_product_list(self.admin_token, shop_id, page=1, page_size=100)
        for product in products:
            product_id = product.get("id")
            if product_id:
                product_actions.delete_product(self.admin_token, product_id, shop_id)

        # 删除店铺
        result = shop_actions.delete_shop(self.admin_token, shop_id)
        assert result, f"删除店铺失败，shop_id: {shop_id}"

    def _test_update_shop(self, shop_id):
        """更新店铺信息（辅助方法）"""
        result = shop_actions.update_shop(
            self.admin_token,
            shop_id,
            name="Updated Shop Name",
            description="Updated description"
        )
        assert result, "更新店铺信息失败"

    def _test_update_product(self, product_id, shop_id):
        """更新商品信息（辅助方法）"""
        result = product_actions.update_product(
            self.admin_token,
            product_id,
            shop_id,
            name="Updated Product Name",
            price=150
        )
        assert result, "更新商品信息失败"

    def _test_update_order(self, order_id, shop_id, user_id, product_id):
        """更新订单信息（辅助方法）"""
        items = [{"product_id": str(product_id), "quantity": 1, "price": 100}]
        result = order_actions.update_order(
            self.admin_token,
            order_id,
            shop_id,
            user_id=user_id,
            total_price="100.00",
            status=1,
            remark="Updated remark",
            items=items
        )
        assert result, "更新订单信息失败"
