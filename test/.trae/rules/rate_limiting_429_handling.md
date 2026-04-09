# 429 限流处理规范

## 📋 概述

本规范定义了 OrderEase 项目测试代码中 **HTTP 429 (Too Many Requests) 限流错误** 的标准处理方式。

### 什么是 429 限流？

当 API 服务器在短时间内收到过多请求时，会返回 **HTTP 429 状态码**，表示请求过于频繁。这是服务器的保护机制，防止系统过载。

---

## ✅ 标准处理方式：指数退避重试

### 核心原则

**必须使用 `make_request_with_retry()` 函数** 处理所有 API 请求，该函数内置了 429 限流的自动重试机制。

### 实现细节

```python
def make_request_with_retry(request_func, max_retries=10, initial_wait=1, backoff_factor=2):
    """
    执行请求，如果遇到429则等待后重试（最多重试max_retries次）

    Args:
        request_func: 请求函数（无参数的callable）
        max_retries: 最大重试次数（默认10次）
        initial_wait: 初始等待时间（秒，默认1秒）
        backoff_factor: 退避因子，每次重试等待时间乘以这个因子（默认2）

    Returns:
        response: 最终的响应对象

    行为：
        - 遇到429状态码时自动重试
        - 使用指数退避策略：1s → 2s → 4s → 8s → ...
        - 最多重试10次后返回最后一次响应
        - 打印详细的重试日志
    """
```

### 重试策略详解

| 重试次数 | 等待时间 | 累计等待 |
|---------|---------|---------|
| 第1次 | 1秒 | 1秒 |
| 第2次 | 2秒 | 3秒 |
| 第3次 | 4秒 | 7秒 |
| 第4次 | 8秒 | 15秒 |
| 第5次 | 16秒 | 31秒 |
| ... | ... | ... |
| 第10次 | 512秒 | **1023秒 (~17分钟)** |

---

## 🔧 正确使用示例

### ✅ 基础用法（所有API调用必须遵循此模式）

```python
import requests
from conftest import API_BASE_URL, make_request_with_retry

# ❌ 错误做法：直接发送请求（不处理429）
def test_wrong_approach():
    url = f"{API_BASE_URL}/admin/shop/list"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)  # 可能遇到429！
    assert response.status_code == 200

# ✅ 正确做法：使用make_request_with_retry包装请求
def test_correct_approach(token):
    url = f"{API_BASE_URL}/admin/shop/list"
    params = {"page": 1, "pageSize": 10}
    headers = {"Authorization": f"Bearer {token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    assert response.status_code == 200
```

### ✅ POST/PUT/DELETE 请求示例

```python
def create_shop(admin_token, shop_data):
    """创建店铺"""
    url = f"{API_BASE_URL}/admin/shop/create"
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.post(url, json=shop_data, headers=headers)

    response = make_request_with_retry(request_func)

    if response.status_code == 200:
        return response.json().get("id")
    return None


def update_product(admin_token, product_id, update_data):
    """更新商品"""
    url = f"{API_BASE_URL}/admin/product/update"
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.put(url, json=update_data, headers=headers)

    response = make_request_with_retry(request_func)
    assert response.status_code == 200, f"更新商品失败: {response.text}"
```

### ✅ 文件上传示例

```python
def upload_image(token, file_path):
    """上传图片"""
    url = f"{API_BASE_URL}/admin/product/upload-image"
    headers = {"Authorization": f"Bearer {token}"}

    with open(file_path, 'rb') as f:
        files = {'file': ('image.jpg', f, 'image/jpeg')}

        def request_func():
            return requests.post(url, files=files, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 200
```

---

## ⚠️ 常见错误及纠正

### ❌ 错误1：直接使用 requests 库

```python
# 错误代码
def get_shops(token):
    url = f"{API_BASE_URL}/admin/shop/list"
    response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    return response.json()  # 如果遇到429会直接失败！

# 正确代码
def get_shops(token):
    url = f"{API_BASE_URL}/admin/shop/list"

    def request_func():
        return requests.get(url, headers={"Authorization": f"Bearer {token}"})

    response = make_request_with_retry(request_func)
    return response.json()
```

### ❌ 错误2：手动实现简单的 sleep 重试

```python
# 错误代码（没有指数退避，效率低）
def get_orders_bad():
    for i in range(5):
        response = requests.get(url)
        if response.status_code != 429:
            break
        time.sleep(1)  # 固定等待，不够灵活

# 正确代码（使用标准的make_request_with_retry）
def get_orders_good():
    def request_func():
        return requests.get(url)

    response = make_request_with_retry(request_func)
    return response
```

### ❌ 错误3：忽略429错误

```python
# 错误代码（静默失败）
try:
    response = requests.post(url, json=data)
except:
    pass  # 吞掉所有错误！

# 正确代码（让make_request_with_retry处理429，其他错误正常抛出）
def request_func():
    return requests.post(url, json=data)

response = make_request_with_retry(request_func)
assert response.status_code == 200, f"请求失败: {response.text}"
```

---

## 🎯 最佳实践清单

### ✅ 必须遵守的规则

1. **所有 HTTP 请求都必须使用 `make_request_with_retry()` 包装**
   - 包括 GET、POST、PUT、DELETE、PATCH
   - 包括文件上传下载
   - 无一例外

2. **使用函数式编程风格**
   ```python
   def request_func():
       return requests.xxx(...)

   response = make_request_with_retry(request_func)
   ```

3. **在断言前检查响应**
   ```python
   response = make_request_with_retry(request_func)
   assert response.status_code == 200, f"操作失败: {response.text}"
   ```

4. **提供有意义的错误信息**
   ```python
   assert response.status_code == 200, f"创建订单失败: {response.text}"
   # 而不是
   assert response.status_code == 200
   ```

### 💡 推荐的做法

#### 1. 在 action 工具类中使用

```python
# tag_actions.py
def create_tag(admin_token, name, shop_id):
    """创建标签"""
    url = f"{API_BASE_URL}/admin/tag/create"
    payload = {"name": name, "shop_id": shop_id}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.post(url, json=payload, headers=headers)

    response = make_request_with_retry(request_func)

    if response.status_code == 200:
        validator = ResponseValidator(response)
        return validator.extract_id()
    return None
```

#### 2. 在测试用例中使用

```python
class TestTagManagement:

    def test_create_tag(self, admin_token, test_shop_id):
        """测试创建标签"""
        url = f"{API_BASE_URL}/admin/tag/create"
        payload = {
            "name": f"Test Tag {os.urandom(4).hex()}",
            "shop_id": str(test_shop_id)
        }
        headers = {"Authorization": f"Bearer {admin_token}"}

        def request_func():
            return requests.post(url, json=payload, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"创建标签失败: {response.text}"

        data = response.json()
        tag_id = data.get("id") or data.get("tagId")
        assert tag_id is not None, "未能获取标签ID"
```

#### 3. 在 fixture 中使用

```python
@pytest.fixture(scope="session")
def test_shop_id(admin_token):
    """获取测试店铺ID"""
    url = f"{API_BASE_URL}/admin/shop/list"
    params = {"page": 1, "pageSize": 1}
    headers = {"Authorization": f"Bearer {admin_token}"}

    def request_func():
        return requests.get(url, params=params, headers=headers)

    response = make_request_with_retry(request_func)
    if response.status_code == 200:
        shops = response.json().get("data", [])
        if shops:
            return shops[0].get("id")
    return None
```

---

## 📊 性能考虑

### 为什么选择指数退避？

1. **避免雪崩效应**：固定间隔重试可能导致所有客户端同时重试
2. **给服务器恢复时间**：随着重试次数增加，等待时间变长
3. **平衡速度与成功率**：初期快速重试，后期耐心等待

### 参数调优建议

| 场景 | max_retries | initial_wait | backoff_factor |
|------|-------------|---------------|----------------|
| 一般API调用 | 10 | 1s | 2 | ✅ 默认值 |
| 批量导入导出 | 15 | 2s | 2 | 📦 大量数据 |
| 高频测试套件 | 20 | 0.5s | 1.5 | ⚡ 快速执行 |
| CI/CD环境 | 12 | 1s | 2.5 | 🏗️ 稳定性优先 |

---

## 🔍 调试技巧

### 查看429重试日志

`make_request_with_retry()` 会自动打印重试信息：

```
[WARN] 请求过于频繁（429），等待 1 秒后重试（第 1/10 次）
[WARN] 请求过于频繁（429），等待 2 秒后重试（第 2/10 次）
[OK] 重试完成，最终状态码: 200
```

### 统计429发生频率

如果频繁遇到429，可以考虑：

1. **增加测试之间的延迟**
   ```python
   import time
   time.sleep(0.5)  # 在每个测试之间添加小延迟
   ```

2. **优化测试顺序**
   - 将高频访问的接口分散开
   - 避免连续调用同一接口

3. **调整服务器限流配置**
   - 在生产环境中适当放宽限制
   - 或为测试环境单独配置

---

## 📚 相关资源

- **实现位置**: `test/conftest.py` - `make_request_with_retry()` 函数
- **依赖库**: Python `requests`, `time`
- **设计模式**: Retry Pattern with Exponential Backoff
- **参考文档**: [RFC 6585 - HTTP Status Code 429](https://tools.ietf.org/html/rfc6585)

---

## ✅ 检查清单

编写新的测试代码时，请确认：

- [ ] 所有 HTTP 请求都使用了 `make_request_with_retry()`
- [ ] 请求函数定义为无参数的 callable
- [ ] 断言包含有意义的错误消息
- [ ] 文件上传也正确使用了重试机制
- [ ] 没有直接调用 `requests.get/post/put/delete`
- [ ] Fixture 中获取资源的逻辑也使用了重试机制

---

## 🚨 违规后果

不遵循此规范可能导致：

1. **测试不稳定**：偶发性的429导致测试失败
2. **CI/CD流水线中断**：自动化测试随机失败
3. **调试困难**：难以复现间歇性故障
4. **团队协作问题**：其他人运行你的代码时遇到不同结果

---

**最后更新**: 2026-04-09  
**维护者**: 测试团队  
**版本**: v1.0
