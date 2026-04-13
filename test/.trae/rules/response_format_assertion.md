# API 响应格式解析与断言规范

## 📋 概述

本规范定义了 OrderEase 项目测试代码中 **API 响应格式解析和断言** 的标准实践方式。

### 核心原则

**响应格式必须是确定的，不允许兼容多种格式。** 每个接口应该有且只有一种明确的响应格式，测试代码必须严格按照该格式进行解析和断言。

---

## ❌ 禁止的做法

### 1. 禁止兼容多种响应格式

```python
# ❌ 错误做法：兼容多种格式
if isinstance(json_data, dict):
    result = json_data.get("data")
    if result:
        return result
    elif "id" in json_data:
        return json_data
elif isinstance(json_data, list) and len(json_data) > 0:
    return json_data[0]
```

**问题**：
- 掩盖了接口响应格式不一致的问题
- 测试无法验证接口是否按照预期格式返回
- 增加了代码复杂度
- 可能导致错误的测试结果

### 2. 禁止模糊的类型检查

```python
# ❌ 错误做法：模糊的类型检查
data = response.json()
orders = data.get("data", data.get("orders", []))
```

**问题**：
- 不明确知道响应的实际结构
- 无法验证接口契约

### 3. 禁止静默失败

```python
# ❌ 错误做法：静默失败
result = json_data.get("data")
if result:
    return result
return None
```

**问题**：
- 无法区分"data字段不存在"和"data字段为空"的情况
- 测试可能通过但验证的是错误的数据

---

## ✅ 正确的做法

### 1. 明确响应格式断言

每个接口必须明确其响应格式，并在测试中断言该格式：

```python
# ✅ 正确做法：明确响应格式并断言
def get_order_detail(admin_token, order_id, shop_id):
    """获取订单详情
    
    响应格式（标准包装格式）：
    {
        "code": 200,
        "data": {
            "id": "xxx",
            "user_id": "xxx",
            ...
        }
    }
    """
    url = f"{API_BASE_URL}/admin/order/detail"
    params = {"id": str(order_id), "shop_id": str(shop_id)}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)

    if response.status_code == 200:
        json_data = response.json()
        
        # 1. 断言响应是字典类型
        assert isinstance(json_data, dict), f"响应必须是字典类型，实际是: {type(json_data)}"
        
        # 2. 断言包含code字段
        assert "code" in json_data, f"响应必须包含code字段，实际响应: {json_data}"
        assert json_data["code"] == 200, f"code必须是200，实际是: {json_data['code']}"
        
        # 3. 断言包含data字段
        assert "data" in json_data, f"响应必须包含data字段，实际响应: {json_data}"
        
        # 4. 断言data字段不为空
        result = json_data["data"]
        assert result is not None, f"data字段不能为None"
        
        # 5. 断言返回的数据包含预期的ID
        result_id = result.get("id")
        assert str(result_id) == str(order_id), f"返回的订单ID不匹配，期望: {order_id}，实际: {result_id}"
        
        return result
    else:
        raise AssertionError(f"获取订单详情失败，状态码: {response.status_code}, 响应: {response.text}")
```

### 2. 使用 ResponseValidator 工具类

```python
# ✅ 正确做法：使用 ResponseValidator
from utils.response_validator import ResponseValidator

def get_order_detail(admin_token, order_id, shop_id):
    """获取订单详情"""
    url = f"{API_BASE_URL}/admin/order/detail"
    params = {"id": str(order_id), "shop_id": str(shop_id)}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    
    # 使用 ResponseValidator 进行链式验证
    validator = ResponseValidator(response)
    validator.status(200) \
            .has_data() \
            .has_field("data.id") \
            .field_equals("data.id", order_id)
    
    return validator.get_data()
```

### 3. 测试用例中的严格断言

```python
# ✅ 正确做法：测试用例中严格断言响应格式
class TestOrderManagement:
    
    def test_get_order_detail(self, admin_token, test_order_id, test_shop_id):
        """测试获取订单详情 - 验证响应格式"""
        response = get_order_detail_response(admin_token, test_order_id, test_shop_id)
        
        # 1. 验证状态码
        assert response.status_code == 200, f"期望状态码200，实际: {response.status_code}"
        
        # 2. 解析响应
        data = response.json()
        
        # 3. 验证响应结构
        assert isinstance(data, dict), "响应必须是字典"
        assert "code" in data, "响应必须包含code字段"
        assert data["code"] == 200, f"code必须是200，实际: {data['code']}"
        assert "data" in data, "响应必须包含data字段"
        
        # 4. 验证业务数据
        order_data = data["data"]
        assert isinstance(order_data, dict), "data必须是字典"
        assert "id" in order_data, "订单必须包含id字段"
        assert order_data["id"] == test_order_id, f"订单ID不匹配"
        assert "user_id" in order_data, "订单必须包含user_id字段"
        assert "shop_id" in order_data, "订单必须包含shop_id字段"
        assert "items" in order_data, "订单必须包含items字段"
        assert isinstance(order_data["items"], list), "items必须是列表"
```

---

## 📐 响应格式标准

### 标准响应格式（推荐）

所有 API 应该遵循以下标准响应格式：

```json
{
    "code": 200,
    "message": "success",
    "data": {
        // 业务数据
    }
}
```

### 列表响应格式

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "list": [...],
        "total": 100,
        "page": 1,
        "pageSize": 10
    }
}
```

### 错误响应格式

```json
{
    "code": 400,
    "message": "错误描述",
    "error": "详细错误信息"
}
```

---

## 🔍 发现格式不一致时的处理流程

当测试发现接口响应格式与预期不符时：

### 步骤 1：记录实际响应

```python
# 在测试中添加调试信息
response = make_request_with_retry(request_func)
print(f"实际响应: {response.text}")
print(f"响应头: {response.headers}")
```

### 步骤 2：确认预期格式

- 查看接口文档
- 与后端开发人员确认
- 检查其他同类接口的格式

### 步骤 3：统一格式

**选择 A：修改后端接口**（推荐）
- 使接口符合标准响应格式
- 更新所有相关测试

**选择 B：修改测试代码**（仅当后端无法修改时）
- 更新测试代码以匹配实际格式
- 记录格式偏差原因

### 步骤 4：更新文档

- 更新接口文档
- 更新测试代码注释
- 记录格式规范

---

## 📝 代码审查清单

### 响应解析检查项

- [ ] **响应类型断言**：明确断言响应是字典类型
- [ ] **必需字段断言**：断言所有预期字段存在
- [ ] **字段类型断言**：断言字段类型正确（字符串、数字、列表等）
- [ ] **字段值断言**：断言关键字段值符合预期
- [ ] **嵌套结构断言**：断言嵌套对象结构正确
- [ ] **列表结构断言**：断言列表元素类型和结构

### 禁止项检查

- [ ] **无多格式兼容**：没有使用 `if-elif` 兼容多种格式
- [ ] **无模糊解析**：没有使用 `data.get("a", data.get("b"))` 模糊解析
- [ ] **无静默失败**：没有在失败时返回 None 而不报错
- [ ] **无不明确类型检查**：没有模糊的类型判断

---

## 💡 最佳实践

### 1. 每个接口明确文档化其响应格式

```python
def get_order_detail(admin_token, order_id, shop_id):
    """获取订单详情
    
    接口: GET /admin/order/detail
    
    请求参数:
        - id: 订单ID
        - shop_id: 店铺ID
    
    响应格式:
        {
            "code": 200,
            "data": {
                "id": "string",
                "user_id": "string",
                "shop_id": "string",
                "total_price": number,
                "status": number,
                "items": [
                    {
                        "id": "string",
                        "product_id": "string",
                        "quantity": number,
                        "price": number
                    }
                ],
                "created_at": "string",
                "updated_at": "string"
            }
        }
    
    异常响应:
        - 404: 订单不存在
        - 403: 无权访问该订单
    """
```

### 2. 使用数据类定义响应结构

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class OrderItem:
    id: str
    product_id: str
    quantity: int
    price: float

@dataclass
class Order:
    id: str
    user_id: str
    shop_id: str
    total_price: float
    status: int
    items: List[OrderItem]
    created_at: str
    updated_at: str

def parse_order_response(data: dict) -> Order:
    """解析订单响应数据"""
    assert "id" in data, "订单必须包含id"
    assert "user_id" in data, "订单必须包含user_id"
    # ... 更多断言
    
    items = [OrderItem(**item) for item in data.get("items", [])]
    return Order(items=items, **{k: v for k, v in data.items() if k != "items"})
```

### 3. 集中管理响应格式定义

```python
# config/response_schemas.py

ORDER_DETAIL_SCHEMA = {
    "type": "object",
    "required": ["code", "data"],
    "properties": {
        "code": {"type": "integer", "enum": [200]},
        "data": {
            "type": "object",
            "required": ["id", "user_id", "shop_id", "items"],
            "properties": {
                "id": {"type": "string"},
                "user_id": {"type": "string"},
                "shop_id": {"type": "string"},
                "total_price": {"type": "number"},
                "status": {"type": "integer"},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["id", "product_id", "quantity", "price"]
                    }
                }
            }
        }
    }
}
```

---

## 🚨 违规后果

不遵循此规范可能导致：

1. **测试不可靠**：接口格式变更时测试仍可能通过
2. **难以定位问题**：格式问题被兼容代码掩盖
3. **技术债务累积**：多种格式兼容代码难以维护
4. **接口契约模糊**：前后端对接口格式理解不一致

---

## ✅ 检查清单

编写新的测试代码时，请确认：

- [ ] 明确知道被测接口的响应格式
- [ ] 测试代码严格按照该格式解析
- [ ] 不包含多格式兼容代码
- [ ] 所有必需字段都有断言
- [ ] 字段类型有明确断言
- [ ] 关键业务值有验证
- [ ] 失败时提供详细的错误信息

---

**最后更新**: 2026-04-13  
**维护者**: 测试团队  
**版本**: v1.0
