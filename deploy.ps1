# OrderEase 自动部署脚本
# 用途：从 Docker Hub 拉取镜像并启动服务
# 使用方法：.\deploy.ps1

param(
    [switch]$SkipPull,
    [switch]$OverrideConfig
)

# 配置变量
$IMAGE_NAME = "siyuanh640/orderease"
$IMAGE_TAG = "latest"
$DEPLOY_DIR = Join-Path $PSScriptRoot "orderease-deploy"

# 颜色函数
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Info { Write-ColorOutput Cyan "[INFO] $args" }
function Write-Success { Write-ColorOutput Green "[SUCCESS] $args" }
function Write-Warning { Write-ColorOutput Yellow "[WARNING] $args" }
function Write-Error { Write-ColorOutput Red "[ERROR] $args" }

# 打印标题
function Show-Header {
    Write-Output ""
    Write-ColorOutput Cyan "========================================"
    Write-ColorOutput Cyan "    OrderEase 本地部署脚本"
    Write-ColorOutput Cyan "========================================"
    Write-Output ""
}

# 检查 Docker 环境
function Test-DockerEnvironment {
    Write-Info "检查 Docker 环境..."

    try {
        $null = docker --version
        Write-Success "Docker 已安装"
    }
    catch {
        Write-Error "Docker 未安装，请先安装 Docker Desktop"
        Write-Output "下载地址: https://www.docker.com/products/docker-desktop/"
        exit 1
    }

    try {
        $null = docker info
        Write-Success "Docker 守护进程运行中"
    }
    catch {
        Write-Error "Docker 守护进程未运行，请启动 Docker Desktop"
        exit 1
    }

    try {
        $null = docker compose version
        Write-Success "Docker Compose 可用"
    }
    catch {
        Write-Error "Docker Compose 不可用"
        exit 1
    }
}

# 检查端口占用
function Test-PortsInUse {
    Write-Info "检查端口占用..."

    $port8080 = Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue
    if ($port8080) {
        Write-Warning "端口 8080 已被占用"
        $continue = Read-Host "是否继续部署？(y/N)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            Write-Info "部署已取消"
            exit 0
        }
    }

    $port3306 = Get-NetTCPConnection -LocalPort 3306 -State Listen -ErrorAction SilentlyContinue
    if ($port3306) {
        Write-Warning "端口 3306 已被占用，如果有其他 MySQL 实例可能会冲突"
        $continue = Read-Host "是否继续部署？(y/N)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            Write-Info "部署已取消"
            exit 0
        }
    }
}

# 创建部署目录
function New-DeployDirectory {
    Write-Info "创建部署目录..."

    if (Test-Path $DEPLOY_DIR) {
        if (-not $OverrideConfig) {
            Write-Warning "部署目录已存在: $DEPLOY_DIR"
            $continue = Read-Host "是否覆盖现有配置？(y/N)"
            if ($continue -ne "y" -and $continue -ne "Y") {
                Write-Info "保留现有配置"
                return
            }
        }
        Write-Warning "将覆盖现有配置文件..."
    }

    $directories = @(
        "$DEPLOY_DIR\config",
        "$DEPLOY_DIR\data\uploads",
        "$DEPLOY_DIR\data\logs",
        "$DEPLOY_DIR\data\mysql"
    )

    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }

    Write-Success "部署目录创建完成: $DEPLOY_DIR"
}

# 生成配置文件
function New-ConfigurationFiles {
    Write-Info "生成配置文件..."

    # 生成随机密码
    $MYSQL_PASSWORD = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 16 | ForEach-Object { [char]$_ })
    $JWT_SECRET = -join ((97..102) + (48..57) | Get-Random -Count 64 | ForEach-Object { [char]$_ })

    # 生成 .env 文件
    $envContent = @"
# ============= 数据库配置 =============
MYSQL_ROOT_PASSWORD=$MYSQL_PASSWORD
MYSQL_DATABASE=orderease

# ============= JWT 配置 =============
JWT_SECRET=$JWT_SECRET
JWT_EXPIRATION=7200

# ============= 时区配置 =============
TZ=Asia/Shanghai

# ============= 端口配置 =============
APP_PORT=8080
MYSQL_PORT=3306
"@

    # 生成 config.yaml
    $configContent = @"
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
  password: $MYSQL_PASSWORD
  dbname: orderease
  charset: utf8mb4
  parseTime: true
  loc: Local
  logLevel: 4

jwt:
  secret: "$JWT_SECRET"
  expiration: 7200
"@

    # 生成 docker-compose.yml
    $dockerComposeContent = @"
version: '3.8'

services:
  orderease-app:
    image: $IMAGE_NAME`:$IMAGE_TAG
    container_name: orderease-app
    ports:
      - "`${APP_PORT:-8080}:8080"
    depends_on:
      mysql:
        condition: service_healthy
    environment:
      - DB_HOST=mysql
      - DB_PORT=3306
      - DB_USERNAME=root
      - DB_PASSWORD=`${MYSQL_ROOT_PASSWORD}
      - DB_NAME=orderease
      - JWT_SECRET=`${JWT_SECRET}
      - JWT_EXPIRATION=7200
      - TZ=`${TZ:-Asia/Shanghai}
    volumes:
      - ./data/uploads:/app/uploads
      - ./data/logs:/app/logs
      - ./config/config.yaml:/app/config/config.yaml:ro
    networks:
      - orderease-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:8080/order-ease-iui/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  mysql:
    image: mysql:8.0
    container_name: orderease-mysql
    environment:
      - MYSQL_ROOT_PASSWORD=`${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=orderease
      - TZ=`${TZ:-Asia/Shanghai}
    volumes:
      - ./data/mysql:/var/lib/mysql
    ports:
      - "`${MYSQL_PORT:-3306}:3306"
    networks:
      - orderease-network
    restart: unless-stopped
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p"`${MYSQL_ROOT_PASSWORD}`]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

networks:
  orderease-network:
    driver: bridge
"@

    # 写入文件
    $envContent | Out-File -FilePath "$DEPLOY_DIR\.env" -Encoding UTF8
    $configContent | Out-File -FilePath "$DEPLOY_DIR\config\config.yaml" -Encoding UTF8
    $dockerComposeContent | Out-File -FilePath "$DEPLOY_DIR\docker-compose.yml" -Encoding UTF8

    Write-Success "配置文件生成完成"
}

# 拉取 Docker 镜像
function Pull-DockerImage {
    Write-Info "拉取 Docker 镜像: $IMAGE_NAME`:$IMAGE_TAG..."

    $images = docker images | Select-String "$IMAGE_NAME.*$IMAGE_TAG"

    if ($images -and -not $SkipPull) {
        Write-Warning "镜像已存在，跳过拉取（使用 -SkipPull 强制重新拉取）"
    }
    elseif (-not $SkipPull) {
        docker pull "$IMAGE_NAME`:$IMAGE_TAG"
    }

    Write-Success "镜像准备完成"
}

# 启动服务
function Start-Services {
    Write-Info "启动 OrderEase 服务..."

    Push-Location $DEPLOY_DIR

    # 确保数据目录存在
    $dataDirs = @("uploads", "logs", "mysql")
    foreach ($dir in $dataDirs) {
        $path = Join-Path $DEPLOY_DIR "data\$dir"
        if (-not (Test-Path $path)) {
            New-Item -ItemType Directory -Path $path -Force | Out-Null
        }
    }

    # 启动服务
    docker compose up -d

    Pop-Location

    Write-Success "服务启动完成"
}

# 等待服务就绪
function Wait-ServiceReady {
    Write-Info "等待服务启动..."

    $maxAttempts = 60
    $attempt = 0

    while ($attempt -lt $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8080/order-ease-iui/" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            Write-Success "服务已就绪"
            return
        }
        catch {
            $attempt++
            Write-Host "." -NoNewline
            Start-Sleep -Seconds 2
        }
    }

    Write-Output ""
    Write-Warning "服务启动时间较长，请检查日志"
}

# 显示部署结果
function Show-DeploymentResult {
    Write-Output ""
    Write-ColorOutput Green "========================================"
    Write-ColorOutput Green "        部署成功！"
    Write-ColorOutput Green "========================================"
    Write-Output ""
    Write-ColorOutput Cyan "访问地址："
    Write-Output "  前台用户: $([ConsoleColor]::Yellow)http://localhost:8080/order-ease-iui/"
    Write-Output "  后台管理: $([ConsoleColor]::Yellow)http://localhost:8080/order-ease-adminiui/"
    Write-Output "  API 接口: $([ConsoleColor]::Yellow)http://localhost:8080/api/order-ease/v1/"
    Write-Output ""
    Write-ColorOutput Cyan "默认账户："
    Write-Output "  用户名: $([ConsoleColor]::Yellow)admin"
    Write-Output "  密码:   $([ConsoleColor]::Yellow)Admin@123456"
    Write-ColorOutput Red "⚠️  请登录后立即修改密码！"
    Write-Output ""
    Write-ColorOutput Cyan "常用命令："
    Write-Output "  进入目录: $([ConsoleColor]::Yellow)cd $DEPLOY_DIR"
    Write-Output "  查看日志: $([ConsoleColor]::Yellow)docker compose logs -f"
    Write-Output "  停止服务: $([ConsoleColor]::Yellow)docker compose stop"
    Write-Output "  重启服务: $([ConsoleColor]::Yellow)docker compose restart"
    Write-Output "  删除服务: $([ConsoleColor]::Yellow)docker compose down"
    Write-Output ""
    Write-ColorOutput Cyan "配置文件位置："
    Write-Output "  $DEPLOY_DIR\docker-compose.yml"
    Write-Output "  $DEPLOY_DIR\.env"
    Write-Output "  $DEPLOY_DIR\config\config.yaml"
    Write-Output ""
    Write-ColorOutput Cyan "数据持久化目录："
    Write-Output "  $DEPLOY_DIR\data\uploads   # 上传文件"
    Write-Output "  $DEPLOY_DIR\data\logs      # 应用日志"
    Write-Output "  $DEPLOY_DIR\data\mysql    # 数据库数据"
    Write-Output ""
}

# 主函数
function Main {
    Show-Header

    # 检查环境
    Test-DockerEnvironment
    Test-PortsInUse

    # 创建配置
    New-DeployDirectory
    New-ConfigurationFiles

    # 拉取镜像并启动
    Pull-DockerImage
    Start-Services

    # 等待服务就绪
    Wait-ServiceReady

    # 显示结果
    Show-DeploymentResult
}

# 执行主函数
Main
