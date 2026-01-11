# OrderEase 本地部署指南（Docker Hub 镜像）

## 目录

1. [环境准备](#环境准备)
2. [拉取镜像](#拉取镜像)
3. [配置说明](#配置说明)
4. [启动服务](#启动服务)
5. [访问应用](#访问应用)
6. [管理命令](#管理命令)
7. [故障排查](#故障排查)

---

## 环境准备

### 系统要求

| 组件 | 最低要求 |
|------|----------|
| 操作系统 | Linux / macOS / Windows (支持 Docker) |
| Docker | 20.10+ |
| Docker Compose | 2.0+ |
| 内存 | 4GB+ |
| 磁盘空间 | 10GB+ |

### 安装 Docker

**Windows:**
```powershell
# 下载并安装 Docker Desktop
# https://www.docker.com/products/docker-desktop/
```

**Linux (Ubuntu/Debian):**
```bash
# 安装 Docker
curl -fsSL https://get.docker.com | bash

# 安装 Docker Compose
sudo apt-get install docker-compose-plugin

# 添加当前用户到 docker 组
sudo usermod -aG docker $USER
newgrp docker
```

**macOS:**
```bash
# 使用 Homebrew 安装
brew install --cask docker
```

---

## 拉取镜像

### Docker Hub 镜像信息

- **镜像地址**: `docker.io/siyuanh640/orderease`
- **标签策略**:
  - `latest` - 最新稳定版本（推荐）
  - `main` - main 分支构建版本
  - `pr-{number}` - PR 测试版本

### 拉取镜像

```bash
# 拉取最新版本
docker pull siyuanh640/orderease:latest

# 查看已拉取的镜像
docker images | grep orderease
```

**预期输出:**
```
siyuanh640/orderease   latest   abc123def456   2 minutes ago   150MB
```

---

## 配置说明

### 目录结构

创建部署目录：

```bash
mkdir -p orderease-deploy/{config,data/{uploads,logs,mysql}}
cd orderease-deploy
```

目录结构：
```
orderease-deploy/
├── docker-compose.yml      # 编排配置
├── .env                    # 环境变量
└── config/
    └── config.yaml         # 应用配置
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  # 应用服务
  orderease-app:
    image: siyuanh640/orderease:latest
    container_name: orderease-app
    ports:
      - "8080:8080"
    depends_on:
      - mysql
    environment:
      - DB_HOST=mysql
      - DB_PORT=3306
      - DB_USERNAME=root
      - DB_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - DB_NAME=orderease
      - JWT_SECRET=${JWT_SECRET}
      - JWT_EXPIRATION=7200
      - TZ=Asia/Shanghai
    volumes:
      - ./data/uploads:/app/uploads
      - ./data/logs:/app/logs
      - ./config/config.yaml:/app/config/config.yaml:ro
    networks:
      - orderease-network
    restart: unless-stopped

  # MySQL数据库
  mysql:
    image: mysql:8.0
    container_name: orderease-mysql
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=orderease
      - TZ=Asia/Shanghai
    volumes:
      - ./data/mysql:/var/lib/mysql
    ports:
      - "${MYSQL_PORT:-3306}:3306"
    networks:
      - orderease-network
    restart: unless-stopped
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci

networks:
  orderease-network:
    driver: bridge
```

### .env 文件

创建 `.env` 文件（不要使用弱密码）：

```bash
cat > .env << 'EOF'
# ============= 数据库配置 =============
MYSQL_ROOT_PASSWORD=YourStrongPassword123!
MYSQL_DATABASE=orderease

# ============= JWT 配置 =============
JWT_SECRET=$(openssl rand -hex 32)
JWT_EXPIRATION=7200

# ============= 时区配置 =============
TZ=Asia/Shanghai

# ============= 端口配置 =============
APP_PORT=8080
MYSQL_PORT=3306
EOF
```

### config.yaml

创建 `config/config.yaml`：

```bash
mkdir -p config
cat > config/config.yaml << 'EOF'
server:
  port: 8080
  basePath: "/api/order-ease/v1"
  host: "0.0.0.0"
  domain: "localhost"
  allowedOrigins:
    - "http://localhost:8080"

database:
  driver: mysql
  host: mysql
  port: 3306
  username: root
  password: YourStrongPassword123!
  dbname: orderease
  charset: utf8mb4
  parseTime: true
  loc: Local
  logLevel: 4

jwt:
  secret: "YOUR_JWT_SECRET_HERE"
  expiration: 7200
EOF
```

**重要**: 将 `config.yaml` 中的 `password` 和 `secret` 替换为 `.env` 文件中的实际值。

---

## 启动服务

### 首次启动

```bash
# 1. 进入部署目录
cd orderease-deploy

# 2. 创建数据目录
mkdir -p data/{uploads,logs,mysql}

# 3. 启动服务
docker-compose up -d

# 4. 查看启动日志
docker-compose logs -f
```

**预期输出:**
```
orderease-mysql  | [Note] mysqld: ready for connections.
orderease-app    | 2026-01-11 16:00:00 [INFO] 服务启动...
orderease-app    | 2026-01-11 16:00:01 [INFO] 配置加载成功
```

### 验证服务状态

```bash
# 查看容器状态
docker-compose ps

# 应该显示两个容器都在运行
# NAME              STATUS
# orderease-app     Up (healthy)
# orderease-mysql   Up (healthy)
```

### 健康检查

```bash
# 等待服务启动完成（约30秒）
sleep 30

# 检查应用健康状态
curl http://localhost:8080/order-ease-iui/

# 预期返回 HTML 内容或 200 状态码
```

---

## 访问应用

### 访问地址

| 组件 | 地址 | 说明 |
|------|------|------|
| 前台用户界面 | http://localhost:8080/order-ease-iui/ | 客户访问 |
| 后台管理界面 | http://localhost:8080/order-ease-adminiui/ | 管理员登录 |
| API 接口 | http://localhost:8080/api/order-ease/v1/ | REST API |

### 默认账户

```
管理员账户:
用户名: admin
密码: Admin@123456
```

**⚠️ 重要**: 首次登录后请立即修改默认密码！

---

## 管理命令

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 只查看应用日志
docker-compose logs -f orderease-app

# 只查看数据库日志
docker-compose logs -f mysql

# 查看最近100行日志
docker-compose logs --tail=100 orderease-app
```

### 服务管理

```bash
# 停止服务
docker-compose stop

# 启动服务
docker-compose start

# 重启服务
docker-compose restart

# 重启单个服务
docker-compose restart orderease-app

# 停止并删除容器
docker-compose down

# 停止并删除容器和数据卷（危险操作！）
docker-compose down -v
```

### 更新镜像

```bash
# 拉取最新镜像
docker pull siyuanh640/orderease:latest

# 停止并删除旧容器
docker-compose down

# 重新启动（使用新镜像）
docker-compose up -d

# 查看新容器状态
docker-compose ps
```

### 进入容器

```bash
# 进入应用容器
docker exec -it orderease-app sh

# 进入数据库容器
docker exec -it orderease-mysql mysql -u root -p
```

---

## 数据管理

### 数据备份

```bash
# 备份数据库
docker exec orderease-mysql mysqldump \
  -u root -pYourStrongPassword123! \
  orderease > backup_$(date +%Y%m%d_%H%M%S).sql

# 备份上传文件
tar -czf uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz data/uploads/
```

### 数据恢复

```bash
# 恢复数据库
docker exec -i orderease-mysql mysql \
  -u root -pYourStrongPassword123! \
  orderease < backup_20260111_160000.sql

# 恢复上传文件
tar -xzf uploads_backup_20260111_160000.tar.gz -C ./
```

### 数据清理

```bash
# 清理上传文件（谨慎操作）
rm -rf data/uploads/*

# 清理日志文件
rm -rf data/logs/*
```

---

## 故障排查

### 容器无法启动

**问题**: 容器启动后立即退出

```bash
# 查看详细日志
docker-compose logs orderease-app

# 常见原因：
# 1. 端口被占用
netstat -ano | findstr :8080  # Windows
netstat -tulpn | grep :8080   # Linux

# 2. 配置文件错误
docker-compose config

# 3. 权限问题
ls -la data/
chmod -R 755 data/
```

### 数据库连接失败

**问题**: 应用无法连接数据库

```bash
# 检查 MySQL 容器状态
docker-compose ps mysql

# 测试数据库连接
docker exec -it orderease-mysql \
  mysql -u root -pYourStrongPassword123! \
  -e "SELECT 1"

# 检查网络连接
docker network inspect orderease-deploy_orderease-network

# 检查环境变量
docker exec orderease-app env | grep DB_
```

### 无法访问 Web 界面

**问题**: 浏览器无法打开页面

```bash
# 1. 检查容器状态
docker-compose ps

# 2. 检查健康状态
curl http://localhost:8080/order-ease-iui/

# 3. 检查防火墙
# Windows: 控制面板 -> 系统和安全 -> Windows 防火墙
# Linux: sudo ufw status

# 4. 检查端口映射
docker port orderease-app
```

### 密码错误

**问题**: 忘记管理员密码

```bash
# 方法1: 重置密码（通过 API）
curl -X POST http://localhost:8080/api/order-ease/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123456"}'

# 方法2: 直接修改数据库
docker exec -it orderease-mysql mysql -u root -p
USE orderease;
UPDATE users SET password='new_hash' WHERE username='admin';
```

---

## 生产环境建议

### 安全加固

1. **修改默认密码**
   ```bash
   # 修改 .env 中的密码
   MYSQL_ROOT_PASSWORD=VeryStrongPasswordHere!
   JWT_SECRET=$(openssl rand -hex 32)
   ```

2. **限制端口暴露**
   ```yaml
   # 在 docker-compose.yml 中注释掉 MySQL 的 ports 配置
   mysql:
     # ports:
     #   - "3306:3306"  # 不对外开放数据库端口
   ```

3. **配置 HTTPS**
   - 使用 Nginx 反向代理
   - 申请 SSL 证书（Let's Encrypt）
   - 启用 HTTPS 强制跳转

4. **配置防火墙**
   ```bash
   # 仅开放必要端口
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw enable
   ```

### 性能优化

1. **资源限制**
   ```yaml
   services:
     orderease-app:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 2G
           reservations:
             cpus: '1'
             memory: 1G
   ```

2. **数据库优化**
   ```bash
   # 编辑 MySQL 配置
   # 添加慢查询日志
   ```

3. **日志管理**
   ```yaml
   services:
     orderease-app:
       logging:
         driver: "json-file"
         options:
           max-size: "10m"
           max-file: "3"
   ```

---

## 卸载

### 完全卸载

```bash
# 停止并删除所有容器
docker-compose down -v

# 删除镜像
docker rmi siyuanh640/orderease:latest

# 删除部署目录
cd ..
rm -rf orderease-deploy
```

---

## 附录

### 镜像版本历史

| 标签 | 说明 | 发布日期 |
|------|------|----------|
| latest | 最新稳定版本 | - |
| main | main 分支构建 | - |
| pr-{n} | Pull Request 测试版本 | - |

### 相关链接

- **Docker Hub**: https://hub.docker.com/r/siyuanh640/orderease
- **GitHub 项目**: https://github.com/hsy730/OrderEase-Deploy
- **问题反馈**: https://github.com/hsy730/OrderEase-Deploy/issues

---

**文档版本**: 1.0
**最后更新**: 2026-01-11
