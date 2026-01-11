# OrderEase Linux 部署指南

## 目录
- [前置要求](#前置要求)
- [快速开始](#快速开始)
- [详细说明](#详细说明)
- [常用操作](#常用操作)
- [故障排查](#故障排查)
- [生产环境配置](#生产环境配置)

---

## 前置要求

### 1. 安装 Docker
#### Ubuntu/Debian
```bash
# 更新包索引
sudo apt-get update

# 安装必要依赖
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# 添加 Docker 官方 GPG 密钥
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 添加 Docker 仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

#### CentOS/RHEL
```bash
# 安装必要依赖
sudo yum install -y yum-utils

# 添加 Docker 仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装 Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. 配置 Docker 用户权限（推荐）
避免每次使用 sudo：
```bash
# 创建 docker 组（如果不存在）
sudo groupadd docker

# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER

# 刷新用户组（需重新登录或执行）
newgrp docker

# 验证（无需 sudo）
docker ps
```

### 3. 验证 Docker 安装
```bash
docker --version
docker info
docker compose version
```

### 4. 准备部署文件
确保你已经获取了 `OrderEase-Deploy` 目录，其中包含：
- `deploy.sh` - 自动部署脚本

---

## 快速开始

### 方法一：全自动部署（推荐）
打开终端，进入部署目录，运行：
```bash
cd /path/to/OrderEase-Deploy
chmod +x deploy.sh
./deploy.sh
```

脚本将自动完成：
1. 检查 Docker 环境
2. 创建部署目录结构
3. 生成随机密码
4. 生成配置文件（docker-compose.yml 和 config.yaml）
5. 拉取 Docker 镜像
6. 启动所有服务
7. 等待服务就绪
8. 显示访问信息和密码

### 方法二：跳过镜像拉取（适用于已有镜像）
```bash
./deploy.sh --skip-pull
```

### 方法三：强制覆盖现有配置
```bash
./deploy.sh --override
```

### 组合参数示例
```bash
# 跳过拉取并覆盖配置
./deploy.sh --skip-pull --override

# 使用后台运行模式
./deploy.sh --detach
```

### 使用 systemd 管理（推荐生产环境）
```bash
# 设置开机自启
sudo systemctl enable docker

# 设置容器开机自启
# 在部署完成后进入部署目录
cd orderease-deploy
docker compose up -d
```

---

## 详细说明

### 部署目录结构
执行脚本后，会在当前目录下生成 `orderease-deploy` 目录：
```
orderease-deploy/
├── docker-compose.yml      # Docker Compose 配置文件
├── config/
│   └── config.yaml        # 应用配置文件
└── data/
    ├── uploads/           # 上传文件存储
    ├── logs/              # 日志文件
    └── mysql/             # MySQL 数据持久化
```

### 服务说明
部署后会启动两个容器：

| 服务 | 容器名 | 端口 | 说明 |
|------|--------|------|------|
| orderease-app | orderease-app | 8080 | 应用服务 |
| mysql | orderease-mysql | 3306 | MySQL 数据库 |

### 网络配置
- 所有服务运行在 `orderease-network` 网络中
- 容器间可通过服务名相互访问

### 资源限制
如需限制容器资源使用，编辑 `docker-compose.yml`：
```yaml
services:
  orderease-app:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

---

## 常用操作

### 查看服务状态
```bash
cd orderease-deploy
docker compose ps
```

### 查看日志
```bash
# 查看所有服务日志（实时）
docker compose logs -f

# 查看特定服务日志
docker compose logs -f orderease-app
docker compose logs -f mysql

# 查看最近 100 行日志
docker compose logs --tail=100 orderease-app
```

### 停止服务
```bash
docker compose stop
```

### 启动服务
```bash
docker compose start
```

### 重启服务
```bash
docker compose restart

# 重启特定服务
docker compose restart orderease-app
```

### 停止并删除容器
```bash
docker compose down
```

### 停止并删除容器及数据卷（谨慎使用）
```bash
docker compose down -v
```

### 更新镜像并重新部署
```bash
# 拉取最新镜像
docker pull siyuanh640/orderease:latest

# 重新创建容器
docker compose up -d --force-recreate

# 或者一键更新
docker compose pull && docker compose up -d --force-recreate
```

### 进入容器
```bash
# 进入应用容器
docker exec -it orderease-app bash

# 进入 MySQL 容器
docker exec -it orderease-mysql bash

# 直接进入 MySQL
docker exec -it orderease-mysql mysql -u root -p
```

### 查看容器资源使用
```bash
docker stats orderease-app orderease-mysql
```

---

## 访问应用

部署成功后，可以通过以下地址访问：

| 访问类型 | 地址 |
|----------|------|
| 前台用户界面 | http://localhost:8080/order-ease-iui/ |
| 后台管理界面 | http://localhost:8080/order-ease-adminiui/ |
| API 接口 | http://localhost:8080/api/order-ease/v1/ |

### 远程访问
如果需要从其他机器访问：
```bash
# 获取服务器 IP
ip addr show   # Linux
hostname -I    # 显示所有 IP

# 使用服务器 IP 访问
# http://<服务器IP>:8080/order-ease-iui/
```

### 默认账户
- 用户名：`admin`
- 密码：`Admin@123456`

> ⚠️ **重要提示**：部署完成后会显示随机生成的数据库密码，请妥善保存该密码！

---

## 故障排查

### 1. 端口被占用
**错误信息**：`Bind for 0.0.0.0:8080 failed: port is already allocated`

**解决方案**：
```bash
# 查看占用 8080 端口的进程
sudo lsof -i :8080
sudo netstat -tulpn | grep 8080

# 结束该进程（替换 <PID> 为实际进程 ID）
sudo kill -9 <PID>

# 或者修改 docker-compose.yml 中的端口映射
```

### 2. 权限问题
**错误信息**：`permission denied`

**解决方案**：
```bash
# 添加用户到 docker 组
sudo usermod -aG docker $USER
newgrp docker

# 修改文件权限
sudo chown -R $USER:$USER orderease-deploy/
chmod -R 755 orderease-deploy/
```

### 3. Docker 服务未运行
**解决方案**：
```bash
# 检查 Docker 状态
sudo systemctl status docker

# 启动 Docker
sudo systemctl start docker

# 设置开机自启
sudo systemctl enable docker
```

### 4. 容器启动失败
**排查步骤**：
```bash
# 查看容器状态
docker compose ps -a

# 查看详细日志
docker compose logs orderease-app
docker compose logs mysql

# 检查容器详情
docker inspect orderease-app
```

### 5. 服务无法访问
**检查清单**：
```bash
# 1. 确认容器状态
docker compose ps

# 2. 检查健康状态
docker inspect orderease-app | grep -A 10 Health

# 3. 检查端口监听
sudo netstat -tulpn | grep 8080

# 4. 测试本地访问
curl http://localhost:8080/order-ease-iui/

# 5. 检查防火墙
sudo ufw status        # Ubuntu
sudo firewall-cmd --list-all  # CentOS
```

### 6. 防火墙配置
```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 8080/tcp
sudo ufw allow 3306/tcp  # 如需外部访问 MySQL

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=3306/tcp
sudo firewall-cmd --reload

# 使用 iptables
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 3306 -j ACCEPT
```

### 7. 数据库连接问题
**排查步骤**：
```bash
# 检查 MySQL 容器状态
docker exec orderease-mysql mysqladmin ping -h localhost -u root -p<你的密码>

# 检查数据库连接
docker exec orderease-mysql mysql -u root -p -e "SHOW DATABASES;"

# 查看数据库日志
docker compose logs mysql | tail -50
```

### 8. 磁盘空间不足
**检查和清理**：
```bash
# 检查磁盘使用
df -h

# 清理 Docker 未使用的资源
docker system prune -a

# 查看容器磁盘使用
docker system df

# 清理日志文件
docker compose logs --tail=0 -f > /dev/null
```

### 9. 内存不足
**检查和优化**：
```bash
# 检查内存使用
free -h

# 查看容器资源使用
docker stats

# 添加 swap（如需要）
sudo dd if=/dev/zero of=/swapfile bs=1G count=4
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 配置修改

### 修改端口
编辑 `orderease-deploy/docker-compose.yml`：
```yaml
services:
  orderease-app:
    ports:
      - "新端口:8080"  # 修改左侧端口号
```

### 修改时区
编辑配置文件中的 `TZ` 环境变量：
```yaml
environment:
  - TZ=Asia/Shanghai  # 修改为你的时区
```

### 修改数据库配置
编辑 `orderease-deploy/config/config.yaml`：
```yaml
database:
  host: mysql
  port: 3306
  username: root
  password: 你的密码  # 修改密码
```

### 使用环境变量
创建 `.env` 文件：
```bash
cd orderease-deploy
cat > .env << EOF
MYSQL_PASSWORD=你的密码
JWT_SECRET=你的密钥
TZ=Asia/Shanghai
EOF
```

修改 `docker-compose.yml` 引用环境变量：
```yaml
environment:
  - DB_PASSWORD=${MYSQL_PASSWORD}
  - TZ=${TZ}
```

---

## 生产环境配置

### 1. 使用 Nginx 反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. 配置 HTTPS（使用 Let's Encrypt）
```bash
# 安装 certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 3. 日志轮转配置
创建 `/etc/logrotate.d/orderease`：
```
/path/to/orderease-deploy/data/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0644 www-data www-data
    sharedscripts
    postrotate
        docker compose restart orderease-app
    endscript
}
```

### 4. 自动备份脚本
创建备份脚本 `backup.sh`：
```bash
#!/bin/bash
BACKUP_DIR="/backups/orderease"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
docker exec orderease-mysql mysqldump -u root -p<密码> orderease > \
    $BACKUP_DIR/mysql_$DATE.sql

# 备份上传文件
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz \
    /path/to/orderease-deploy/data/uploads/

# 删除 7 天前的备份
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

添加到 crontab：
```bash
crontab -e

# 每天凌晨 2 点执行备份
0 2 * * * /path/to/backup.sh >> /var/log/orderease-backup.log 2>&1
```

### 5. 监控和告警
```bash
# 安装监控工具
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v /path/to/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# 使用 cAdvisor 监控容器
docker run -d \
  --name=cadvisor \
  --volume=/:/rootfs:ro \
  --volume=/var/run:/var/run:ro \
  --volume=/sys:/sys:ro \
  --volume=/var/lib/docker/:/var/lib/docker:ro \
  --publish=8081:8080 \
  --detach=true \
  --name=cadvisor \
  gcr.io/cadvisor/cadvisor:latest
```

### 6. 配置系统服务
创建 systemd 服务文件 `/etc/systemd/system/orderease.service`：
```ini
[Unit]
Description=OrderEase Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/orderease-deploy
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable orderease
sudo systemctl start orderease
sudo systemctl status orderease
```

---

## 安全建议

1. **修改默认密码**：首次登录后立即修改管理员密码
2. **保护数据库密码**：妥善保存部署时生成的随机密码
3. **限制端口暴露**：MySQL 端口不要暴露到公网
4. **配置防火墙**：只开放必要的端口
5. **使用 HTTPS**：生产环境务必使用 SSL/TLS
6. **定期备份**：设置自动备份策略
7. **更新镜像**：定期更新 Docker 镜像获取安全补丁
8. **日志审计**：定期检查访问日志和错误日志
9. **资源限制**：设置容器资源使用上限
10. **网络隔离**：使用 Docker 网络隔离不同服务

---

## 卸载

### 完全卸载 OrderEase
```bash
# 1. 停止并删除容器
cd orderease-deploy
docker compose down -v

# 2. 删除部署目录
cd ..
rm -rf orderease-deploy

# 3. （可选）删除 Docker 镜像
docker rmi siyuanh640/orderease:latest
docker rmi mysql:8.0

# 4. （可选）删除 systemd 服务
sudo systemctl stop orderease
sudo systemctl disable orderease
sudo rm /etc/systemd/system/orderease.service
sudo systemctl daemon-reload
```

---

## 性能优化

### 1. MySQL 优化
在 `docker-compose.yml` 中添加：
```yaml
mysql:
  command: >
    --character-set-server=utf8mb4
    --collation-server=utf8mb4_unicode_ci
    --max-connections=200
    --innodb-buffer-pool-size=256M
```

### 2. 应用连接池
在 `config.yaml` 中配置：
```yaml
database:
  maxOpenConns: 100
  maxIdleConns: 10
  connMaxLifetime: 3600
```

### 3. 日志级别调整
```yaml
logging:
  level: INFO  # 生产环境使用 INFO 或 WARN
```

---

## 技术支持

如遇到问题，请：
1. 查看上述故障排查章节
2. 检查容器日志：`docker compose logs -f`
3. 收集系统信息：`docker info`、`docker compose ps -a`
4. 提交 Issue 并附上相关日志信息

### 常用信息收集命令
```bash
# 系统信息
uname -a
cat /etc/os-release

# Docker 信息
docker version
docker compose version
docker info

# 容器状态
docker compose ps -a
docker compose logs --tail=100

# 网络信息
ip addr show
sudo netstat -tulpn
```

---

**文档版本**：1.0  
**更新日期**：2026-01-11  
**支持平台**：Ubuntu 20.04+, Debian 10+, CentOS 7+, RHEL 7+
