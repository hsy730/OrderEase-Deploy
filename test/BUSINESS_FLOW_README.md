# 测试用例业务流程说明

## 问题背景

原有的测试用例存在业务逻辑顺序依赖问题：
- 创建店铺后才能创建商品
- 创建商品后才能创建订单
- 删除所有订单后才能删除商品
- 删除所有商品后才能删除店铺

但之前的测试文件（test_shop.py、test_product.py、test_order.py）是分离的，执行顺序不受控制，导致部分测试用例必然失败。

## 解决方案

### 1. 业务流程测试文件

创建了 `test_business_flow.py` 文件，将有关联的业务测试整合在一起，按照正确的业务顺序执行：

```
创建店铺 → 创建商品 → 创建订单 → 删除订单 → 删除商品 → 删除店铺
```

### 2. 原有测试文件处理

原有的测试文件（test_shop.py、test_product.py、test_order.py）已添加 `@pytest.mark.skip` 装饰器，标记为跳过，因为相关测试已整合到业务流程测试中。

### 3. 测试运行脚本

创建了 `run_business_flow_tests.py` 脚本，优先执行业务流程测试，然后执行其他独立的测试。

修改了 `run_all_tests.py` 脚本，使其调用新的业务流程测试脚本。

## 使用方法

### 运行业务流程测试

```bash
cd d:\local_code_repo\OrderEase-Deploy\test
python run_business_flow_tests.py
```

### 运行所有测试（优先业务流程）

```bash
cd d:\local_code_repo\OrderEase-Deploy\test
python run_all_tests.py
```

### 直接运行业务流程测试

```bash
cd d:\local_code_repo\OrderEase-Deploy\test
python -m pytest admin/test_business_flow.py -v
```

## 测试结果

测试结果将保存在以下文件中：
- `business_flow_test_results.json`: 业务流程测试的详细结果
- `business_flow_report.html`: 业务流程测试的HTML报告

## 注意事项

1. 业务流程测试使用临时创建的数据，测试完成后会自动清理，不会影响现有数据。
2. 如果业务流程测试失败，可能会影响后续的其他测试结果。
3. 如需单独测试原有功能，可以临时移除 `@pytest.mark.skip` 装饰器。