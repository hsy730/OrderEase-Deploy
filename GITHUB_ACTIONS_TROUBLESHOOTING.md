# GitHub Actions CI/CD 故障排查总结

## 概述

本文档记录了 OrderEase-Deploy 项目在配置 GitHub Actions CI/CD 流水线时遇到的关键问题及其解决方案。

## 整体架构

### 工作流结构

OrderEase-Deploy 使用 GitHub Actions 实现完整的 CI/CD 流程：

```
┌─────────────────────────────────────────────────────────────────┐
│                     GitHub Actions 工作流                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Job 1: checkout-repos                                           │
│  ─────────────────────                                           │
│  • 检出 OrderEase-Deploy 仓库                                     │
│  • 检出 OrderEase-FrontUI 仓库                                    │
│  • 检出 OrderEase-BackedUI 仓库                                   │
│  • 检出 OrderEase-Golang 仓库                                     │
│  • 构建上下文并上传为 artifact                                    │
│                                                                  │
│  Job 2: build-image                                              │
│  ────────────────                                                │
│  • 下载构建上下文                                                 │
│  • 登录 Docker Hub                                               │
│  • 设置镜像标签                                                   │
│  • 多阶段构建 Docker 镜像                                         │
│  • 导出镜像为 TAR 文件                                            │
│  • 上传镜像为 artifact                                           │
│                                                                  │
│  Job 3: integration-test                                         │
│  ─────────────────────                                           │
│  • 启动 MySQL 服务容器                                           │
│  • 下载并加载 Docker 镜像                                         │
│  • 启动 OrderEase 应用容器                                       │
│  • 运行 pytest 测试套件                                          │
│  • 生成测试报告                                                  │
│                                                                  │
│  Job 4: push-to-registry                                         │
│  ────────────────────                                            │
│  • 加载 Docker 镜像                                              │
│  • 登录 Docker Hub                                               │
│  • 推送镜像到 Docker Hub                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Docker 镜像构建

采用多阶段构建策略，将所有组件打包为单一镜像：

```
Stage 1: Node 16 Alpine    → 构建 Backend UI
Stage 2: Node 18 Alpine    → 构建 Frontend UI
Stage 3: Go 1.22 Alpine    → 构建 Go 后端
Stage 4: Alpine Runtime    → 最终运行时镜像
                            • Go 二进制文件
                            • UI 静态文件
                            • 健康检查
```

---

## 关键问题与解决方案

### 问题 1: IMAGE_TAG 跨 Job 传递失败

#### 问题描述

在 `build-image` job 中设置的输出 `image-tag` 无法传递到 `integration-test` 和 `push-to-registry` job。

**错误日志：**
```bash
IMAGE_TAG=""
# invalid reference format
```

#### 根本原因

GitHub Actions 的 job outputs 机制在特定情况下可能失效：
1. 虽然 `steps.set-tag.outputs.tag` 在同一 job 内可以正确读取
2. 但通过 `needs.build-image.outputs.image-tag` 跨 job 传递时值为空

#### 解决方案

**使用备用机制：从 docker images 命令获取标签**

```yaml
- name: Start OrderEase Application Container
  run: |
    IMAGE_TAG="${{ needs.build-image.outputs.image-tag }}"

    # Fallback: if IMAGE_TAG is empty, get it from docker images
    if [ -z "$IMAGE_TAG" ]; then
      echo "Warning: IMAGE_TAG from job output is empty, getting tag from docker images..."
      IMAGE_TAG=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep "siyuanh640/orderease" | head -n1)
      echo "Using tag: $IMAGE_TAG"
    fi

    if [ -z "$IMAGE_TAG" ]; then
      echo "Error: IMAGE_TAG is still empty after fallback!"
      docker images
      exit 1
    fi

    docker run -d --name orderease-app ...
```

**应用位置：**
- `integration-test` job 的 `Start OrderEase Application Container` 步骤
- `push-to-registry` job 的 `Push Image to Docker Hub` 步骤

---

### 问题 2: 数据库连接失败

#### 问题描述

应用容器启动时无法连接到数据库：

**错误日志：**
```
panic: failed to connect database: 连接数据库失败: dial tcp 127.0.0.1:3306: connect: connection refused
```

#### 根本原因

GitHub Actions 的 `services` 容器运行在独立的 Docker 网络中：
- 应用容器通过 `127.0.0.1` 无法访问服务容器
- 应该使用服务名称作为主机名

#### 解决方案

**修改数据库主机地址和网络配置：**

```yaml
# 修改前
docker run -d \
  --name orderease-app \
  -p 8080:8080 \
  -e DB_HOST=127.0.0.1 \
  ...

# 修改后
docker run -d \
  --name orderease-app \
  --network ${{ job.container.network }} \
  -p 8080:8080 \
  -e DB_HOST=mysql \
  ...
```

**关键变更：**
1. `DB_HOST=127.0.0.1` → `DB_HOST=mysql`
2. 添加 `--network ${{ job.container.network }}` 确保容器在同一网络

---

### 问题 3: 测试执行顺序不一致

#### 问题描述

本地测试顺序为 `frontend → admin → shopOwner → auth`，但 GitHub Actions 中顺序变为 `frontend → shopOwner → admin → auth`。

#### 根本原因

`conftest.py` 中的文件优先级映射配置错误：
- `shop_owner/test_business_flow.py`: 10 (优先级高于 admin)
- `admin/test_business_flow.py`: 20 (优先级低于 shop_owner)

#### 解决方案

**调整优先级数值：**

```python
file_priority_map = {
    "test_frontend_flow.py": 0,           # 前端业务流程
    "admin/test_business_flow.py": 10,    # 管理员业务流程 (从 20 改为 10)
    "shop_owner/test_business_flow.py": 20, # 商家业务流程 (从 10 改为 20)
    "test_auth_flow.py": 100,             # 认证测试
    ...
}
```

---

### 问题 4: GITHUB_OUTPUT 写入失败

#### 问题描述

尝试设置 job output 时，脚本在写入 `$GITHUB_OUTPUT` 后停止执行。

**错误日志：**
```
Final tag: docker.io/***/orderease:latest
GITHUB
# 脚本在此停止
```

#### 根本原因

在 bash 中直接 echo `$GITHUB_OUTPUT` 环境变量时，由于变量包含特殊字符或路径，导致命令失败。由于使用了 `set -e` 选项，脚本立即退出。

#### 解决方案

**使用安全的写入方式：**

```bash
# 不安全的写法
echo "GITHUB_OUTPUT=$GITHUB_OUTPUT"  # 可能导致脚本失败
echo "tag=${TAG}" >> "$GITHUB_OUTPUT"

# 安全的写法
echo "tag=${TAG}" >> "${GITHUB_OUTPUT}" 2>/dev/null || echo "Failed to write"
```

**关键改进：**
1. 移除打印 `$GITHUB_OUTPUT` 变量的调试代码
2. 使用双引号包裹变量路径
3. 添加错误抑制 `2>/dev/null`

---

## 技术要点总结

### 1. Job Outputs 的局限性

GitHub Actions 的 job outputs 机制在某些情况下不可靠。当遇到 outputs 传递失败时：
- 添加日志确认值是否设置
- 使用 artifacts 或文件传递作为备用方案
- 考虑使用环境变量或直接查询（如 docker images）

### 2. Docker 网络配置

在 CI/CD 环境中，容器间通信需要注意：
- Service containers 使用服务名称作为主机名
- 显式指定网络确保容器可以相互通信
- 不要假设 localhost/127.0.0.1 可以访问其他容器

### 3. 多阶段构建优化

```
优势：
• 每个阶段可以使用不同的基础镜像
• 最终镜像只包含运行时所需文件
• 可以利用 Docker 缓存加速构建

注意事项：
• 确保阶段之间文件路径正确
• 注意基础镜像的兼容性
```

### 4. 测试顺序管理

使用 `pytest_collection_modifyitems` 钩子控制测试执行顺序：
- 数值越小优先级越高
- 注意文件路径匹配的正确性
- 为子测试（如认证测试内的方法）设置细粒度优先级

---

## 配置文件关键片段

### 镜像标签设置

```yaml
- name: Set Image Tag
  id: set-tag
  run: |
    DOCKER_IMAGE="${{ env.DOCKER_IMAGE }}"
    if [ "${{ github.event_name }}" = "pull_request" ]; then
      TAG="${DOCKER_IMAGE}:pr-${{ github.event.pull_request.number }}"
    elif [ "${{ github.ref }}" = "refs/heads/main" ]; then
      TAG="${DOCKER_IMAGE}:latest"
    else
      BRANCH_NAME=$(echo "${{ github.ref_name }}" | sed 's/\//-/g')
      TAG="${DOCKER_IMAGE}:${BRANCH_NAME}"
    fi
    echo "tag=${TAG}" >> "${GITHUB_OUTPUT}"
```

### 服务容器配置

```yaml
services:
  mysql:
    image: mysql:8.0
    env:
      MYSQL_ROOT_PASSWORD: RootPassword123!
      MYSQL_DATABASE: mysql
    ports:
      - 3306:3306
    options: >-
      --health-cmd="mysqladmin ping -h localhost -u root -pRootPassword123!"
      --health-interval=10s
      --health-timeout=5s
      --health-retries=5
      --health-start-period=30s
```

### 测试执行命令

```yaml
- name: Run Pytest Tests
  working-directory: OrderEase-Deploy/test
  env:
    API_BASE_URL: http://localhost:8080/api/order-ease/v1
  run: |
    pytest -v --html=report.html --self-contained-html \
      --junitxml=test-results.xml
```

---

## 最佳实践建议

### 1. 容错设计

- 始终为关键数据（如 IMAGE_TAG）提供备用获取方式
- 添加详细的调试日志输出
- 使用 `if: always()` 确保清理步骤执行

### 2. 安全配置

```yaml
# 不要在日志中暴露敏感信息
echo "Password is: ${PASSWORD:0:3}***"

# 使用 GitHub Secrets 存储敏感信息
username: ${{ secrets.DOCKER_USERNAME }}
```

### 3. 性能优化

- 使用 Docker Buildx 缓存加速构建
- 并行执行独立的 jobs
- 合理设置 artifact 保留天数

### 4. 监控与报告

```yaml
# 始终上传测试报告
- name: Upload Test Report
  if: always()
  uses: actions/upload-artifact@v4

# 失败时输出应用日志
- name: Print Application Logs on Failure
  if: failure()
  run: docker logs orderease-app || true
```

---

## 相关文档

- [GitHub Actions 工作流语法](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Docker 多阶段构建](https://docs.docker.com/build/building/multi-stage/)
- [Pytest 文档](https://docs.pytest.org/)
- [项目 CLAUDE.md](./CLAUDE.md)

---

## 变更历史

| 日期 | 提交 | 描述 |
|------|------|------|
| 2026-01-11 | `e4a7afc` | 安全写入 GITHUB_OUTPUT |
| 2026-01-11 | `7bbd27e` | 修正测试执行顺序 |
| 2026-01-11 | `d242e6f` | 修复数据库连接配置 |
| 2026-01-11 | `aba9c14` | 添加 push-to-registry 备用机制 |
| 2026-01-11 | `58577f4` | 添加 integration-test 备用机制 |

---

**文档版本**: 1.0
**最后更新**: 2026-01-11
