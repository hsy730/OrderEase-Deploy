# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OrderEase-Deploy is a deployment and testing repository for the OrderEase e-commerce management system. It combines multiple components into a unified Docker deployment:
- **Backend API**: Go-based REST API (from OrderEase-Golang repository)
- **Admin UI**: Vue.js admin dashboard (from OrderEase-BackedUI repository)
- **Frontend UI**: Customer-facing web interface (from OrderEase-FrontUI repository)
- **Database**: MySQL 8.0

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

The `build/Dockerfile` uses a 4-stage build:
1. Stage 1: Build Backend UI (Node 16 Alpine)
2. Stage 2: Build Frontend UI (Node 18 Alpine)
3. Stage 3: Build Go backend (Go 1.22 Alpine)
4. Stage 4: Final runtime image - copies Go binary and UI static files

### Unified Deployment

Single Docker image serves all components:
- Go backend serves both API and static UI files
- Static files served from `/app/static/`:
  - `/order-ease-adminiui/` - Admin dashboard
  - `/order-ease-iui/` - Customer interface
  - API at `/api/order-ease/v1/`

### Configuration

**Environment Variables** (`deploy/.env`):
- `DB_HOST`, `DB_PORT`, `DB_USERNAME`, `DB_PASSWORD`, `DB_NAME` - Database connection
- `JWT_SECRET`, `JWT_EXPIRATION` - Authentication
- `SERVER_PORT`, `APP_PORT`, `MYSQL_PORT` - Port mappings
- `TZ` - Timezone (default: Asia/Shanghai)

**Application Config** (`deploy/config/config.yaml`):
- `server.*`: Base path, host, domain, CORS origins
- `database.*`: MySQL connection settings
- `jwt.*`: JWT authentication settings

### CI/CD Pipeline

Located in `.github/workflows/build-test-deploy.yml`:
1. **Build Phase**: Multi-stage Docker build with image tagging
2. **Test Phase**: Starts MySQL, runs Docker image, executes pytest suite
3. **Deploy Phase**: Pushes to `docker.io/siyuanh640/orderease` (only if tests pass)

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
