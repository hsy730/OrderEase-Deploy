# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OrderEase-Deploy is a unified deployment and comprehensive testing repository for the OrderEase e-commerce management system. It combines multiple components into a single Docker-based deployment:
- **Backend API**: Go-based REST API with DDD architecture (from OrderEase-Golang repository)
- **Admin UI**: Vue 3 admin dashboard for shop owners and administrators (from OrderEase-BackedUI repository)
- **Frontend UI**: Vue 3 mobile-first customer interface (from OrderEase-FrontUI repository)
- **Database**: MySQL 8.0 for data persistence

**Repository Relationships**:
- This repository depends on three separate source repositories checked out during CI/CD:
  - `hsy730/OrderEase-Golang` - Go backend
  - `hsy730/OrderEase-BackedUI` - Admin UI
  - `hsy730/OrderEase-FrontUI` - Customer UI
- The multi-stage Docker build copies source code from sibling directories (or artifact from CI/CD)

## Build and Deploy Commands

### Building the Docker Image

**Using docker-compose**:
```bash
cd build
docker-compose build
```

**Using PowerShell deploy script** (Windows):
```powershell
cd scripts
# First, allow script execution:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# Then deploy:
.\deploy.ps1
```

**Using Bash deploy script** (Linux/Mac):
```bash
cd scripts
chmod +x deploy.sh
./deploy.sh
```

**Direct Docker build** (for manual builds with sibling source repos):
```bash
docker build -t orderease:latest -f build/Dockerfile ../..
```

**Deploy script options** (Windows PowerShell):
- `.\deploy.ps1` - Full deployment with image pull
- `.\deploy.ps1 -SkipPull` - Skip image pull if already available
- `.\deploy.ps1 -OverrideConfig` - Override existing configuration

**Deploy script options** (Linux/Mac Bash):
- `./deploy.sh` - Interactive deployment with image source selection
- `./deploy.sh --skip-pull` - Skip image pull

### Running the Application

```bash
cd deploy
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Clean restart (removes volumes)
docker-compose down -v
```

### Access Points

After deployment:
- **Frontend UI**: `http://localhost:8080/order-ease-iui/`
- **Admin UI**: `http://localhost:8080/order-ease-adminiui/`
- **API Base**: `http://localhost:8080/api/order-ease/v1/`

**Default credentials**: `admin` / `Admin@123456`

## Testing

### Running Tests

```bash
cd test

# Run all tests
pytest -v

# Run with HTML report
pytest -v --html=report.html --self-contained-html

# Run specific test module
pytest admin/test_business_flow.py -v

# Run specific test case
pytest admin/test_business_flow.py::TestBusinessFlow::test_complete_business_flow -v

# Run with detailed output
pytest -v -s
```

### Test Structure

The test suite follows a layered architecture:

1. **conftest.py** - Central fixture management
   - Session-scoped fixtures for authentication tokens (`admin_token`, `shop_owner_token`, `user_token`)
   - Resource ID fixtures (`test_shop_id`, `test_product_id`, etc.)
   - `make_request_with_retry()` - Handles 429 rate limiting with exponential backoff
   - Test execution ordering via `pytest_collection_modifyitems()`

2. **Action Modules** (`*_actions.py`) - Reusable business operations
   - Pure functions that perform API calls
   - Return structured data for use in tests
   - Located in `admin/`, `shop_owner/`, and `frontend/` directories

3. **Test Flow Files** (`test_*_flow.py`) - Business orchestration
   - Test classes with setup/teardown
   - Automatic resource cleanup using cleanup lists
   - Business dependency ordering

### Test Execution Order

Tests execute in priority order (defined in `conftest.py::pytest_collection_modifyitems`):
1. Frontend tests (`test_frontend_flow.py`) - Priority 0
2. Shop owner business flow (`shop_owner/test_business_flow.py`) - Priority 10
3. Admin business flow (`admin/test_business_flow.py`) - Priority 20
4. Auth tests (`test_auth_flow.py`) - Priority 100 (logs out tokens)
5. Unauthorized tests (`test_unauthorized.py`) - Priority 110

## Architecture Patterns

### Multi-Stage Docker Build

The `build/Dockerfile` uses a 4-stage build with extreme optimization:
1. **Stage 1**: Build Backend UI (Node 20 Alpine) - creates admin dashboard at `dist/`
2. **Stage 2**: Build Frontend UI (Node 20 Alpine) - creates customer interface at `dist/build/h5/`
3. **Stage 3**: Build Go backend (Go 1.24 Alpine) - compiles with UPX compression
4. **Stage 4**: Final runtime (Alpine 3.19) - minimal ~36MB image

**Build Optimizations**:
- UPX binary compression (`upx --best --lzma`) reduces Go binary size significantly
- Go build flags: `-ldflags="-s -w -buildid="` removes symbols and debug info
- `--trimpath` removes file path information
- Non-root user execution (uid 1000, group orderease)
- Health checks using wget for container monitoring

**Static File Paths** (in final image):
- `/app/static/order-ease-adminiui/` - Admin UI
- `/app/static/order-ease-iui/` - Customer UI
- `/app/uploads/` - User uploads
- `/app/logs/` - Application logs

### Unified Deployment

Single Docker image serves all components:
- Go backend serves both API and static UI files
- Static files served from `/app/static/`:
  - `/order-ease-adminiui/` - Admin dashboard
  - `/order-ease-iui/` - Customer interface
  - API at `/api/order-ease/v1/`

### Configuration

> **📖 环境变量配置指南**: 详见 [docs/guides/ENV_CONFIGURATION_GUIDE.md](docs/guides/ENV_CONFIGURATION_GUIDE.md)
>
> 该指南包含：
> - 完整的环境变量列表和说明
> - 本地部署环境变量配置步骤
> - CI/CD (GitHub Actions) 环境变量配置
> - 安全密钥生成方法
> - 常见问题排查

**Environment Variables** (`deploy/.env`):
- `DB_HOST`, `DB_PORT`, `DB_USERNAME`, `DB_PASSWORD`, `DB_NAME` - Database connection
- `JWT_SECRET`, `JWT_EXPIRATION` - Authentication
- `SERVER_PORT`, `APP_PORT`, `MYSQL_PORT` - Port mappings
- `TZ` - Timezone (default: Asia/Shanghai)

**Application Config** (`deploy/config/config.yaml`):
- `server.*`: Base path, host, domain, CORS origins
- `database.*`: MySQL connection settings
- `jwt.*`: JWT authentication settings

### Environment Variable Setup

**Quick Setup for Local Deployment**:
```bash
# 1. Copy the template
cd deploy
cp .env.template .env

# 2. Edit with your values
# Required minimum:
#   DB_PASSWORD=YourStrongPassword123!
#   JWT_SECRET=your_jwt_secret_minimum_32_bytes_long
```

**CI/CD Required Secrets** (GitHub Repository Settings):
- `JWT_SECRET` - JWT signing key (≥32 bytes)
- `DOCKER_USERNAME` - Docker Hub username
- `DOCKER_PASSWORD` - Docker Hub password/token

See [ENV_CONFIGURATION_GUIDE.md](docs/guides/ENV_CONFIGURATION_GUIDE.md) for detailed setup instructions.

### CI/CD Pipeline

Located in `.github/workflows/build-test-deploy.yml`:

**Job 1: Checkout Repositories**
- Checks out all 4 repositories from `hsy730/` org:
  - OrderEase-Deploy
  - OrderEase-FrontUI
  - OrderEase-BackedUI
  - OrderEase-Golang
- Creates build context artifact for downstream jobs

**Job 2: Go Unit Tests**
- Uses Go 1.22 with GOMODCACHE
- Runs Go tests with race detection (`-race`) and coverage reporting
- Uploads coverage report (`coverage.html`) as artifact (7-day retention)

**Job 3: Build Docker Image**
- Multi-stage Docker build with GitHub Actions caching (type=gha)
- Runs Trivy vulnerability scanner (CRITICAL, HIGH severity)
- Uploads SARIF results to GitHub Security tab
- Exports image as TAR artifact for downstream jobs

**Job 4: Integration Tests**
- Requires `build-image` job to succeed
- Uses GitHub Actions MySQL 8.0 service with health checks
- Loads Docker image from artifact and starts container
- Waits up to 120 seconds for application to be ready
- Executes pytest suite with HTML and JUnit XML reports

**Job 5: Push to Registry**
- Only runs if all tests pass (`needs.integration-test.result == 'success'`)
- Loads image from artifact
- Pushes to `docker.io/siyuanh640/orderease:latest` (or PR-specific tag)

**Manual Trigger Options**:
- `skip_tests` input - Skip integration tests (not recommended)
- `workflow_dispatch` - Manual trigger from GitHub Actions UI

## Testing Conventions

### Assertion Strictness (CRITICAL)

**测试断言必须严格明确，禁止模糊处理！**

#### ✅ 正确做法：单一期望

```python
# 期望成功：严格断言必须成功
def test_delete_product():
    result = product_actions.delete_product(admin_token, product_id, shop_id)
    assert result, f"删除商品失败，product_id: {product_id}"  # 必须成功
```

```python
# 期望失败：使用 pytest.raises 明确捕获异常
def test_delete_nonexistent_product():
    with pytest.raises(Exception):  # 或者检查特定的错误状态码
        product_actions.delete_product(admin_token, invalid_id, shop_id)
```

#### ❌ 错误做法：混合期望（禁止）

```python
# 禁止：将成功和失败都视为"通过"
if response.status_code == 200:
    return True
elif response.status_code == 404:
    return True  # ❌ 错误！404应该被视为失败
else:
    return False
```

```python
# 禁止：try-except 吞掉所有错误
try:
    delete_product(product_id)
except:
    pass  # ❌ 错误！隐藏了真实的失败原因
```

#### 🎯 核心原则

1. **一一对应**：每个 `create_*` 操作必须有且仅有一个对应的 `delete_*` 操作
2. **严格断言**：使用 `assert` 强制要求操作必须成功或必须失败
3. **不兼容**：不能同时期望"成功"和"失败"两种结果都通过
4. **明确意图**：代码要清晰表达预期行为，不要用容错逻辑掩盖问题

#### ⚠️ 常见违规模式

| 违规模式 | 问题 | 正确做法 |
|---------|------|---------|
| `if success or 404: return True` | 模糊处理 | 只接受一种状态 |
| `try-except: pass` | 吞掉异常 | 让异常暴露或明确处理 |
| 双重清理机制 | 资源被删除多次 | 只清理一次 |
| 宽松的返回值 | 返回 True/False 但不断言 | 使用 assert 严格验证 |

### Data Uniqueness

Test data uses random suffixes to avoid conflicts:
```python
unique_suffix = os.urandom(4).hex()
```

### Resource Cleanup

Tests use cleanup lists with reverse-order teardown:
```python
cleanup_functions = [cleanup_shop, cleanup_products, cleanup_users]
for cleanup_func in cleanup_functions:
    cleanup_func()
```

### API Request Handling

All API calls should use `make_request_with_retry()` to handle rate limiting:
```python
def request_func():
    return requests.post(url, json=payload, headers=headers)

response = make_request_with_retry(request_func)
```

### Test Fixtures

- Use session-scoped fixtures for expensive resources (tokens, database IDs)
- Use function-scoped fixtures for test-specific resources
- Automatic cleanup in fixture teardown

### Testing Utilities

**ResponseValidator** (`test/utils/response_validator.py`):
- Chainable validation API for API responses
- Handles multiple naming conventions (PascalCase, camelCase, snake_case)
- Common validations: status codes, field existence, field values, list lengths

**FieldResolver** (`test/utils/field_resolver.py`):
- Extracts nested fields from JSON responses using dot notation
- Auto-handles ID field variants (`ID`, `id`, `Id`, `shopId`, `shop_id`, etc.)
- Normalizes keys between naming conventions

Usage example:
```python
ResponseValidator(response)
    .status(200)
    .has_data()
    .field_equals("data.name", "Expected Name")
    .list_length("data.products", min_length=1)
```

## Database Operations

```bash
# Backup database
docker exec orderease-mysql mysqldump -u root -p123456 orderease > backup.sql

# Restore database
docker exec -i orderease-mysql mysql -u root -p123456 orderease < backup.sql

# Access MySQL CLI
docker exec -it orderease-mysql mysql -u root -p123456
```

## Persistent Data

Stored in `deploy/data/`:
- `uploads/` - User uploaded files
- `logs/` - Application logs
- `mysql/` - Database data

## Additional Deployment Options

### HAProxy Reverse Proxy

For production deployments requiring SSL termination or load balancing, HAProxy can be used as a reverse proxy in front of the OrderEase container.

**See**: `docs/haproxy/HAProxy-Docker-QuickStart.md` for complete guide

**Key Points**:
- HAProxy listens on port 80, forwards to backend port 8080
- Linux deployments: use `docker0` bridge IP (e.g., `10.255.0.1`) instead of `host.docker.internal`
- Always validate HAProxy configuration before starting container:
  ```bash
  docker run --rm -v ~/haproxy-config/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro \
    haproxy:latest haproxy -c -f /usr/local/etc/haproxy/haproxy.cfg
  ```
- Use specific port bindings (not ranges) to avoid blocking ports like SSH 22

## Troubleshooting

**Container won't start**:
- Check port conflicts: `netstat -ano | findstr ":8080"` (Windows) or `lsof -i :8080` (Linux)
- View container logs: `docker-compose logs orderease-app`
- Check Docker is running: `docker info`

**Database connection issues**:
- Check MySQL container: `docker-compose ps mysql`
- Test connection: `docker exec orderease-mysql mysql -u` root -p<password> -e "SELECT 1"`
- Verify network: `docker network inspect deploy_orderease-network`

**Frontend not accessible**:
- Check static files: `docker exec orderease-app ls -la /app/static/`
- Test health: `curl http://localhost:8080/order-ease-iui/`
- Verify health check: `docker inspect orderease-app | jq '.[0].State.Health'`

**PowerShell script execution policy error**:
- Error: "无法加载文件 xxx.ps1，因为在此系统上禁止运行脚本"
- Solution: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

**CI/CD integration test timeout**:
- Check MySQL service health in GitHub Actions logs
- Verify app container startup: look for "服务器启动" message
- Check API base URL is correct in test environment

## Cross-Repository Context

This repository is part of a larger OrderEase project. The parent-level `CLAUDE.md` (at `D:\local_code_repo\OrderEase\CLAUDE.md`) provides:
- Overall architecture overview across all repositories
- Backend (Go) DDD architecture patterns
- Frontend Vue 3 architecture and conventions
- Key concepts like multi-tenant shop context, ID handling, authentication flows

When working on features that span multiple repositories (e.g., adding a new API endpoint), consult the parent CLAUDE.md for the full context.
