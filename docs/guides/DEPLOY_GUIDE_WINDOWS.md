# OrderEase Windows 部署指南

## 目录
- [前置要求](#前置要求)
- [快速开始](#快速开始)
- [详细说明](#详细说明)
- [常用操作](#常用操作)
- [故障排查](#故障排查)

---

## 前置要求

### 1. 安装 Docker Desktop
下载并安装 Docker Desktop for Windows：
- 官方下载地址：https://www.docker.com/products/docker-desktop/
- 安装完成后启动 Docker Desktop
- 确保 Docker 状态为运行中

### 2. 验证 Docker 安装
打开 PowerShell，运行以下命令：
```powershell
docker --version
docker info
```

### 3. 配置 PowerShell 执行策略
Windows PowerShell 默认禁止运行未签名的脚本，需要先配置执行策略。

打开 **PowerShell（以管理员身份运行）**，执行以下命令：

```powershell
# 查看当前执行策略
Get-ExecutionPolicy

# 临时允许当前会话运行脚本（推荐，仅对当前窗口有效）
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 或者永久修改执行策略（需要管理员权限）
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**执行策略说明**：
- `Bypass` - 不阻止任何脚本，临时使用推荐
- `RemoteSigned` - 允许运行本地脚本，远程脚本需要签名（推荐用于日常开发）
- `Restricted` - 默认策略，不允许运行任何脚本

### 4. 准备部署文件
确保你已经获取了 `OrderEase-Deploy` 目录，其中包含：
- `deploy.ps1` - 自动部署脚本

---

## 快速开始

### 前置步骤：允许脚本执行

**首次运行前，必须在 PowerShell 窗口中执行以下命令**：

```powershell
# 临时允许当前会话运行脚本（推荐方式）
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

> ⚠️ **注意**：此命令仅对当前 PowerShell 窗口有效，关闭窗口后失效。每次重新打开 PowerShell 运行脚本前都需要执行此命令。

### 方法一：全自动部署（推荐）
打开 PowerShell，进入部署目录，运行：
```powershell
cd D:\local_code_repo\OrderEase-Deploy

# 首次运行前执行此命令
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 然后运行部署脚本
.\deploy.ps1
```

### 如果遇到执行策略错误
如果看到错误提示 **"无法加载文件 xxx.ps1，因为在此系统上禁止运行脚本"**，说明执行策略限制生效。

**解决方案**：
```powershell
# 方案 A：临时绕过（推荐，安全）
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 方案 B：使用 PowerShell 的 -ExecutionPolicy 参数
powershell -ExecutionPolicy Bypass -File .\deploy.ps1

# 方案 C：永久修改为允许本地脚本（需要管理员权限）
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
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
```powershell
.\deploy.ps1 -SkipPull
```

### 方法三：强制覆盖现有配置
```powershell
.\deploy.ps1 -OverrideConfig
```

### 组合参数示例
```powershell
# 跳过拉取并覆盖配置
.\deploy.ps1 -SkipPull -OverrideConfig
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

---

## 常用操作

### 查看服务状态
```powershell
cd orderease-deploy
docker compose ps
```

### 查看日志
```powershell
# 查看所有服务日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f orderease-app
docker compose logs -f mysql
```

### 停止服务
```powershell
docker compose stop
```

### 启动服务
```powershell
docker compose start
```

### 重启服务
```powershell
docker compose restart
```

### 停止并删除容器
```powershell
docker compose down
```

### 停止并删除容器及数据卷（谨慎使用）
```powershell
docker compose down -v
```

### 更新镜像并重新部署
```powershell
# 拉取最新镜像
docker pull siyuanh640/orderease:latest

# 重新创建容器
docker compose up -d --force-recreate
```

---

## 访问应用

部署成功后，可以通过以下地址访问：

| 访问类型 | 地址 |
|----------|------|
| 前台用户界面 | http://localhost:8080/order-ease-iui/ |
| 后台管理界面 | http://localhost:8080/order-ease-adminiui/ |
| API 接口 | http://localhost:8080/api/order-ease/v1/ |

### 默认账户
- 用户名：`admin`
- 密码：`Admin@123456`

> ⚠️ **重要提示**：部署完成后会显示随机生成的数据库密码，请妥善保存该密码！

---

## 故障排查

### 1. 端口被占用
**错误信息**：`Bind for 0.0.0.0:8080 failed: port is already allocated`

**解决方案**：
```powershell
# 查看占用 8080 端口的进程
netstat -ano | findstr :8080

# 结束该进程（替换 <PID> 为实际进程 ID）
taskkill /PID <PID> /F
```

### 2. Docker 未运行
**错误信息**：`Docker 未运行`

**解决方案**：
- 启动 Docker Desktop
- 等待 Docker 完全启动（状态栏图标不再动画）
- 重新运行部署脚本

### 3. 容器启动失败
**排查步骤**：
```powershell
# 查看容器状态
docker compose ps

# 查看详细日志
docker compose logs orderease-app
docker compose logs mysql
```

### 4. 服务无法访问
**检查清单**：
1. 确认容器状态：`docker compose ps`
2. 检查健康状态：`docker inspect orderease-app | Select-String Health`
3. 查看应用日志：`docker compose logs -f orderease-app`
4. 尝试重启：`docker compose restart`

### 5. 数据库连接问题
**排查步骤**：
```powershell
# 检查 MySQL 容器状态
docker exec orderease-mysql mysqladmin ping -h localhost -u root -p<你的密码>

# 进入 MySQL 容器
docker exec -it orderease-mysql bash

# 登录 MySQL
mysql -u root -p
```

### 6. 脚本执行权限问题
**错误信息**：`无法加载文件 deploy.ps1，因为在此系统上禁止运行脚本`

**原因**：Windows PowerShell 默认执行策略为 `Restricted`，禁止运行未签名脚本。

**解决方案**：
```powershell
# 方案 A：临时允许（推荐，每次打开 PowerShell 都要执行）
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 方案 B：直接用参数绕过执行策略
powershell -ExecutionPolicy Bypass -File .\deploy.ps1

# 方案 C：永久修改用户级策略
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**推荐使用方案 A 或 B**，安全性更高且不影响系统全局设置。

### 7. 中文乱码问题
如果脚本执行时出现中文乱码：

```powershell
# 方法一：使用 UTF-8 编码重新保存文件
[System.IO.File]::ReadAllText('deploy.ps1', [System.Text.Encoding]::UTF8) | 
    Set-Content -Path 'deploy.ps1' -Encoding UTF8

# 方法二：设置 PowerShell 控制台编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001
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

---

## 安全建议

1. **修改默认密码**：首次登录后立即修改管理员密码
2. **保护数据库密码**：妥善保存部署时生成的随机密码
3. **防火墙设置**：生产环境建议配置防火墙规则
4. **定期备份**：定期备份 `data/mysql` 目录

---

## 卸载

### 完全卸载 OrderEase
```powershell
# 1. 停止并删除容器
cd orderease-deploy
docker compose down -v

# 2. 删除部署目录
cd ..
Remove-Item -Recurse -Force orderease-deploy

# 3. （可选）删除 Docker 镜像
docker rmi siyuanh640/orderease:latest
docker rmi mysql:8.0
```

---

## 技术支持

如遇到问题，请：
1. 查看上述故障排查章节
2. 检查容器日志：`docker compose logs -f`
3. 提交 Issue 并附上相关日志信息

---

**文档版本**：1.0  
**更新日期**：2026-01-11
