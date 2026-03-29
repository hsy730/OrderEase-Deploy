# HAProxy 容器部署完整指南与避坑经验总结

## 一、部署步骤回顾

### 1. 基础安装

```bash
# 拉取镜像
docker pull haproxy:latest

# 创建配置目录
mkdir -p ~/haproxy-config
```

### 2. 配置文件模板（HTTPS 版本）

HTTP 80 端口自动重定向到 HTTPS 443 端口，转发到后端应用 8080 端口

**前置条件：准备 SSL 证书**

```bash
# 将证书和私钥合并为 PEM 格式
cat your_domain.crt your_domain.key > ~/haproxy-config/haproxy.pem

# 或者使用自签名证书（仅测试用）
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj '/CN=localhost'
cat cert.pem key.pem > ~/haproxy-config/haproxy.pem
```

```bash
cat > ~/haproxy-config/haproxy.cfg <<'EOF'
global
    log stdout format raw local0 info
    maxconn 4096
    user haproxy
    group haproxy

defaults
    mode http
    log global
    option httplog
    option dontlognull
    option forwardfor
    option http-server-close
    timeout connect 5s
    timeout client 30s
    timeout server 30s
    timeout http-request 5s

# HTTP 前端：将 80 端口流量重定向到 HTTPS
frontend http_front
    bind *:80
    mode http
    # 重定向到 HTTPS
    redirect scheme https code 301 if !{ ssl_fc }
    
    # 添加简单的安全头
    http-response set-header X-Content-Type-Options nosniff
    http-response set-header X-Frame-Options SAMEORIGIN

# HTTPS 前端：监听 443 端口，使用 SSL 证书
frontend https_front
    bind *:443 ssl crt /etc/haproxy/haproxy.pem
    mode http
    # 添加简单的安全头
    http-response set-header X-Content-Type-Options nosniff
    http-response set-header X-Frame-Options SAMEORIGIN
    
    # 默认后端
    default_backend app_backend

# 后端：转发到本地的8080服务
backend app_backend
    mode http
    balance roundrobin
    # 转发到宿主机的8080端口
    server app1 10.255.0.1:8080 check inter 3s fall 3 rise 2
    
    # 传递真实客户端IP
    http-request set-header X-Real-IP %[src]
    http-request set-header X-Forwarded-For %[src]
EOF
```

### 3. 运行容器

```bash
docker run -d \
  --name haproxy-dynamic \
  --restart unless-stopped \
  -p 80:80 \
  -p 443:443 \
  -v ~/haproxy-config/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro \
  -v ~/haproxy-config/haproxy.pem:/etc/haproxy/haproxy.pem:ro \
  haproxy:latest
```

### 4. 验证部署

```bash
# 检查容器状态
docker ps
docker logs haproxy-dynamic

# 测试访问（HTTP 会自动重定向到 HTTPS）
curl http://localhost:80

# 测试 HTTPS 访问（使用 -k 跳过自签名证书验证）
curl -k https://localhost:443
```

### 5. 重启容器

```bash
# 方式一：重启容器（配置不变）
docker restart haproxy-dynamic

# 方式二：重新创建容器（配置已修改）
docker rm -f haproxy-dynamic
docker run -d \
  --name haproxy-dynamic \
  --restart unless-stopped \
  -p 80:80 \
  -p 443:443 \
  -v ~/haproxy-config/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro \
  -v ~/haproxy-config/haproxy.pem:/etc/haproxy/haproxy.pem:ro \
  haproxy:latest
```

### 6. 更新 SSL 证书

```bash
# 进入证书目录
cd /home/admin/cert

# 合并证书和私钥为 PEM 格式
sudo cat xhsj.xyz.pem xhsj.xyz.key | sudo tee /home/admin/haproxy-config/haproxy.pem > /dev/null

# 设置正确的权限
sudo chmod 644 /home/admin/haproxy-config/haproxy.pem

# 重启 HAProxy 使证书生效
docker restart haproxy-dynamic
```

## 二、踩过的坑及解决方案

### 🕳️ 坑1：端口范围过大导致网络中断

**错误配置：**

```bash
-p 8000-9000:8000-9000  # 监听1000个端口
```

**后果：**

- 可能覆盖SSH 22端口
- Docker生成大量iptables规则，阻塞正常网络
- 远程连接中断

**解决方案：**

- ✅ 只开放必要端口
- ✅ 使用白名单策略
- ✅ 永远不要监听22端口

### 🕳️ 坑2：host.docker.internal 在 Linux 上不可用

**错误配置：**

```bash
server app1 host.docker.internal:8080 check
```

**错误日志：**

```
could not resolve address 'host.docker.internal'
```

**解决方案：**

```bash
# 查找正确的IP
ip addr show docker0 | grep "inet "  # 输出: 10.255.0.1

# 使用正确的IP
server app1 10.255.0.1:8080 check
```

### 🕳️ 坑3：配置文件修改后未生效

**现象：**

- 修改了配置文件
- 容器日志仍显示旧错误

**原因：**

- Docker容器使用内存中的配置缓存
- 只重启不够，需要重新创建

**解决方案：**

```bash
# 必须完全重新创建容器
docker rm -f haproxy-dynamic
docker run ...  # 重新运行
```

### 🕳️ 坑4：配置文件语法错误导致启动失败

**预防措施：**

```bash
# 每次修改后验证语法
docker run --rm \
  -v ~/haproxy-config/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro \
  haproxy:latest \
  haproxy -c -f /usr/local/etc/haproxy/haproxy.cfg
```

### 🕳️ 坑5：Workbench 连接超时

**现象：**

- 执行长时间命令时断开
- 无法查看命令执行结果

**解决方案：**

```bash
# 使用 screen 或 tmux
screen -S haproxy-install
# 执行命令
# Ctrl+A D 分离
screen -r haproxy-install  # 重新连接
```

## 三、最佳实践总结

### 1. 安全第一原则

```bash
# ❌ 错误：开放范围端口
-p 8000-9000:8000-9000

# ✅ 正确：明确列出端口
-p 80:80 -p 443:443
```

### 2. 白名单配置模板

```bash
# HTTP 前端
frontend http_front
    bind *:80
    redirect scheme https code 301 if !{ ssl_fc }

# HTTPS 前端
frontend https_front
    # 明确列出每个端口
    bind *:443 ssl crt /etc/haproxy/haproxy.pem
    # bind *:8443 ssl crt /etc/haproxy/haproxy.pem  # 需要时取消注释
    
    # 根据端口选择后端
    use_backend backend_app1 if { dst_port 443 }
    # use_backend backend_app2 if { dst_port 8443 }
```

### 3. 完整的工作流程

```bash
# 1. 创建配置
vim ~/haproxy-config/haproxy.cfg

# 2. 准备 SSL 证书
# 将证书和私钥合并为 PEM 格式
cat your_domain.crt your_domain.key > ~/haproxy-config/haproxy.pem

# 3. 验证语法
docker run --rm -v ~/haproxy-config/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro haproxy:latest haproxy -c -f /usr/local/etc/haproxy/haproxy.cfg

# 4. 停止旧容器
docker stop haproxy-dynamic
docker rm haproxy-dynamic

# 5. 启动新容器
docker run -d \
  --name haproxy-dynamic \
  --restart unless-stopped \
  -p 80:80 \
  -p 443:443 \
  -v ~/haproxy-config/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro \
  -v ~/haproxy-config/haproxy.pem:/etc/haproxy/haproxy.pem:ro \
  haproxy:latest

# 6. 验证运行
docker logs haproxy-dynamic --tail 20
curl -k https://localhost:443
```

### 4. 监控和维护

```bash
# 查看实时日志
docker logs -f haproxy-dynamic

# 进入容器调试
docker exec -it haproxy-dynamic sh

# 检查端口监听
netstat -tlnp | grep -E ':80|:443'

# 备份配置
cp ~/haproxy-config/haproxy.cfg ~/haproxy-config/haproxy.cfg.$(date +%Y%m%d)
cp ~/haproxy-config/haproxy.pem ~/haproxy-config/haproxy.pem.$(date +%Y%m%d)

# 测试 HTTPS 连接
curl -k https://localhost:443
```

## 四、关键经验总结

### ✅ 必须做的

1. **永远先验证配置语法**
2. **使用明确的端口白名单**
3. **修改配置后必须重新创建容器**
4. **Linux 上使用 docker0 IP 代替 host.docker.internal**
5. **定期备份配置文件和 SSL 证书**
6. **SSL 证书需要将证书和私钥合并为 PEM 格式**

### ❌ 绝不能做的

1. **不要监听大范围端口**（尤其是包含22）
2. **不要直接在生产环境使用 host.docker.internal**
3. **不要修改配置后只 restart，要 rm 后重新 run**
4. **不要在 Workbench 中执行长时间任务而不使用 screen**

### 🔧 故障排查三板斧

```bash
# 1. 看日志
docker logs haproxy-dynamic

# 2. 验证配置
docker run --rm -v ~/haproxy-config/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro haproxy:latest haproxy -c -f /usr/local/etc/haproxy/haproxy.cfg

# 3. 重建容器
docker rm -f haproxy-dynamic && docker run ...

# 4. 检查 SSL 证书
openssl x509 -in ~/haproxy-config/haproxy.pem -text -noout
```

## 五、最终配置模板（可直接使用）

```bash
# 获取正确的 docker0 IP
DOCKER_IP=$(ip addr show docker0 | grep "inet " | awk '{print $2}' | cut -d/ -f1)

# 准备 SSL 证书（如果没有正式证书，使用自签名）
if [ ! -f ~/haproxy-config/haproxy.pem ]; then
    openssl req -x509 -newkey rsa:4096 -keyout ~/haproxy-config/key.pem -out ~/haproxy-config/cert.pem -days 365 -nodes -subj '/CN=localhost'
    cat ~/haproxy-config/cert.pem ~/haproxy-config/key.pem > ~/haproxy-config/haproxy.pem
fi

# 创建配置文件
cat > ~/haproxy-config/haproxy.cfg <<EOF
global
    log stdout format raw local0 info
    maxconn 4096
    user haproxy
    group haproxy

defaults
    mode http
    log global
    option httplog
    option dontlognull
    option forwardfor
    option http-server-close
    timeout connect 5s
    timeout client 30s
    timeout server 30s
    timeout http-request 5s

# HTTP 前端：将 80 端口流量重定向到 HTTPS
frontend http_front
    bind *:80
    mode http
    redirect scheme https code 301 if !{ ssl_fc }
    http-response set-header X-Content-Type-Options nosniff
    http-response set-header X-Frame-Options SAMEORIGIN

# HTTPS 前端：监听 443 端口，使用 SSL 证书
frontend https_front
    bind *:443 ssl crt /etc/haproxy/haproxy.pem
    mode http
    http-response set-header X-Content-Type-Options nosniff
    http-response set-header X-Frame-Options SAMEORIGIN
    default_backend app_backend
    
    # 需要添加新端口时，在这里添加 bind 行
    # bind *:8443 ssl crt /etc/haproxy/haproxy.pem

# 后端：转发到本地的8080服务
backend app_backend
    mode http
    balance roundrobin
    server app1 ${DOCKER_IP}:8080 check inter 3s fall 3 rise 2
    http-request set-header X-Real-IP %[src]
    http-request set-header X-Forwarded-For %[src]
    
    # 添加新后端时，在这里添加 server 行
    # server app2 ${DOCKER_IP}:8081 check
    # server app3 ${DOCKER_IP}:8082 check
EOF

# 运行容器
docker run -d \
  --name haproxy-dynamic \
  --restart unless-stopped \
  -p 80:80 \
  -p 443:443 \
  -v ~/haproxy-config/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro \
  -v ~/haproxy-config/haproxy.pem:/etc/haproxy/haproxy.pem:ro \
  haproxy:latest
```

这个总结包含了我们遇到的所有问题和解决方案，以后部署 HAProxy 时按照这个流程，就能避免踩坑了！
