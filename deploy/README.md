# OrderEase 统一部署指南

## 架构说明

OrderEase 采用统一部署架构：
- **一个后端服务**：Go 服务提供所有 API
- **两个前端 UI**：共用同一后端服务
  - `/order-ease-iui/` - 客户端 H5
  - `/order-ease-adminiui/` - 管理后台 UI

## 快速部署

### 1. 准备配置文件

```bash
cd OrderEase-Deploy/deploy
cp .env.example .env
```

### 2. 修改配置（仅需修改 3 个参数）

```env
# 后端 API 地址（两个前端共用）
VITE_API_BASE_URL=http://192.168.1.100:8080

# 数据库密码
DB_PASSWORD=YourStrongPassword123!

# JWT 密钥（至少32字节）
JWT_SECRET=your_jwt_secret_minimum_32_bytes_long
```

### 3. 启动服务

```bash
docker-compose up -d
```

### 4. 访问应用

- **客户端 UI**: http://your-server:8080/order-ease-iui/
- **管理后台 UI**: http://your-server:8080/order-ease-adminiui/
- **API 文档**: http://your-server:8080/swagger/index.html

## 环境变量说明

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `VITE_API_BASE_URL` | 后端 API 地址（两个前端共用） | `http://192.168.1.100:8080` |
| `VITE_API_PREFIX` | API 路径前缀 | `/api/order-ease/v1` |
| `DB_HOST` | 数据库主机 | `mysql` |
| `DB_PORT` | 数据库端口 | `3306` |
| `DB_USERNAME` | 数据库用户名 | `root` |
| `DB_PASSWORD` | 数据库密码 | `YourStrongPassword123!` |
| `DB_NAME` | 数据库名称 | `orderease` |
| `JWT_SECRET` | JWT 密钥（≥32字节） | `your_jwt_secret_minimum_32_bytes_long` |
| `JWT_EXPIRATION` | JWT 过期时间（秒） | `7200` |
| `SERVER_HOST` | 服务器监听地址 | `0.0.0.0` |
| `SERVER_PORT` | 服务器端口 | `8080` |
| `TZ` | 时区 | `Asia/Shanghai` |

## 常见场景配置

### 局域网部署

```env
VITE_API_BASE_URL=http://192.168.1.100:8080
DB_PASSWORD=YourStrongPassword123!
JWT_SECRET=your_jwt_secret_minimum_32_bytes_long
```

### 公网域名部署

```env
VITE_API_BASE_URL=https://api.your-domain.com
DB_PASSWORD=YourStrongPassword123!
JWT_SECRET=your_jwt_secret_minimum_32_bytes_long
```

### 本地开发测试

```env
VITE_API_BASE_URL=http://localhost:8080
DB_PASSWORD=YourStrongPassword123!
JWT_SECRET=your_jwt_secret_minimum_32_bytes_long
```