#!/bin/bash
# OrderEase 镜像构建脚本

set -e

echo "========================================="
echo "开始构建 OrderEase 镜像"
echo "========================================="

# 获取当前时间作为构建标签
BUILD_DATE=$(date +%Y%m%d%H%M%S)
VERSION=${1:-latest}

echo "构建版本: $VERSION"
echo "构建时间: $BUILD_DATE"

# 构建镜像
docker-compose build

# 打标签
if [ "$VERSION" != "latest" ]; then
    echo "添加版本标签: orderease:$VERSION"
    docker tag orderease:latest orderease:$VERSION
fi

echo "========================================="
echo "镜像构建完成！"
echo "========================================="
echo "镜像列表:"
docker images | grep orderease

echo ""
echo "可用命令："
echo "  - 查看镜像: docker images orderease"
echo "  - 导出镜像: docker save orderease:latest -o orderease-$BUILD_DATE.tar"
echo "  - 推送镜像: docker push orderease:latest"
