# OrderEase 部署指南

## 📁 目录结构

```
OrderEase-Deploy/
├── build/              # 镜像构建目录
│   ├── Dockerfile      # 多阶段构建文件
│   ├── docker-compose.yml  # 构建配置
│   └── build.sh        # 构建脚本
├── deploy/             # 生产部署目录
│   ├── docker-compose.yml  # 部署配置
│   ├── .env.example    # 环境变量示例
│   ├── config/         # 配置文件目录
│   │   └── config.yaml # 应用配置
│   └── data/           # 数据持久化目录（自动创建）
│       ├── uploads/    # 上传文件
│       ├── logs/       # 应用日志
│       └── mysql/      # 数据库数据
└── README.md           # 本文件
```

## 🚀 快速开始

### 阶段1：构建镜像

```bash
# 进入构建目录
cd d:\local_code_repo\OrderEase-Deploy\build

# 方式1：使用 docker-compose 构建
docker-compose build

# 方式2：使用脚本构建（Linux/Mac）
chmod +x build.sh
./build.sh

# 方式3：直接使用 docker build
docker build -t orderease:latest -f Dockerfile ../..

# 验证镜像
docker images | grep orderease
```

### 阶段2：部署应用

```bash
# 进入部署目录
cd d:\local_code_repo\OrderEase-Deploy\deploy

# 1. 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 文件，修改数据库密码等配置

# 2. 配置应用（可选）
# 编辑 config/config.yaml，修改域名、CORS 等配置

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 检查服务状态
docker-compose ps
```

## 🌐 访问地址

部署成功后，可通过以下地址访问：

- **前台用户界面**: http://localhost:8080/order-ease-iui/
- **后台管理界面**: http://localhost:8080/order-ease-adminiui/
- **API 接口**: http://localhost:8080/api/order-ease/v1/

## 📋 常用命令

### 构建相关

```bash
# 构建指定版本的镜像
docker build -t orderease:v1.0.0 -f build/Dockerfile ..

# 查看镜像
docker images orderease

# 导出镜像
docker save orderease:latest -o orderease.tar

# 导入镜像（在其他机器上）
docker load -i orderease.tar

# 推送镜像到仓库
docker tag orderease:latest registry.example.com/orderease:latest
docker push registry.example.com/orderease:latest
```

### 部署相关

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f orderease-app
docker-compose logs -f mysql

# 进入容器
docker exec -it orderease-app sh
docker exec -it orderease-mysql mysql -u root -p

# 更新应用（重新拉取镜像）
docker-compose pull
docker-compose up -d

# 清理旧数据（危险操作！）
docker-compose down -v
```

### 数据备份

```bash
# 备份数据库
docker exec orderease-mysql mysqldump -u root -p123456 orderease > backup_$(date +%Y%m%d).sql

# 恢复数据库
docker exec -i orderease-mysql mysql -u root -p123456 orderease < backup_20231229.sql

# 备份上传文件
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz deploy/data/uploads/

# 恢复上传文件
tar -xzf uploads_backup_20231229.tar.gz -C deploy/data/
```

## ⚙️ 配置说明

### 环境变量（.env）

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DB_HOST | 数据库主机 | mysql |
| DB_PORT | 数据库端口 | 3306 |
| DB_USERNAME | 数据库用户名 | root |
| DB_PASSWORD | 数据库密码 | 123456 |
| DB_NAME | 数据库名称 | orderease |
| JWT_SECRET | JWT 密钥 | e6jf493kdhbms9ew6mv2v1a4dx2 |
| JWT_EXPIRATION | Token 过期时间（秒） | 7200 |
| SERVER_PORT | 应用端口 | 8080 |
| APP_PORT | 主机映射端口 | 8080 |
| MYSQL_PORT | MySQL 映射端口 | 3306 |

### 应用配置（config/config.yaml）

主要配置项：
- `server.domain`: 服务域名
- `server.allowedOrigins`: CORS 允许的来源
- `database.*`: 数据库连接配置
- `jwt.*`: JWT 认证配置

## 🔒 生产环境建议

### 安全配置

1. **修改默认密码**
   ```bash
   # 修改 MySQL root 密码
   # 修改 JWT Secret 密钥
   ```

2. **限制端口暴露**
   ```yaml
   # 在 docker-compose.yml 中注释掉 MySQL 的 ports 配置
   # 只在容器内部访问数据库
   ```

3. **使用 HTTPS**
   - 配置 Nginx 反向代理
   - 申请 SSL 证书
   - 启用 HTTPS 重定向

4. **配置防火墙**
   ```bash
   # 只允许必要的端口
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw enable
   ```

### 性能优化

1. **资源限制**
   ```yaml
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
   - 调整 MySQL 配置参数
   - 定期清理日志
   - 配置慢查询日志

3. **日志管理**
   - 配置日志轮转
   - 限制日志大小
   - 使用集中式日志收集

## 🐛 故障排查

### 容器无法启动

1. 检查端口占用
   ```bash
   netstat -ano | findstr ":8080"
   netstat -ano | findstr ":3306"
   ```

2. 查看容器日志
   ```bash
   docker-compose logs orderease-app
   ```

3. 检查镜像是否存在
   ```bash
   docker images orderease
   ```

### 数据库连接失败

1. 检查数据库容器状态
   ```bash
   docker-compose ps mysql
   ```

2. 测试数据库连接
   ```bash
   docker exec orderease-mysql mysql -u root -p123456 -e "SELECT 1"
   ```

3. 检查网络连接
   ```bash
   docker network inspect deploy_orderease-network
   ```

### 前端页面无法访问

1. 检查应用容器状态
   ```bash
   docker exec orderease-app ps aux
   ```

2. 检查静态文件
   ```bash
   docker exec orderease-app ls -la /app/static/
   ```

3. 测试健康检查
   ```bash
   curl http://localhost:8080/order-ease-iui/
   ```

## 📝 更新日志

### v1.0.0 (2025-12-29)
- ✅ 初始版本
- ✅ 分离构建和部署流程
- ✅ 支持基于镜像的部署
- ✅ 添加健康检查
- ✅ 完善文档说明

## 🤝 支持

如有问题，请检查：
1. Docker 和 Docker Compose 版本
2. 系统资源是否充足
3. 网络端口是否可用
4. 查看详细日志定位问题

---

**最后更新**: 2025-12-29
