#!/bin/bash

# OrderEase Docker 清理脚本
# 用法: ./cleanup.sh [-a|--all] [-f|--force] [-d|--dry-run]
# 功能: 清理旧的 Docker 镜像、容器、网络和卷

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# 日志函数
log_info() { echo -e "${CYAN}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_dryrun() { echo -e "${MAGENTA}[DRY-RUN]${NC} $1"; }

# 参数解析
REMOVE_ALL=false
FORCE=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--all)
            REMOVE_ALL=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            echo "OrderEase Docker 清理脚本"
            echo ""
            echo "用法: ./cleanup.sh [选项]"
            echo ""
            echo "选项:"
            echo "  -a, --all      清理所有未使用的资源（包括卷）"
            echo "  -f, --force    强制清理，不提示确认"
            echo "  -d, --dry-run  仅预览，不实际执行清理"
            echo "  -h, --help     显示帮助信息"
            echo ""
            echo "示例:"
            echo "  ./cleanup.sh              # 基础清理（推荐）"
            echo "  ./cleanup.sh -f           # 强制清理"
            echo "  ./cleanup.sh -d           # 预览模式"
            echo "  ./cleanup.sh -a           # 全面清理"
            exit 0
            ;;
        *)
            log_error "未知参数: $1"
            echo "使用 -h 或 --help 查看帮助"
            exit 1
            ;;
    esac
done

# 显示标题
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}    OrderEase Docker 清理脚本${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# 检查 Docker
log_info "检查 Docker 环境..."
if ! command -v docker &> /dev/null; then
    log_error "Docker 未安装"
    exit 1
fi

if ! docker info &> /dev/null; then
    log_error "Docker 未运行"
    exit 1
fi
log_success "Docker 环境正常"

# 获取当前资源使用情况
echo ""
log_info "当前 Docker 资源使用情况："
docker system df
echo ""

# 统计待清理资源
log_info "统计可清理资源..."

# 悬空镜像（无标签的镜像）
DANGLING_IMAGES=$(docker images -f "dangling=true" -q 2>/dev/null | wc -l)
DANGLING_COUNT=$(echo "$DANGLING_IMAGES" | tr -d ' ')

# 已停止的容器
STOPPED_CONTAINERS=$(docker ps -f "status=exited" -q 2>/dev/null | wc -l)
STOPPED_COUNT=$(echo "$STOPPED_CONTAINERS" | tr -d ' ')

# 未使用的网络
UNUSED_NETWORKS=$(docker network ls -f "dangling=true" -q 2>/dev/null | wc -l)
NETWORK_COUNT=$(echo "$UNUSED_NETWORKS" | tr -d ' ')

# 未使用的卷
UNUSED_VOLUMES=$(docker volume ls -f "dangling=true" -q 2>/dev/null | wc -l)
VOLUME_COUNT=$(echo "$UNUSED_VOLUMES" | tr -d ' ')

# 旧的 OrderEase 镜像（非 latest 版本）
OLD_ORDEREASE_IMAGES=$(docker images --format "{{.Repository}}:{{.Tag}}" | \
    grep "^siyuanh640/orderease:" | grep -v "siyuanh640/orderease:latest" || true)
OLD_IMAGE_COUNT=$(echo "$OLD_ORDEREASE_IMAGES" | grep -c "siyuanh640/orderease" || echo "0")

echo ""
echo -e "${CYAN}可清理资源统计：${NC}"
echo -e "  ${YELLOW}悬空镜像 (dangling): $DANGLING_COUNT${NC}"
echo -e "  ${YELLOW}已停止容器: $STOPPED_COUNT${NC}"
echo -e "  ${YELLOW}未使用网络: $NETWORK_COUNT${NC}"
echo -e "  ${YELLOW}未使用卷: $VOLUME_COUNT${NC}"
echo -e "  ${YELLOW}旧版 OrderEase 镜像: $OLD_IMAGE_COUNT${NC}"
echo ""

# 如果没有可清理的资源
TOTAL_COUNT=$((DANGLING_COUNT + STOPPED_COUNT + NETWORK_COUNT + VOLUME_COUNT + OLD_IMAGE_COUNT))
if [ "$TOTAL_COUNT" -eq 0 ]; then
    log_success "没有需要清理的资源"
    exit 0
fi

# 确认清理
if [ "$FORCE" = false ] && [ "$DRY_RUN" = false ]; then
    read -p "确认清理以上资源? (y/N) " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        log_info "已取消清理"
        exit 0
    fi
fi

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}开始清理...${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# 1. 清理已停止的容器
if [ "$STOPPED_COUNT" -gt 0 ]; then
    log_info "清理已停止的容器 ($STOPPED_COUNT)..."
    if [ "$DRY_RUN" = true ]; then
        log_dryrun "将执行: docker container prune -f"
    else
        docker container prune -f > /dev/null 2>&1
        log_success "已清理已停止的容器"
    fi
fi

# 2. 清理悬空镜像
if [ "$DANGLING_COUNT" -gt 0 ]; then
    log_info "清理悬空镜像 ($DANGLING_COUNT)..."
    if [ "$DRY_RUN" = true ]; then
        log_dryrun "将执行: docker image prune -f"
    else
        docker image prune -f > /dev/null 2>&1
        log_success "已清理悬空镜像"
    fi
fi

# 3. 清理旧版 OrderEase 镜像
if [ "$OLD_IMAGE_COUNT" -gt 0 ]; then
    log_info "清理旧版 OrderEase 镜像 ($OLD_IMAGE_COUNT)..."
    echo "$OLD_ORDEREASE_IMAGES" | while read -r image; do
        if [ -n "$image" ]; then
            if [ "$DRY_RUN" = true ]; then
                log_dryrun "将执行: docker rmi $image"
            else
                if docker rmi "$image" > /dev/null 2>&1; then
                    log_success "已删除镜像: $image"
                else
                    log_warning "无法删除镜像 $image (可能正在被使用)"
                fi
            fi
        fi
    done
fi

# 4. 清理未使用的网络
if [ "$NETWORK_COUNT" -gt 0 ]; then
    log_info "清理未使用的网络 ($NETWORK_COUNT)..."
    if [ "$DRY_RUN" = true ]; then
        log_dryrun "将执行: docker network prune -f"
    else
        docker network prune -f > /dev/null 2>&1
        log_success "已清理未使用的网络"
    fi
fi

# 5. 清理未使用的卷（仅在 --all 模式下）
if [ "$REMOVE_ALL" = true ] && [ "$VOLUME_COUNT" -gt 0 ]; then
    log_warning "警告: 将清理未使用的卷，卷中的数据将丢失！"
    if [ "$FORCE" = false ] && [ "$DRY_RUN" = false ]; then
        read -p "确认清理未使用的卷? (y/N) " confirm_volume
        if [ "$confirm_volume" != "y" ] && [ "$confirm_volume" != "Y" ]; then
            log_info "跳过卷的清理"
        else
            log_info "清理未使用的卷 ($VOLUME_COUNT)..."
            if [ "$DRY_RUN" = true ]; then
                log_dryrun "将执行: docker volume prune -f"
            else
                docker volume prune -f > /dev/null 2>&1
                log_success "已清理未使用的卷"
            fi
        fi
    else
        log_info "清理未使用的卷 ($VOLUME_COUNT)..."
        if [ "$DRY_RUN" = true ]; then
            log_dryrun "将执行: docker volume prune -f"
        else
            docker volume prune -f > /dev/null 2>&1
            log_success "已清理未使用的卷"
        fi
    fi
fi

# 6. 全面清理（仅在 --all 模式下）
if [ "$REMOVE_ALL" = true ]; then
    echo ""
    log_info "执行全面系统清理..."
    if [ "$DRY_RUN" = true ]; then
        log_dryrun "将执行: docker system prune -a -f --volumes"
    else
        docker system prune -a -f --volumes > /dev/null 2>&1
        log_success "系统全面清理完成"
    fi
fi

echo ""
echo -e "${GREEN}========================================${NC}"
if [ "$DRY_RUN" = true ]; then
    echo -e "${MAGENTA}    预览完成（未实际执行）${NC}"
else
    echo -e "${GREEN}    清理完成！${NC}"
fi
echo -e "${GREEN}========================================${NC}"
echo ""

# 显示清理后的资源使用情况
if [ "$DRY_RUN" = false ]; then
    log_info "清理后的 Docker 资源使用情况："
    docker system df
    echo ""
fi

# 提示常用命令
echo -e "${CYAN}常用清理命令参考：${NC}"
echo -e "  ${YELLOW}./cleanup.sh              # 基础清理（推荐）${NC}"
echo -e "  ${YELLOW}./cleanup.sh -f           # 强制清理，不提示确认${NC}"
echo -e "  ${YELLOW}./cleanup.sh -d           # 仅预览，不执行${NC}"
echo -e "  ${YELLOW}./cleanup.sh -a           # 全面清理（包括卷）${NC}"
echo ""
