# OrderEase API 测试说明

## 测试环境

- **Python 版本**: 3.12.7
- **测试目标**: OrderEase-Golang 代码库中的 API 接口
- **API 基础路径**: `http://localhost:8080/api/order-ease/v1`

## 测试工具

- **requests**: HTTP 请求库
- **pytest**: 测试框架
- **python-dotenv**: 环境变量管理

## 准备工作

### 1. 安装 Python 3.12.7

请从 [Python 官方网站](https://www.python.org/downloads/release/python-3127/) 下载并安装 Python 3.12.7。

### 2. 创建虚拟环境

```bash
# 在 test 目录下创建虚拟环境
cd d:\local_code_repo\OrderEase-Deploy\test
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 启动 OrderEase-Golang 服务

请确保 OrderEase-Golang 服务已经启动，默认监听端口为 8080。

```bash
# 进入 OrderEase-Golang 目录
cd d:\local_code_repo\OrderEase-Golang\src

# 启动服务
./orderease.exe
# 或使用 go run 命令启动
go run main.go
```

## 测试文件结构

```
test/
├── conftest.py                           # pytest 配置文件，定义共享 fixtures
├── pytest.ini                            # pytest 配置文件
├── requirements.txt                        # 依赖包列表
├── .env                                  # 环境变量配置
├── README.md                              # 本文档
├── admin/                                # 管理员接口测试
│   ├── test_base.py                     # 管理员基础功能测试
│   ├── test_order.py                    # 管理员订单管理接口测试
│   ├── test_product.py                 # 管理员商品管理接口测试
│   ├── test_shop.py                    # 管理员店铺管理接口测试
│   ├── test_tag.py                     # 管理员标签管理接口测试
│   └── test_user.py                    # 管理员用户管理接口测试
├── shop_owner/                           # 商家接口测试
│   ├── test_base.py                     # 商家基础功能测试
│   ├── test_order.py                    # 商家订单管理接口测试
│   ├── test_product.py                 # 商家商品管理接口测试
│   ├── test_shop.py                    # 商家店铺管理接口测试
│   ├── test_tag.py                     # 商家标签管理接口测试
│   └── test_user.py                    # 商家用户管理接口测试
├── frontend/                             # 前端用户接口测试
│   ├── test_auth.py                    # 前端用户认证测试
│   ├── test_order.py                   # 前端用户订单测试
│   ├── test_product.py                # 前端用户商品测试
│   └── test_shop.py                    # 前端用户店铺测试
└── auth/                                # 认证相关测试
    ├── test_login.py                    # 登录接口测试
    ├── test_logout.py                  # 登出接口测试
    ├── test_refresh_token.py            # 刷新令牌测试
    ├── test_temp_login.py               # 临时令牌登录测试
    ├── test_unauthorized.py            # 未授权访问测试
    ├── test_privilege_escalation.py     # 越权测试
    ├── test_parameter_validation.py     # 参数校验测试
    └── test_boundary_conditions.py    # 边界条件测试
```

## 测试模块说明

### 1. 认证模块 (auth/)

#### 1.1 基础认证 (auth/test_login.py, auth/test_logout.py)
测试基础认证接口，包括：
- 通用登录接口（管理员和商家）
- 登出接口
- 令牌刷新接口
- 临时令牌登录

#### 1.2 安全测试 (auth/test_unauthorized.py, auth/test_privilege_escalation.py)
测试安全性相关场景：
- 未授权访问测试（无token、无效token、过期token等）
- 越权测试（不同角色访问其他角色接口）

#### 1.3 参数校验 (auth/test_parameter_validation.py)
测试各种无效参数场景：
- 缺少必填字段
- 无效数据格式
- 无效数据类型
- 无效数据范围

#### 1.4 边界条件 (auth/test_boundary_conditions.py)
测试各种边界值场景：
- 最小值
- 最大值
- 零值
- 负值
- 超长值

### 2. 前端模块 (frontend/)

测试前端用户接口，包括：
- 用户认证（登录、注册、检查用户名）
- 产品相关接口（列表、详情、图片）
- 订单相关接口（创建、列表、详情、删除）
- 店铺相关接口（详情、图片、标签）

### 3. 管理员模块 (admin/)

#### 3.1 管理员基础 (admin/test_base.py)
- 修改管理员密码

#### 3.2 店铺管理 (admin/test_shop.py)
- 创建/更新/删除店铺
- 获取店铺列表/详情
- 上传店铺图片
- 检查店铺名称
- 获取店铺临时令牌
- 更新订单状态流转

#### 3.3 商品管理 (admin/test_product.py)
- 创建/更新/删除商品
- 获取商品列表/详情
- 上传商品图片
- 切换商品状态
- 获取商品图片

#### 3.4 用户管理 (admin/test_user.py)
- 创建/更新/删除用户
- 获取用户列表/详情/简单列表

#### 3.5 订单管理 (admin/test_order.py)
- 创建/更新/删除订单
- 获取订单列表/详情
- 切换订单状态

#### 3.6 标签管理 (admin/test_tag.py)
- 创建/更新/删除标签
- 获取标签列表/详情
- 批量打标签/解绑标签
- 获取标签关联商品
- 获取商品绑定/未绑定标签

### 4. 商家模块 (shop_owner/)

#### 4.1 商家基础 (shop_owner/test_base.py)
- 修改商家密码

#### 4.2 商品管理 (shop_owner/test_product.py)
- 创建/更新/删除商品
- 获取商品列表/详情
- 上传商品图片
- 切换商品状态
- 获取商品图片

#### 4.3 订单管理 (shop_owner/test_order.py)
- 创建/更新/删除订单
- 获取订单列表/详情
- 切换订单状态

#### 4.4 标签管理 (shop_owner/test_tag.py)
- 创建/更新/删除标签
- 获取标签列表/详情
- 批量打标签/解绑标签
- 获取标签关联商品
- 获取商品绑定/未绑定标签

#### 4.5 店铺管理 (shop_owner/test_shop.py)
- 获取店铺详情/图片
- 更新店铺信息
- 更新订单状态流转

#### 4.6 用户管理 (shop_owner/test_user.py)
- 创建/更新/删除用户
- 获取用户列表/详情/简单列表

## 运行测试

### 1. 运行所有测试

```bash
# 运行所有测试
pytest -v

# 生成 HTML 测试报告
pytest -v --html=report.html

# 生成 XML 报告（用于 CI/CD）
pytest -v --junitxml=report.xml
```

### 2. 运行特定模块的测试

```bash
# 运行认证模块测试
pytest auth/ -v

# 运行管理员模块测试
pytest admin/ -v

# 运行商家模块测试
pytest shop_owner/ -v

# 运行前端模块测试
pytest frontend/ -v
```

### 3. 运行特定类型的测试

```bash
# 运行未授权访问测试
pytest auth/test_unauthorized.py -v

# 运行越权测试
pytest auth/test_privilege_escalation.py -v

# 运行参数校验测试
pytest auth/test_parameter_validation.py -v

# 运行边界条件测试
pytest auth/test_boundary_conditions.py -v
```

### 4. 运行特定测试文件

```bash
# 运行特定测试文件
pytest admin/test_user.py -v

# 运行特定测试类
pytest admin/test_user.py::TestAdminUserAPI -v

# 运行单个测试函数
pytest admin/test_user.py::TestAdminUserAPI::test_create_user -v
```

### 5. 组合使用多个测试文件

```bash
# 运行多个测试文件
pytest admin/test_user.py admin/test_shop.py -v
```

## 环境变量配置

创建 `.env` 文件，配置测试所需的环境变量：

```env
# API 基础 URL
API_BASE_URL=http://localhost:8080/api/order-ease/v1
```

## 测试注意事项

1. **确保服务已启动**: 在运行测试之前，请确保 OrderEase-Golang 服务已经正常启动。
2. **测试令牌**: 测试脚本使用测试令牌（`test_token`），实际使用时需要替换为有效的认证令牌。
3. **测试数据**: 建议在测试前准备好必要的测试数据，如店铺、产品等。
4. **测试顺序**: 某些测试可能依赖于其他测试的结果，建议按顺序执行测试。
5. **清理数据**: 测试完成后，建议清理测试过程中创建的临时数据，以保持数据库的整洁。
6. **速率限制**: API 可能有速率限制，测试中已添加 429 状态码处理。

## 测试统计

当前测试套件包含：
- **功能测试**: 84 个测试用例
- **未授权访问测试**: 10 个测试用例
- **越权测试**: 15 个测试用例
- **参数校验测试**: 39 个测试用例
- **边界条件测试**: 57 个测试用例
- **总计**: 206 个测试用例

## 扩展测试

### 1. 添加性能测试

使用 `locust` 进行性能测试：

```bash
# 安装 locust
pip install locust

# 创建性能测试脚本 locustfile.py
# 运行性能测试
locust -f locustfile.py --host=http://localhost:8080
```

### 2. 添加 API 文档测试

使用 `schemathesis` 进行 API 文档测试：

```bash
# 安装 schemathesis
pip install schemathesis

# 运行 API 文档测试
schemathesis run --base-url http://localhost:8080/api/order-ease/v1 docs/swagger.json
```

## 故障排查

### 1. 服务未启动

如果测试失败并提示 "Connection refused"，请检查 OrderEase-Golang 服务是否已经启动。

### 2. 认证失败

如果测试失败并提示 "Unauthorized"，请检查认证令牌是否正确。

### 3. 数据问题

如果测试失败并提示 "Not Found" 或其他数据相关错误，请检查测试数据是否存在。

### 4. Python 版本问题

如果遇到 Python 版本相关的错误，请确保使用的是 Python 3.12.7。

### 5. 测试速率限制

如果测试失败并提示 "Too Many Requests"，这是 API 的速率限制，可以稍后重试或调整测试间隔。

## 持续集成

可以将 API 测试集成到 CI/CD 流程中，例如使用 GitHub Actions 或 GitLab CI。

### GitHub Actions 示例

```yaml
# .github/workflows/api-test.yml
name: API Test

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python 3.12.7
      uses: actions/setup-python@v5
      with:
        python-version: 3.12.7
    
    - name: Install dependencies
      run: |
        cd d:\local_code_repo\OrderEase-Deploy\test
        pip install -r requirements.txt
    
    - name: Start OrderEase-Golang service
      run: |
        cd d:\local_code_repo\OrderEase-Golang\src
        ./orderease.exe &
        sleep 5
    
    - name: Run API tests
      run: |
        cd d:\local_code_repo\OrderEase-Deploy\test
        pytest -v --junitxml=report.xml
    
    - name: Upload test results
      uses: actions/upload-artifact@v4
      with:
        name: test-results
        path: report.xml
```

## 总结

本测试说明提供了使用 Python 3.12.7 测试 OrderEase-Golang API 接口的详细步骤和示例代码。测试文件已按业务模块和测试类型拆分，结构清晰，便于维护和扩展。通过 pytest 可以方便地运行不同模块和类型的测试。

## 参考资料

- [Python requests 文档](https://requests.readthedocs.io/en/latest/)
- [pytest 文档](https://docs.pytest.org/en/latest/)
- [python-dotenv 文档](https://saurabh-kumar.com/python-dotenv/)
- [pytest-html 文档](https://pytest-html.readthedocs.io/en/latest/)
- [locust 文档](https://docs.locust.io/en/stable/)
- [schemathesis 文档](https://schemathesis.readthedocs.io/en/stable/)