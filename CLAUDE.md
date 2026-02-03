# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OrderEase-Deploy is a unified deployment and comprehensive testing repository for the OrderEase e-commerce management system. It combines multiple components into a single Docker-based deployment:
- **Backend API**: Go-based REST API with DDD architecture (from OrderEase-Golang repository)
- **Admin UI**: Vue 3 admin dashboard for shop owners and administrators (from OrderEase-BackedUI repository)
- **Frontend UI**: Vue 3 mobile-first customer interface (from OrderEase-FrontUI repository)
- **Database**: MySQL 8.0 for data persistence

**Repository Relationships**:
- This repository depends on three separate source repositories checked out during CI/CD
- The multi-stage Docker build copies source code from sibling directories

## Build and Deploy Commands

### Building the Docker Image

```bash
cd build
docker-compose build
```

Alternative build methods:
```bash
# Using build script (Linux/Mac)
chmod +x build.sh && ./build.sh

# Direct Docker build
docker build -t orderease:latest -f build/Dockerfile ../..
```

**Windows Deployment**:
```powershell
# Automated deployment (generates config, pulls image, starts services)
.\deploy.ps1

# Skip image pull if already available
.\deploy.ps1 -SkipPull

# Override existing configuration
.\deploy.ps1 -OverrideConfig
```

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
1. **Stage 1**: Build Backend UI (Node 20 Alpine) - creates admin dashboard
2. **Stage 2**: Build Frontend UI (Node 20 Alpine) - creates customer interface
3. **Stage 3**: Build Go backend (Go 1.24 Alpine) - compiles with UPX compression
4. **Stage 4**: Final runtime (Alpine 3.19) - minimal ~36MB image

**Build Optimizations**:
- UPX binary compression (`upx --best --lzma`) reduces Go binary size significantly
- Go build flags: `-ldflags="-s -w -buildid="` removes symbols and debug info
- Non-root user execution (uid 1000)
- Health checks using wget for container monitoring

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
- Checks out all 4 repositories (Deploy, FrontUI, BackedUI, Golang)
- Creates build context artifact for downstream jobs

**Job 2: Go Unit Tests**
- Runs Go tests with race detection and coverage reporting
- Uploads coverage report as artifact

**Job 3: Build Docker Image**
- Multi-stage Docker build with GitHub Actions caching
- Runs Trivy vulnerability scanner (CRITICAL, HIGH severity)
- Uploads SARIF results to GitHub Security tab

**Job 4: Integration Tests**
- Starts MySQL service container with health checks
- Loads and runs Docker image
- Executes pytest suite with HTML and JUnit reports

**Job 5: Push to Registry**
- Only runs if all tests pass
- Pushes to `docker.io/siyuanh640/orderease`

## Testing Conventions

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

## Troubleshooting

**Container won't start**:
- Check port conflicts: `netstat -ano | findstr ":8080"`
- View container logs: `docker-compose logs orderease-app`

**Database connection issues**:
- Check MySQL container: `docker-compose ps mysql`
- Test connection: `docker exec orderease-mysql mysql -u root -p123456 -e "SELECT 1"`

**Frontend not accessible**:
- Check static files: `docker exec orderease-app ls -la /app/static/`
- Test health: `curl http://localhost:8080/order-ease-iui/`

## Cross-Repository Context

This repository is part of a larger OrderEase project. The parent-level `CLAUDE.md` (at `D:\local_code_repo\OrderEase\CLAUDE.md`) provides:
- Overall architecture overview across all repositories
- Backend (Go) DDD architecture patterns
- Frontend Vue 3 architecture and conventions
- Key concepts like multi-tenant shop context, ID handling, authentication flows

When working on features that span multiple repositories (e.g., adding a new API endpoint), consult the parent CLAUDE.md for the full context.
