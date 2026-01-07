# Admin 测试目录说明

## 目录结构

本目录包含 OrderEase 管理员 API 的所有测试用例。

### 文件说明

#### 可执行测试文件
- **`test_business_flow.py`** - 唯一的可执行测试文件
  - 包含所有业务流程测试用例
  - 使用 pytest 的 setup/teardown 管理测试环境
  - 按照业务依赖顺序执行测试

#### 操作工具类（静态文件）
- **`shop_actions.py`** - 店铺相关业务操作函数
- **`product_actions.py`** - 商品相关业务操作函数
- **`order_actions.py`** - 订单相关业务操作函数
- **`user_actions.py`** - 用户相关业务操作函数
- **`tag_actions.py`** - 标签相关业务操作函数

这些文件提供可调用的业务操作函数，供 `test_business_flow.py` 使用。

#### 已废弃的测试文件（保留用于参考）
以下文件已不再作为测试执行，仅保留用于参考：
- **`test_shop.py`** - 已重构为 `shop_actions.py`
- **`test_product.py`** - 已重构为 `product_actions.py`
- **`test_order.py`** - 已重构为 `order_actions.py`
- **`test_user.py`** - 已重构为 `user_actions.py`
- **`test_tag.py`** - 已重构为 `tag_actions.py`
- **`test_base.py`** - 已整合到 `test_business_flow.py`

这些文件开头添加了 `__test__ = False`，pytest 不会收集其中的测试用例。

## 如何运行测试

### 运行所有测试
```bash
cd d:/local_code_repo/OrderEase-Deploy/test/admin
pytest test_business_flow.py -v
```

### 运行特定测试用例
```bash
# 运行完整业务流程测试
pytest test_business_flow.py::TestBusinessFlow::test_complete_business_flow -v

# 运行店铺管理流程测试
pytest test_business_flow.py::TestBusinessFlow::test_shop_management_flow -v

# 运行商品管理流程测试
pytest test_business_flow.py::TestBusinessFlow::test_product_management_flow -v

# 运行订单管理流程测试
pytest test_business_flow.py::TestBusinessFlow::test_order_management_flow -v

# 运行用户管理流程测试
pytest test_business_flow.py::TestBusinessFlow::test_user_management_flow -v

# 运行标签管理流程测试
pytest test_business_flow.py::TestBusinessFlow::test_tag_management_flow -v
```

### 查看测试输出详情
```bash
pytest test_business_flow.py -v -s
```

## 测试流程说明

### test_complete_business_flow
完整业务流程测试，按照以下顺序执行：
1. 创建店铺
2. 创建商品
3. 获取用户ID
4. 创建订单
5. 删除订单
6. 删除商品
7. 删除店铺

### test_shop_management_flow
店铺管理流程测试，包含：
- 创建店铺
- 更新店铺信息
- 获取店铺详情
- 上传店铺图片
- 获取店铺列表
- 检查店铺名称
- 删除店铺

### test_product_management_flow
商品管理流程测试，包含：
- 创建店铺（前提）
- 创建商品
- 获取商品列表
- 获取商品详情
- 更新商品信息
- 上传商品图片
- 切换商品状态
- 删除商品
- 删除店铺（清理）

### test_order_management_flow
订单管理流程测试，包含：
- 创建店铺和商品（前提）
- 创建订单
- 获取订单列表
- 获取订单详情
- 更新订单
- 切换订单状态
- 删除订单
- 清理资源

### test_user_management_flow
用户管理流程测试，包含：
- 创建用户
- 获取用户列表
- 获取用户简单列表
- 更新用户

### test_tag_management_flow
标签管理流程测试，包含：
- 创建店铺和商品（前提）
- 创建标签
- 获取商品已绑定标签
- 获取商品未绑定标签
- 清理资源

## Setup 和 Teardown

每个测试用例都会自动执行 setup 和 teardown：
- **Setup**: 初始化 admin_token，创建清理资源列表
- **Teardown**: 按相反顺序清理所有创建的资源（店铺、商品、订单等）

这种设计确保测试数据的完整性和隔离性。

## 操作工具类使用示例

```python
import shop_actions
from conftest import admin_token

# 创建店铺
shop_id = shop_actions.create_shop(
    admin_token,
    name="Test Shop",
    description="Test description"
)

# 获取店铺列表
shops = shop_actions.get_shop_list(admin_token, page=1, page_size=10)

# 删除店铺
result = shop_actions.delete_shop(admin_token, shop_id)
```

其他操作工具类的使用方式类似，详见各文件的函数文档字符串。
