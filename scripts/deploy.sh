#!/bin/bash
#
# OrderEase 自动部署脚本
# 用途：从 Docker Hub 拉取镜像并启动服务
# 使用方法：chmod +x deploy.sh && ./deploy.sh
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

IMAGE_NAME="siyuanh640/orderease"
IMAGE_TAG="latest"
DEPLOY_DIR="$(pwd)/orderease-deploy"
MYSQL_PASSWORD=""
JWT_SECRET=""

RETRY_COUNT=5
RETRY_DELAY=10
PULL_TIMEOUT=600

MIRROR_LIST=(
    "docker.1panel.live"
    "docker.1ms.run"
    "docker.xuanyuan.me"
    "docker.m.daocloud.io"
    "dockerproxy.net"
    "hub.rat.dev"
    "dytt.online"
    "docker.mirrors.sjtug.sjtu.edu.cn"
    "hub.nat.tf"
    "hub1.nat.tf"
    "hub2.nat.tf"
)

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

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}    OrderEase 本地部署脚本${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

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

check_ports() {
    print_info "检查端口占用..."

    if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -an 2>/dev/null | grep ":8080.*LISTEN" >/dev/null; then
        print_warning "端口 8080 已被占用"
        read -p "是否继续部署？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "部署已取消"
            exit 0
        fi
    fi

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

generate_configs() {
    print_info "生成配置文件..."

    cd "$DEPLOY_DIR"

    if [ -z "$MYSQL_PASSWORD" ]; then
        MYSQL_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-16)
        JWT_SECRET=$(openssl rand -hex 32)
    fi

    cat > .env << EOF
MYSQL_ROOT_PASSWORD=$MYSQL_PASSWORD
MYSQL_DATABASE=orderease
JWT_SECRET=$JWT_SECRET
JWT_EXPIRATION=7200
TZ=Asia/Shanghai
APP_PORT=8080
MYSQL_PORT=3306
EOF

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

try_pull_with_retry() {
    local image="$1"
    local attempt=1

    while [ $attempt -le $RETRY_COUNT ]; do
        print_info "拉取尝试 $attempt/$RETRY_COUNT: $image"
        
        local pull_result=0
        if command -v timeout &> /dev/null; then
            timeout $PULL_TIMEOUT docker pull "$image" 2>&1 || pull_result=$?
        else
            docker pull "$image" 2>&1 || pull_result=$?
        fi
        
        if [ $pull_result -eq 0 ]; then
            return 0
        fi
        
        if [ $attempt -lt $RETRY_COUNT ]; then
            print_warning "拉取失败，${RETRY_DELAY}秒后重试..."
            sleep $RETRY_DELAY
        fi
        attempt=$((attempt + 1))
    done

    return 1
}

pull_from_registry() {
    print_info "方式 1: 从镜像源拉取..."
    
    for mirror in "${MIRROR_LIST[@]}"; do
        print_info "尝试镜像源: $mirror"
        local mirror_image="$mirror/$IMAGE_NAME:$IMAGE_TAG"
        if try_pull_with_retry "$mirror_image"; then
            print_info "打标签为 $IMAGE_NAME:$IMAGE_TAG"
            docker tag "$mirror_image" "$IMAGE_NAME:$IMAGE_TAG" 2>/dev/null || true
            return 0
        fi
    done
    
    print_warning "镜像源拉取失败，尝试 Docker Hub 官方源..."
    if try_pull_with_retry "$IMAGE_NAME:$IMAGE_TAG"; then
        return 0
    fi
    
    return 1
}

load_from_tar() {
    print_info "方式 2: 从本地 tar 文件导入镜像..."
    
    local tar_files=$(find . -maxdepth 1 -name "orderease*.tar" -type f 2>/dev/null)
    
    if [ -n "$tar_files" ]; then
        echo "发现以下 tar 文件:"
        echo "$tar_files"
        read -p "是否使用这些文件？(y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            for tar_file in $tar_files; do
                print_info "导入: $tar_file"
                if docker load -i "$tar_file"; then
                    print_success "镜像导入成功"
                    return 0
                fi
            done
        fi
    fi
    
    read -p "请输入 tar 文件路径（留空跳过）: " tar_path
    if [ -n "$tar_path" ] && [ -f "$tar_path" ]; then
        print_info "导入: $tar_path"
        if docker load -i "$tar_path"; then
            print_success "镜像导入成功"
            return 0
        fi
    fi
    
    return 1
}

download_from_url() {
    print_info "方式 3: 从 URL 下载镜像 tar 文件..."
    
    read -p "请输入镜像 tar 文件下载地址（留空跳过）: " download_url
    
    if [ -n "$download_url" ]; then
        local tar_file="/tmp/orderease-$(date +%Y%m%d%H%M%S).tar"
        print_info "下载中..."
        
        if wget -c -O "$tar_file" "$download_url" 2>&1 || curl -L -o "$tar_file" "$download_url" 2>&1; then
            print_info "导入镜像..."
            if docker load -i "$tar_file"; then
                rm -f "$tar_file"
                print_success "镜像下载并导入成功"
                return 0
            fi
            rm -f "$tar_file"
        fi
    fi
    
    return 1
}

pull_image() {
    print_info "检查镜像: $IMAGE_NAME:$IMAGE_TAG..."

    if docker images | grep -q "$IMAGE_NAME.*$IMAGE_TAG"; then
        print_warning "镜像已存在"
        read -p "是否重新获取镜像？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_success "使用现有镜像"
            return
        fi
    fi

    echo ""
    echo -e "${YELLOW}请选择镜像获取方式：${NC}"
    echo "  1) 从 Docker Hub 拉取（需要网络通畅）"
    echo "  2) 从本地 tar 文件导入"
    echo "  3) 从 URL 下载 tar 文件"
    echo "  4) 跳过（手动处理）"
    echo ""
    read -p "请选择 [1-4]: " choice

    case $choice in
        1)
            if pull_from_registry; then
                print_success "镜像准备完成"
                return
            fi
            print_error "Docker Hub 拉取失败"
            ;;
        2)
            if load_from_tar; then
                print_success "镜像准备完成"
                return
            fi
            print_error "tar 文件导入失败"
            ;;
        3)
            if download_from_url; then
                print_success "镜像准备完成"
                return
            fi
            print_error "URL 下载失败"
            ;;
        4)
            print_warning "已跳过镜像获取"
            print_info "请手动拉取镜像后运行: ./deploy.sh --skip-pull"
            exit 0
            ;;
        *)
            print_error "无效选择"
            exit 1
            ;;
    esac

    print_error "镜像获取失败"
    print_info ""
    print_info "手动获取镜像的方法："
    print_info "  1. 在网络通畅的机器上执行:"
    print_info "     docker pull $IMAGE_NAME:$IMAGE_TAG"
    print_info "     docker save $IMAGE_NAME:$IMAGE_TAG -o orderease.tar"
    print_info "  2. 将 orderease.tar 上传到服务器"
    print_info "  3. 执行: docker load -i orderease.tar"
    print_info "  4. 重新运行: ./deploy.sh --skip-pull"
    exit 1
}

start_services() {
    print_info "启动 OrderEase 服务..."

    cd "$DEPLOY_DIR"

    mkdir -p data/{uploads,logs,mysql}

    docker-compose up -d

    print_success "服务启动完成"
}

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

main() {
    print_header

    check_docker
    check_ports

    create_deploy_dir
    generate_configs

    if [[ "$1" != "--skip-pull" ]]; then
        pull_image
    else
        print_info "跳过镜像拉取"
    fi

    start_services
    wait_for_ready
    show_result
}

main "$@"
