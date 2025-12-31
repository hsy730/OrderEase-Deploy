# OrderEase API 测试说明

## 测试环境

- **Python 版本**: 3.12.7
- **测试目标**: OrderEase-Golang 代码库中的 API 接口
- **API 基础路径**: `http://localhost:8080/api`

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
├── conftest.py                    # pytest 配置文件，定义共享 fixtures
├── main.py                       # 测试主入口文件
├── test_auth.py                  # 认证相关接口测试
├── test_frontend.py              # 前端用户接口测试
├── test_admin_base.py           # 管理员基础接口测试
├── test_admin_shop.py           # 管理员店铺管理接口测试
├── test_admin_product.py        # 管理员商品管理接口测试
├── test_admin_user.py           # 管理员用户管理接口测试
├── test_admin_order.py          # 管理员订单管理接口测试
├── test_admin_tag.py            # 管理员标签管理接口测试
├── test_admin_data.py           # 管理员数据管理接口测试
├── test_shop_owner_base.py      # 商家基础接口测试
├── test_shop_owner_product.py   # 商家商品管理接口测试
├── test_shop_owner_order.py     # 商家订单管理接口测试
├── test_shop_owner_tag.py       # 商家标签管理接口测试
├── test_shop_owner_shop.py      # 商家店铺管理接口测试
├── test_shop_owner_user.py      # 商家用户管理接口测试
├── api_test.py                 # 原始测试文件（已弃用）
├── requirements.txt             # 依赖包列表
└── README.md                   # 本文档
```

## 测试模块说明

### 1. 认证模块 (test_auth.py)
测试认证相关接口，包括：
- 通用登录接口（管理员和商家）
- 令牌刷新接口
- 前端用户登录/注册
- 临时令牌登录

### 2. 前端模块 (test_frontend.py)
测试前端用户接口，包括：
- 产品相关接口
- 订单相关接口
- 标签相关接口
- 店铺相关接口
- 用户相关接口

### 3. 管理员模块

#### 3.1 管理员基础 (test_admin_base.py)
- 管理员登出
- 修改管理员密码

#### 3.2 店铺管理 (test_admin_shop.py)
- 创建/更新/删除店铺
- 获取店铺列表/详情
- 上传店铺图片
- 检查店铺名称
- 获取店铺临时令牌
- 更新订单状态流转

#### 3.3 商品管理 (test_admin_product.py)
- 创建/更新/删除商品
- 获取商品列表/详情
- 上传商品图片
- 切换商品状态
- 获取商品图片

#### 3.4 用户管理 (test_admin_user.py)
- 创建/更新/删除用户
- 获取用户列表/详情/简单列表

#### 3.5 订单管理 (test_admin_order.py)
- 创建/更新/删除订单
- 获取订单列表/详情
- 切换订单状态
- 获取订单状态流转
- 高级搜索订单

#### 3.6 标签管理 (test_admin_tag.py)
- 创建/更新/删除标签
- 获取标签列表/详情
- 批量打标签/解绑标签
- 获取标签关联商品
- 获取商品绑定/未绑定标签

#### 3.7 数据管理 (test_admin_data.py)
- 导出数据
- 导入数据

### 4. 商家模块

#### 4.1 商家基础 (test_shop_owner_base.py)
- 商家登出
- 修改商家密码

#### 4.2 商品管理 (test_shop_owner_product.py)
- 创建/更新/删除商品
- 获取商品列表/详情
- 上传商品图片
- 切换商品状态
- 获取商品图片

#### 4.3 订单管理 (test_shop_owner_order.py)
- 创建/更新/删除订单
- 获取订单列表/详情
- 切换订单状态
- 获取订单状态流转
- 获取未完成订单
- 高级搜索订单

#### 4.4 标签管理 (test_shop_owner_tag.py)
- 创建/更新/删除标签
- 获取标签列表/详情
- 批量打标签/解绑标签
- 获取标签关联商品
- 获取商品绑定/未绑定标签

#### 4.5 店铺管理 (test_shop_owner_shop.py)
- 获取店铺详情/图片
- 更新店铺信息
- 更新订单状态流转

#### 4.6 用户管理 (test_shop_owner_user.py)
- 创建/更新/删除用户
- 获取用户列表/详情/简单列表

## 运行测试

### 1. 使用主入口文件运行

```bash
# 运行所有测试
python main.py

# 运行认证模块测试
python main.py --module auth

# 运行前端模块测试
python main.py --module frontend

# 运行管理员模块测试
python main.py --module admin

# 运行商家模块测试
python main.py --module shop_owner

# 显示详细输出
python main.py --verbose

# 组合使用
python main.py --module auth --verbose
```

### 2. 使用 pytest 直接运行

```bash
# 运行所有测试
pytest -v

# 运行特定测试文件
pytest test_auth.py -v
pytest test_frontend.py -v

# 运行特定测试类
pytest test_auth.py::TestAuthAPI -v

# 运行单个测试函数
pytest test_auth.py::TestAuthAPI::test_universal_login_admin -v

# 运行多个测试文件
pytest test_auth.py test_frontend.py -v
```

### 3. 生成测试报告

```bash
# 安装 pytest-html
pip install pytest-html

# 生成 HTML 测试报告
pytest -v --html=report.html

# 生成 XML 报告（用于 CI/CD）
pytest -v --junitxml=report.xml
```

## 环境变量配置

创建 `.env` 文件，配置测试所需的环境变量：

```env
# API 基础 URL
API_BASE_URL=http://localhost:8080/api
```

## 测试注意事项

1. **确保服务已启动**: 在运行测试之前，请确保 OrderEase-Golang 服务已经正常启动。

2. **测试数据**: 测试脚本使用测试令牌（`test_token`），实际使用时需要替换为有效的认证令牌。

3. **测试数据**: 建议在测试前准备好必要的测试数据，如店铺、产品等。

4. **测试顺序**: 某些测试可能依赖于其他测试的结果，建议按顺序执行测试。

5. **清理数据**: 测试完成后，建议清理测试过程中创建的临时数据，以保持数据库的整洁。

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
schemathesis run --base-url http://localhost:8080/api docs/swagger.json
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
        python main.py
```

## 总结

本测试说明提供了使用 Python 3.12.7 测试 OrderEase-Golang API 接口的详细步骤和示例代码。测试文件已按业务模块拆分，结构清晰，便于维护和扩展。通过主入口文件 `main.py` 可以方便地运行不同模块的测试。

## 参考资料

- [Python requests 文档](https://requests.readthedocs.io/en/latest/)
- [pytest 文档](https://docs.pytest.org/en/latest/)
- [python-dotenv 文档](https://saurabh-kumar.com/python-dotenv/)
