#!/bin/bash
#
# OrderEase 自动部署脚本
# 用途：从 Docker Hub 拉取镜像并启动服务
# 使用方法：chmod +x deploy.sh && ./deploy.sh
#

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
IMAGE_NAME="siyuanh640/orderease"
IMAGE_TAG="latest"
DEPLOY_DIR="$(pwd)/orderease-deploy"
MYSQL_PASSWORD=""
JWT_SECRET=""

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 打印标题
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}    OrderEase 本地部署脚本${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# 检查 Docker 是否安装
check_docker() {
    print_info "检查 Docker 环境..."

    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        echo "安装指南：https://docs.docker.com/get-docker/"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        print_error "Docker 守护进程未运行，请启动 Docker"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose 未安装"
        exit 1
    fi

    print_success "Docker 环境检查通过"
}

# 检查端口占用
check_ports() {
    print_info "检查端口占用..."

    # 检查 8080 端口
    if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -an 2>/dev/null | grep ":8080.*LISTEN" >/dev/null; then
        print_warning "端口 8080 已被占用"
        read -p "是否继续部署？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "部署已取消"
            exit 0
        fi
    fi

    # 检查 3306 端口
    if lsof -Pi :3306 -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -an 2>/dev/null | grep ":3306.*LISTEN" >/dev/null; then
        print_warning "端口 3306 已被占用，如果有其他 MySQL 实例可能会冲突"
        read -p "是否继续部署？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "部署已取消"
            exit 0
        fi
    fi
}

# 创建部署目录
create_deploy_dir() {
    print_info "创建部署目录..."

    if [ -d "$DEPLOY_DIR" ]; then
        print_warning "部署目录已存在: $DEPLOY_DIR"
        read -p "是否覆盖现有配置？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "保留现有配置，跳过创建步骤"
            return
        fi
        print_warning "将覆盖现有配置文件..."
    fi

    mkdir -p "$DEPLOY_DIR"/{config,data/{uploads,logs,mysql}}
    print_success "部署目录创建完成: $DEPLOY_DIR"
}

# 生成配置文件
generate_configs() {
    print_info "生成配置文件..."

    cd "$DEPLOY_DIR"

    # 生成随机密码
    if [ -z "$MYSQL_PASSWORD" ]; then
        MYSQL_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-16)
        JWT_SECRET=$(openssl rand -hex 32)
    fi

    # 生成 .env 文件
    cat > .env << EOF
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
EOF

    # 生成 config.yaml
    cat > config/config.yaml << EOF
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
EOF

    # 生成 docker-compose.yml
    cat > docker-compose.yml << EOF
version: '3.8'

services:
  orderease-app:
    image: $IMAGE_NAME:$IMAGE_TAG
    container_name: orderease-app
    ports:
      - "\${APP_PORT:-8080}:8080"
    depends_on:
      mysql:
        condition: service_healthy
    environment:
      - DB_HOST=mysql
      - DB_PORT=3306
      - DB_USERNAME=root
      - DB_PASSWORD=\${MYSQL_ROOT_PASSWORD}
      - DB_NAME=orderease
      - JWT_SECRET=\${JWT_SECRET}
      - JWT_EXPIRATION=7200
      - TZ=\${TZ:-Asia/Shanghai}
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
      - MYSQL_ROOT_PASSWORD=\${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=orderease
      - TZ=\${TZ:-Asia/Shanghai}
    volumes:
      - ./data/mysql:/var/lib/mysql
    ports:
      - "\${MYSQL_PORT:-3306}:3306"
    networks:
      - orderease-network
    restart: unless-stopped
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p\${MYSQL_ROOT_PASSWORD}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

networks:
  orderease-network:
    driver: bridge
EOF

    print_success "配置文件生成完成"
}

# 拉取 Docker 镜像
pull_image() {
    print_info "拉取 Docker 镜像: $IMAGE_NAME:$IMAGE_TAG..."

    if docker images | grep -q "$IMAGE_NAME.*$IMAGE_TAG"; then
        print_warning "镜像已存在，跳过拉取"
        read -p "是否重新拉取最新镜像？(y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker pull "$IMAGE_NAME:$IMAGE_TAG"
        fi
    else
        docker pull "$IMAGE_NAME:$IMAGE_TAG"
    fi

    print_success "镜像准备完成"
}

# 启动服务
start_services() {
    print_info "启动 OrderEase 服务..."

    cd "$DEPLOY_DIR"

    # 创建数据目录（如果不存在）
    mkdir -p data/{uploads,logs,mysql}

    # 启动服务
    docker-compose up -d

    print_success "服务启动完成"
}

# 等待服务就绪
wait_for_ready() {
    print_info "等待服务启动..."

    local max_attempts=60
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if curl -sf http://localhost:8080/order-ease-iui/ > /dev/null 2>&1; then
            print_success "服务已就绪"
            return
        fi
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done

    echo
    print_warning "服务启动时间较长，请检查日志"
}

# 显示部署结果
show_result() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}        部署成功！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${BLUE}访问地址：${NC}"
    echo -e "  前台用户: ${YELLOW}http://localhost:8080/order-ease-iui/${NC}"
    echo -e "  后台管理: ${YELLOW}http://localhost:8080/order-ease-adminiui/${NC}"
    echo -e "  API 接口: ${YELLOW}http://localhost:8080/api/order-ease/v1/${NC}"
    echo ""
    echo -e "${BLUE}默认账户：${NC}"
    echo -e "  用户名: ${YELLOW}admin${NC}"
    echo -e "  密码:   ${YELLOW}Admin@123456${NC}"
    echo -e "${RED}⚠️  请登录后立即修改密码！${NC}"
    echo ""
    echo -e "${BLUE}常用命令：${NC}"
    echo -e "  查看日志: ${YELLOW}cd $DEPLOY_DIR && docker-compose logs -f${NC}"
    echo -e "  停止服务: ${YELLOW}cd $DEPLOY_DIR && docker-compose stop${NC}"
    echo -e "  重启服务: ${YELLOW}cd $DEPLOY_DIR && docker-compose restart${NC}"
    echo -e "  删除服务: ${YELLOW}cd $DEPLOY_DIR && docker-compose down${NC}"
    echo ""
    echo -e "${BLUE}配置文件位置：${NC}"
    echo -e "  $DEPLOY_DIR/docker-compose.yml"
    echo -e "  $DEPLOY_DIR/.env"
    echo -e "  $DEPLOY_DIR/config/config.yaml"
    echo ""
    echo -e "${BLUE}数据持久化目录：${NC}"
    echo -e "  $DEPLOY_DIR/data/uploads   # 上传文件"
    echo -e "  $DEPLOY_DIR/data/logs      # 应用日志"
    echo -e "  $DEPLOY_DIR/data/mysql    # 数据库数据"
    echo ""
}

# 主函数
main() {
    print_header

    # 检查环境
    check_docker
    check_ports

    # 创建配置
    create_deploy_dir
    generate_configs

    # 拉取镜像并启动
    pull_image
    start_services

    # 等待服务就绪
    wait_for_ready

    # 显示结果
    show_result
}

# 执行主函数
main "$@"
