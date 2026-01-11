# GitHub Actions 执行流程详解

## 目录

1. [工作流文件结构](#工作流文件结构)
2. [触发条件](#触发条件)
3. [执行流程](#执行流程)
4. [关键配置详解](#关键配置详解)
5. [数据传递机制](#数据传递机制)
6. [执行时序图](#执行时序图)

---

## 工作流文件结构

### 文件位置

```
OrderEase-Deploy/
└── .github/
    └── workflows/
        └── build-test-deploy.yml
```

### 基本结构

```yaml
name: OrderEase Build, Test and Deploy    # 工作流名称

on:                                        # 触发条件
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:                       # 手动触发

env:                                       # 全局环境变量
  DOCKER_IMAGE: docker.io/siyuanh640/orderease
  PYTHON_VERSION: "3.11"

jobs:                                      # 作业定义
  checkout-repos:                          # Job 1
    runs-on: ubuntu-latest
    steps: [...]
  build-image:                             # Job 2
    needs: checkout-repos                  # 依赖关系
    steps: [...]
  integration-test:                        # Job 3
    needs: build-image
    steps: [...]
  push-to-registry:                        # Job 4
    needs: [build-image, integration-test]
    steps: [...]
```

---

## 触发条件

### 1. Push 事件

```yaml
on:
  push:
    branches:
      - main
```

**触发时机**: 当代码推送到 `main` 分支时

**用途**: 正式部署到生产环境

---

### 2. Pull Request 事件

```yaml
on:
  pull_request:
    branches:
      - main
```

**触发时机**: 当创建或更新针对 `main` 分支的 PR 时

**用途**: CI 验证，测试通过后才能合并

**镜像标签策略**:
```yaml
if [ "${{ github.event_name }}" = "pull_request" ]; then
  TAG="${DOCKER_IMAGE}:pr-${{ github.event.pull_request.number }}"
  # 例如: docker.io/siyuanh640/orderease:pr-42
fi
```

---

### 3. 手动触发

```yaml
on:
  workflow_dispatch:
    inputs:
      skip_tests:
        description: "跳过测试（不推荐）"
        required: false
        type: boolean
        default: false
```

**触发方式**: 在 GitHub Actions 页面点击 "Run workflow"

**参数**: 可以选择是否跳过测试

---

## 执行流程

### Job 1: checkout-repos（检出代码）

**目的**: 准备所有仓库的代码用于构建

**执行步骤**:

```yaml
steps:
  # 1. 检出 OrderEase-Deploy（当前仓库）
  - uses: actions/checkout@v4
    with:
      path: OrderEase-Deploy

  # 2. 检出 OrderEase-FrontUI（外部仓库）
  - uses: actions/checkout@v4
    with:
      repository: hsy730/OrderEase-FrontUI
      ref: main
      path: OrderEase-FrontUI

  # 3. 检出 OrderEase-BackedUI（外部仓库）
  - uses: actions/checkout@v4
    with:
      repository: hsy730/OrderEase-BackedUI
      ref: master
      path: OrderEase-BackedUI

  # 4. 检出 OrderEase-Golang（外部仓库）
  - uses: actions/checkout@v4
    with:
      repository: hsy730/OrderEase-Golang
      ref: master
      path: OrderEase-Golang

  # 5. 准备构建上下文
  - run: |
      mkdir -p build-context
      cp -r OrderEase-FrontUI build-context/
      cp -r OrderEase-BackedUI build-context/
      cp -r OrderEase-Golang build-context/

  # 6. 上传构建上下文为 artifact
  - uses: actions/upload-artifact@v4
    with:
      name: build-context
      path: build-context/
      retention-days: 1  # 保留 1 天
```

**输出**: `build-context` artifact（包含所有源代码）

---

### Job 2: build-image（构建镜像）

**目的**: 构建多阶段 Docker 镜像

**依赖**: `needs: checkout-repos`

**执行步骤**:

```yaml
steps:
  # 1. 检出部署仓库（获取 Dockerfile）
  - uses: actions/checkout@v4
    with:
      path: OrderEase-Deploy

  # 2. 下载构建上下文
  - uses: actions/download-artifact@v4
    with:
      name: build-context
      path: .

  # 3. 设置 Docker Buildx
  - uses: docker/setup-buildx-action@v3

  # 4. 登录 Docker Hub
  - uses: docker/login-action@v3
    with:
      username: ${{ secrets.DOCKER_USERNAME }}
      password: ${{ secrets.DOCKER_PASSWORD }}

  # 5. 设置镜像标签
  - id: set-tag
    run: |
      if [ "${{ github.event_name }}" = "pull_request" ]; then
        TAG="${DOCKER_IMAGE}:pr-${{ github.event.pull_request.number }}"
      elif [ "${{ github.ref }}" = "refs/heads/main" ]; then
        TAG="${DOCKER_IMAGE}:latest"
      else
        BRANCH_NAME=$(echo "${{ github.ref_name }}" | sed 's/\//-/g')
        TAG="${DOCKER_IMAGE}:${BRANCH_NAME}"
      fi
      echo "tag=${TAG}" >> "${GITHUB_OUTPUT}"

  # 6. 构建 Docker 镜像
  - uses: docker/build-push-action@v5
    with:
      context: .                              # 构建上下文
      file: ./OrderEase-Deploy/build/Dockerfile
      push: false                             # 不推送，仅本地构建
      load: true                              # 加载到 Docker
      tags: ${{ steps.set-tag.outputs.tag }}
      cache-from: type=gha                    # 使用 GitHub 缓存
      cache-to: type=gha,mode=max
      build-args: |
        BUILD_DATE=${{ github.event.repository.updated_at }}
        VERSION=${{ github.sha }}

  # 7. 导出镜像为 TAR 文件
  - run: |
      TAG="${{ steps.set-tag.outputs.tag }}"
      docker image save "$TAG" -o orderease-image.tar

  # 8. 上传镜像 artifact
  - uses: actions/upload-artifact@v4
    with:
      name: orderease-docker-image
      path: orderease-image.tar
      retention-days: 1
```

**输出**:
- `image-tag` job output
- `image-digest` job output
- `orderease-docker-image` artifact

---

### Job 3: integration-test（集成测试）

**目的**: 运行 pytest 测试套件

**依赖**: `needs: build-image`

**条件**: `if: github.event.inputs.skip_tests != 'true'`

**服务容器配置**:

```yaml
services:
  mysql:
    image: mysql:8.0
    env:
      MYSQL_ROOT_PASSWORD: RootPassword123!
      MYSQL_DATABASE: mysql
      TZ: Asia/Shanghai
    ports:
      - 3306:3306  # 映射到主机
    options: >-
      --health-cmd="mysqladmin ping -h localhost -u root -pRootPassword123!"
      --health-interval=10s      # 健康检查间隔
      --health-timeout=5s        # 超时时间
      --health-retries=5         # 重试次数
      --health-start-period=30s  # 启动等待期
```

**执行步骤**:

```yaml
steps:
  # 1. 检出部署仓库（获取测试代码）
  - uses: actions/checkout@v4
    with:
      path: OrderEase-Deploy

  # 2. 下载镜像 artifact
  - uses: actions/download-artifact@v4
    with:
      name: orderease-docker-image
      path: .

  # 3. 加载 Docker 镜像
  - run: docker image load -i orderease-image.tar

  # 4. 启动应用容器（使用备用机制获取标签）
  - run: |
      IMAGE_TAG="${{ needs.build-image.outputs.image-tag }}"
      if [ -z "$IMAGE_TAG" ]; then
        IMAGE_TAG=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep "siyuanh640/orderease" | head -n1)
      fi
      docker run -d \
        --name orderease-app \
        --network ${{ job.container.network }} \
        -p 8080:8080 \
        -e DB_HOST=mysql \
        -e DB_PORT=3306 \
        -e DB_USERNAME=root \
        -e DB_PASSWORD=${{ env.MYSQL_ROOT_PASSWORD }} \
        -e DB_NAME=mysql \
        -e JWT_SECRET=${{ env.JWT_SECRET }} \
        -e TZ=Asia/Shanghai \
        -e GIN_MODE=release \
        "$IMAGE_TAG"

  # 5. 等待应用就绪
  - run: timeout 120 bash -c 'until curl -f http://localhost:8080/order-ease-iui/; do sleep 2; done'

  # 6. 设置 Python 环境
  - uses: actions/setup-python@v5
    with:
      python-version: ${{ env.PYTHON_VERSION }}
      cache: "pip"
      cache-dependency-path: OrderEase-Deploy/test/requirements.txt

  # 7. 安装测试依赖
  - run: pip install -r OrderEase-Deploy/test/requirements.txt

  # 8. 创建测试环境文件
  - working-directory: OrderEase-Deploy/test
    run: |
      cat > .env << EOF
      API_BASE_URL=http://localhost:8080/api/order-ease/v1
      DB_HOST=127.0.0.1
      DB_PORT=3306
      DB_USER=root
      DB_PASSWORD=${{ env.MYSQL_ROOT_PASSWORD }}
      DB_NAME=mysql
      EOF

  # 9. 运行 pytest 测试
  - working-directory: OrderEase-Deploy/test
    run: |
      pytest -v --html=report.html --self-contained-html \
        --junitxml=test-results.xml

  # 10. 上传测试报告
  - if: always()
    uses: actions/upload-artifact@v4
    with:
      name: test-report
      path: OrderEase-Deploy/test/report.html

  # 11. 清理容器
  - if: always()
    run: |
      docker stop orderease-app || true
      docker rm orderease-app || true
```

**输出**:
- `test-report` artifact（HTML 格式）
- `test-results` artifact（JUnit XML 格式）

---

### Job 4: push-to-registry（推送镜像）

**目的**: 将镜像推送到 Docker Hub

**依赖**: `needs: [build-image, integration-test]`

**条件**: `if: always() && needs.integration-test.result == 'success'`

**执行步骤**:

```yaml
steps:
  # 1. 下载镜像 artifact
  - uses: actions/download-artifact@v4
    with:
      name: orderease-docker-image
      path: .

  # 2. 加载 Docker 镜像
  - run: docker image load -i orderease-image.tar

  # 3. 登录 Docker Hub
  - uses: docker/login-action@v3
    with:
      username: ${{ secrets.DOCKER_USERNAME }}
      password: ${{ secrets.DOCKER_PASSWORD }}

  # 4. 推送镜像（使用备用机制获取标签）
  - run: |
      TAG="${{ needs.build-image.outputs.image-tag }}"
      if [ -z "$TAG" ]; then
        TAG=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep "siyuanh640/orderease" | head -n1)
      fi
      docker push "${TAG}"

  # 5. 输出镜像摘要
  - run: echo "Image pushed with digest: ${{ needs.build-image.outputs.image-digest }}"
```

---

## 关键配置详解

### 1. Job 依赖关系

```yaml
jobs:
  checkout-repos:
    runs-on: ubuntu-latest
    # 无依赖，首先执行

  build-image:
    needs: checkout-repos          # 等待 checkout-repos 完成
    runs-on: ubuntu-latest

  integration-test:
    needs: build-image             # 等待 build-image 完成
    runs-on: ubuntu-latest

  push-to-registry:
    needs: [build-image, integration-test]  # 等待两个 job 都完成
    runs-on: ubuntu-latest
```

**依赖图**:
```
checkout-repos
      ↓
  build-image
      ↓          ┌──────────────────┐
integration-test  │  push-to-registry │ ← 等待两者完成
      └──────────┴──────────────────┘
```

---

### 2. 条件执行

**跳过测试**:
```yaml
integration-test:
  if: github.event.inputs.skip_tests != 'true'
```

**仅测试成功后推送**:
```yaml
push-to-registry:
  if: |
    always() &&                           # 始终执行
    needs.integration-test.result == 'success'  # 但要求测试成功
```

**失败时执行**:
```yaml
- name: Print Logs on Failure
  if: failure()                          # 仅当前步骤失败时执行
  run: docker logs orderease-app

- name: Cleanup
  if: always()                           # 无论成功失败都执行
  run: docker stop orderease-app || true
```

---

### 3. 环境变量作用域

**全局环境变量**:
```yaml
env:
  DOCKER_IMAGE: docker.io/siyuanh640/orderease
  PYTHON_VERSION: "3.11"
```

**Job 级别环境变量**:
```yaml
integration-test:
  env:
    MYSQL_ROOT_PASSWORD: RootPassword123!
    JWT_SECRET: ${{ secrets.JWT_SECRET }}
```

**Step 级别环境变量**:
```yaml
- name: Run Pytest Tests
  env:
    API_BASE_URL: http://localhost:8080/api/order-ease/v1
  run: pytest -v
```

**引用方式**:
```yaml
${{ env.DOCKER_IMAGE }}        # 引用 env 定义的变量
${{ secrets.JWT_SECRET }}      # 引用 GitHub Secrets
${{ github.sha }}              # 引用 GitHub 上下文
```

---

### 4. Services 容器配置

```yaml
services:
  mysql:
    image: mysql:8.0
    env:
      MYSQL_ROOT_PASSWORD: RootPassword123!
      MYSQL_DATABASE: mysql
    ports:
      - 3306:3306               # 格式: "主机端口:容器端口"
    options: >-                 # 多行字符串
      --health-cmd="mysqladmin ping -h localhost -u root -pRootPassword123!"
      --health-interval=10s     # 健康检查间隔
      --health-timeout=5s       # 单次检查超时
      --health-retries=5        # 失败重试次数
      --health-start-period=30s # 容器启动后等待时间
```

**关键点**:
- Service containers 在独立的 Docker 网络中运行
- 可以通过服务名称（`mysql`）访问
- 健康检查确保服务就绪后再执行后续步骤

---

### 5. Artifacts 使用

**上传 Artifact**:
```yaml
- uses: actions/upload-artifact@v4
  with:
    name: build-context            # artifact 名称
    path: build-context/           # 要上传的路径
    retention-days: 1              # 保留天数（1-90 天）
```

**下载 Artifact**:
```yaml
- uses: actions/download-artifact@v4
  with:
    name: build-context            # 要下载的 artifact 名称
    path: .                        # 下载目标路径
```

**典型用途**:
- 在 jobs 之间传递数据
- 保存测试报告、日志文件
- 传递构建产物

---

### 6. 缓存配置

**Python pip 缓存**:
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: ${{ env.PYTHON_VERSION }}
    cache: "pip"                    # 启用 pip 缓存
    cache-dependency-path: OrderEase-Deploy/test/requirements.txt
```

**Docker Buildx 缓存**:
```yaml
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha            # 从 GitHub Actions 缓存读取
    cache-to: type=gha,mode=max     # 写入缓存（最大化缓存）
```

---

## 数据传递机制

### 1. Job Outputs

**定义输出**:
```yaml
build-image:
  outputs:
    image-tag: ${{ steps.set-tag.outputs.tag }}
    image-digest: ${{ steps.build.outputs.digest }}
  steps:
    - id: set-tag
      run: echo "tag=docker.io/...:latest" >> "${GITHUB_OUTPUT}"
    - id: build
      uses: docker/build-push-action@v5
```

**使用输出**:
```yaml
integration-test:
  needs: build-image
  steps:
    - run: |
        TAG="${{ needs.build-image.outputs.image-tag }}"
        echo "Using tag: $TAG"
```

**问题与备用方案**:
```yaml
# Job outputs 可能失败，添加备用机制
- run: |
    TAG="${{ needs.build-image.outputs.image-tag }}"
    if [ -z "$TAG" ]; then
      # 从 docker images 命令获取
      TAG=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep "orderease" | head -n1)
    fi
```

---

### 2. Step Outputs

**设置输出**:
```yaml
- id: set-tag
  run: |
    TAG="docker.io/siyuanh640/orderease:latest"
    echo "tag=${TAG}" >> "${GITHUB_OUTPUT}"  # 写入输出文件
```

**引用输出**:
```yaml
- uses: docker/build-push-action@v5
  with:
    tags: ${{ steps.set-tag.outputs.tag }}  # 引用 step 输出
```

---

### 3. Artifacts 传递

**Job A 上传**:
```yaml
- uses: actions/upload-artifact@v4
  with:
    name: docker-image
    path: image.tar
```

**Job B 下载**:
```yaml
- uses: actions/download-artifact@v4
  with:
    name: docker-image
    path: .
```

---

## 执行时序图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          GitHub Actions 执行时序                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  时间 →                                                                      │
│                                                                              │
│  checkout-repos Job:                                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │ Checkout Deploy  → Checkout FrontUI → Checkout BackedUI → Checkout    │   │
│  │                 → Checkout Golang   → Prepare Context → Upload        │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                      ↓                                        │
│  build-image Job:                                                            │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │ Checkout Deploy  → Download Context → Setup Buildx → Login DH → Set   │   │
│  │                 → Build Image → Export TAR → Upload Artifact           │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                      ↓                                        │
│                         ┌───────────────────────┐                           │
│                         │  并行执行（如果独立）    │                           │
│                         └───────────────────────┘                           │
│                      ↓                         ↓                            │
│  integration-test Job              push-to-registry Job                     │
│  ┌─────────────────────────────┐   ┌─────────────────────────────────────┐  │
│  │ Checkout → Download Image  │   │ (等待 integration-test 完成)          │  │
│  │ → Load → Start Containers  │   │                                     │  │
│  │ → Setup Python → Install   │   │                                     │  │
│  │ → Create .env → Run Pytest │   │                                     │  │
│  │ → Upload Reports           │   │                                     │  │
│  └─────────────────────────────┘   │                                     │  │
│            ↓ (测试成功)              │ Download → Load → Login DH         │  │
│                                     │ → Push Image → Output Digest      │  │
│                                     └─────────────────────────────────────┘  │
│                                                                              │
│  Service Containers (MySQL):                                                 │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │ Pull Image → Start Container → Health Check → Ready (端口 3306)       │   │
│  │                                                    ↑                  │   │
│  │                                        integration-test 开始前        │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## GitHub 上下文变量

### 常用上下文

| 上下文 | 变量 | 示例值 | 说明 |
|--------|------|--------|------|
| `github` | `github.event_name` | `push` / `pull_request` | 触发事件 |
| | `github.ref` | `refs/heads/main` | 完整引用 |
| | `github.ref_name` | `main` | 分支名 |
| | `github.sha` | `abc123...` | 提交 SHA |
| | `github.repository.updated_at` | `2026-01-11T...` | 仓库更新时间 |
| | `github.event.pull_request.number` | `42` | PR 编号 |
| `env` | `env.DOCKER_IMAGE` | `docker.io/...` | 自定义环境变量 |
| `secrets` | `secrets.DOCKER_USERNAME` | `***` | 加密的 Secrets |
| `needs` | `needs.build-image.outputs.image-tag` | `docker.io/...:latest` | 上游 job 输出 |
| `job` | `job.container.network` | `github_network_...` | 容器网络 ID |

---

## 关键 Actions 使用

### 1. Checkout Action

```yaml
- uses: actions/checkout@v4
  with:
    repository: hsy730/OrderEase-Golang  # 外部仓库（可选）
    ref: master                           # 分支/标签（可选）
    path: OrderEase-Golang                # 目标路径（可选）
    token: ${{ secrets.GITHUB_TOKEN }}     # 认证 token（可选）
```

---

### 2. Docker Buildx Action

```yaml
- uses: docker/build-push-action@v5
  with:
    context: .                           # 构建上下文路径
    file: ./Dockerfile                   # Dockerfile 路径
    push: true                           # 是否推送到 registry
    load: true                           # 是否加载到本地 Docker
    tags: user/app:latest,user/app:v1    # 镜像标签（逗号分隔）
    labels: maintainer=user              # 镜像标签
    cache-from: type=gha                 # 缓存来源
    cache-to: type=gha,mode=max          # 缓存目标
    build-args: |                        # 构建参数
      VERSION=1.0.0
      BUILD_DATE=2026-01-11
```

---

### 3. Setup Python Action

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'               # Python 版本
    cache: 'pip'                         # 缓存类型（pip/pipenv/poetry）
    cache-dependency-path: requirements.txt  # 依赖文件路径
```

---

### 4. Artifact Actions

**上传**:
```yaml
- uses: actions/upload-artifact@v4
  with:
    name: my-artifact                    # artifact 名称
    path: path/to/file                   # 文件/目录路径
    retention-days: 7                    # 保留天数
    if-no-files-found: warn              # 无文件时的行为
```

**下载**:
```yaml
- uses: actions/download-artifact@v4
  with:
    name: my-artifact                    # artifact 名称
    path: path/to/destination            # 目标路径
```

---

## 最佳实践

### 1. 使用 `if: always()` 确保清理

```yaml
- name: Cleanup
  if: always()                           # 无论前置步骤成功失败都执行
  run: docker stop orderease-app || true
```

### 2. 添加失败时的日志输出

```yaml
- name: Print Logs on Failure
  if: failure()
  run: docker logs orderease-app || true
```

### 3. 使用 `|| true` 防止错误中断

```yaml
- run: docker stop orderease-app || true  # 容器可能已停止
```

### 4. 合理设置 artifact 保留时间

```yaml
retention-days: 1  # 仅保留 1 天，节省存储空间
```

### 5. 使用缓存加速构建

```yaml
cache-from: type=gha                    # 读取缓存
cache-to: type=gha,mode=max             # 写入缓存
```

---

## 相关文档

- [GitHub Actions 官方文档](https://docs.github.com/en/actions)
- [工作流语法](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Docker Buildx Action](https://github.com/docker/build-push-action)
- [Python Setup Action](https://github.com/actions/setup-python)

---

**文档版本**: 1.0
**最后更新**: 2026-01-11
