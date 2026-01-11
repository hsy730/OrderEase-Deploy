# OrderEase 自动部署脚本
# 用法: .\deploy.ps1 [-SkipPull]

param(
    [switch]$SkipPull,
    [switch]$OverrideConfig
)

# 颜色输出
function Write-Info { Write-Host "[INFO] $args" -ForegroundColor Cyan }
function Write-Success { Write-Host "[SUCCESS] $args" -ForegroundColor Green }
function Write-Warning { Write-Host "[WARNING] $args" -ForegroundColor Yellow }
function Write-Error { Write-Host "[ERROR] $args" -ForegroundColor Red }

# 显示标题
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    OrderEase 本地部署脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 配置
$IMAGE_NAME = "siyuanh640/orderease"
$IMAGE_TAG = "latest"
$DEPLOY_DIR = Join-Path $PSScriptRoot "orderease-deploy"
$FULL_IMAGE = $IMAGE_NAME + ":" + $IMAGE_TAG

# 检查 Docker
Write-Info "检查 Docker 环境..."
try {
    $null = docker --version 2>&1
} catch {
    Write-Error "Docker 未安装"
    exit 1
}
try {
    $null = docker info 2>&1
} catch {
    Write-Error "Docker 未运行"
    exit 1
}
Write-Success "Docker 环境正常"

# 创建目录
Write-Info "创建部署目录..."
if ((Test-Path $DEPLOY_DIR) -and (-not $OverrideConfig)) {
    $continue = Read-Host "目录已存在，是否覆盖？(y/N)"
    if ($continue -ne "y") { exit 0 }
}

$dirs = @("config", "data\uploads", "data\logs", "data\mysql")
foreach ($d in $dirs) {
    $path = Join-Path $DEPLOY_DIR $d
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
}
Write-Success "目录创建完成"

# 生成密码
$MYSQL_PWD = -join ((48..57)+(65..90)+(97..122) | Get-Random -Count 16 | % {[char]$_})
$JWT_SECRET = -join ((97..102)+(48..57) | Get-Random -Count 64 | % {[char]$_})

# 生成 docker-compose.yml
Write-Info "生成配置文件..."
$compose = @"
version: '3.8'
services:
  orderease-app:
    image: $FULL_IMAGE
    container_name: orderease-app
    ports:
      - "8080:8080"
    depends_on:
      mysql:
        condition: service_healthy
    environment:
      - DB_HOST=mysql
      - DB_PORT=3306
      - DB_USERNAME=root
      - DB_PASSWORD=$MYSQL_PWD
      - DB_NAME=orderease
      - JWT_SECRET=$JWT_SECRET
      - JWT_EXPIRATION=7200
      - TZ=Asia/Shanghai
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
      - MYSQL_ROOT_PASSWORD=$MYSQL_PWD
      - MYSQL_DATABASE=orderease
      - TZ=Asia/Shanghai
    volumes:
      - ./data/mysql:/var/lib/mysql
    ports:
      - "3306:3306"
    networks:
      - orderease-network
    restart: unless-stopped
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p$MYSQL_PWD"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
networks:
  orderease-network:
    driver: bridge
"@

# 生成 config.yaml
$config = @"
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
  password: $MYSQL_PWD
  dbname: orderease
  charset: utf8mb4
  parseTime: true
  loc: Local
  logLevel: 4
jwt:
  secret: "$JWT_SECRET"
  expiration: 7200
"@

# 写入文件
New-Item -ItemType Directory -Force (Join-Path $DEPLOY_DIR "config") | Out-Null
$compose | Out-File -FilePath (Join-Path $DEPLOY_DIR "docker-compose.yml") -Encoding UTF8
$config | Out-File -FilePath (Join-Path $DEPLOY_DIR "config\config.yaml") -Encoding UTF8
Write-Success "配置文件生成完成"

# 拉取镜像
if (-not $SkipPull) {
    Write-Info "拉取镜像: $FULL_IMAGE..."
    docker pull $FULL_IMAGE
    Write-Success "镜像拉取完成"
}

# 启动服务
Write-Info "启动服务..."
Push-Location $DEPLOY_DIR
docker compose up -d
Pop-Location
Write-Success "服务启动完成"

# 等待就绪
Write-Info "等待服务启动..."
$sleep = 0
while ($sleep -lt 60) {
    try {
        Invoke-WebRequest -Uri "http://localhost:8080/order-ease-iui/" -UseBasicParsing -TimeoutSec 2 | Out-Null
        Write-Success "服务已就绪"
        break
    }
    catch {
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 2
        $sleep++
    }
}

# 显示结果
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "        部署成功！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "访问地址：" -ForegroundColor Cyan
Write-Host "  前台: http://localhost:8080/order-ease-iui/" -ForegroundColor Yellow
Write-Host "  后台: http://localhost:8080/order-ease-adminiui/" -ForegroundColor Yellow
Write-Host "  API:  http://localhost:8080/api/order-ease/v1/" -ForegroundColor Yellow
Write-Host ""
Write-Host "默认账户: admin / Admin@123456" -ForegroundColor Yellow
Write-Host ""
Write-Host "常用命令：" -ForegroundColor Cyan
Write-Host "  cd $DEPLOY_DIR"
Write-Host "  docker compose logs -f"
Write-Host "  docker compose stop"
Write-Host "  docker compose restart"
Write-Host "  docker compose down"
Write-Host ""
Write-Host "数据库密码: $MYSQL_PWD" -ForegroundColor Red
Write-Host "请妥善保管此密码！"
Write-Host ""

