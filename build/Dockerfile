# OrderEase 合一版镜像构建文件 - 极致优化版
# 构建命令: docker build -t orderease:latest -f Dockerfile ../../

# 阶段1: 构建后台管理UI
FROM node:20-alpine AS backend-ui-build
WORKDIR /app/backend-ui
COPY OrderEase-BackedUI/package*.json ./
RUN npm ci --production=false && npm cache clean --force
COPY OrderEase-BackedUI/ .
# 覆盖 .env 文件，设置生产环境配置（前后端在同一服务器，使用相对路径）
RUN echo "VITE_API_BASE_URL=" > .env && \
    echo "VITE_API_PREFIX=/api/order-ease/v1" >> .env
RUN npm run build
RUN echo "=== Debug: Checking backend dist directory ===" && \
    ls -la dist/ && \
    if [ ! -f dist/index.html ]; then \
        echo "ERROR: backend dist/index.html not found! Build may have failed."; \
        exit 1; \
    fi

# 阶段2: 构建前台UI (uni-app项目)
FROM node:20-alpine AS frontend-ui-build
WORKDIR /app/frontend-ui
COPY OrderEase-FrontUI/package*.json ./
COPY OrderEase-FrontUI/scripts ./scripts
RUN echo "=== Debug: Listing files after COPY scripts ===" && \
    ls -la && \
    ls -la scripts/ || echo "scripts directory not found"
RUN npm ci --production=false && npm cache clean --force
COPY OrderEase-FrontUI/ ./
RUN npm run build:h5
# uni-app H5构建输出到 dist/build/h5/ 目录
RUN echo "=== Debug: Checking dist directory structure ===" && \
    ls -la dist/ && \
    ls -la dist/build/ && \
    ls -la dist/build/h5/ && \
    if [ ! -f dist/build/h5/index.html ]; then \
        echo "ERROR: dist/build/h5/index.html not found! Build may have failed."; \
        exit 1; \
    fi

# 阶段3: 构建Go后端 - 极致优化
FROM golang:1.24-alpine AS go-builder
WORKDIR /app/src
COPY OrderEase-Golang/src/ .
ENV GOPROXY=https://goproxy.cn,direct
ENV CGO_ENABLED=0
ENV GOOS=linux
ENV GOARCH=amd64

# 安装 UPX 压缩工具
RUN apk add --no-cache upx

RUN go mod tidy
# 测试由 CI/CD 处理，构建时跳过以加速
# RUN go test -v ./...

# 极致构建参数
# -ldflags:
#   -s: 去除符号表
#   -w: 去除 DWARF 调试信息
#   -buildid=: 清除构建 ID
# -trimpath: 去除文件路径信息
RUN go build \
    -ldflags="-s -w -buildid=" \
    -trimpath \
    -o ../orderease main.go && \
    upx --best --lzma /app/orderease

# 阶段4: 最终运行阶段 - 固定版本 Alpine
FROM alpine:3.19

# 仅安装最小运行时依赖
RUN apk add --no-cache ca-certificates tzdata

# 设置时区
ENV TZ=Asia/Shanghai

# 创建非 root 用户
RUN addgroup -g 1000 orderease && \
    adduser -D -u 1000 -G orderease orderease

# 设置工作目录
WORKDIR /app

# 从Go构建阶段复制二进制文件和配置
COPY --from=go-builder --chown=orderease:orderease /app/orderease .
COPY --from=go-builder --chown=orderease:orderease /app/src/config/ ./config/

# 从UI构建阶段复制静态文件
COPY --from=backend-ui-build --chown=orderease:orderease /app/backend-ui/dist ./static/order-ease-adminiui/
# uni-app H5构建输出在 dist/build/h5/ 目录
COPY --from=frontend-ui-build --chown=orderease:orderease /app/frontend-ui/dist/build/h5 ./static/order-ease-iui/

# 创建必要的目录并设置权限（在切换用户前以root身份执行）
RUN mkdir -p uploads/products uploads/shops logs && \
    chmod -R 750 uploads && \
    chown -R orderease:orderease /app/uploads /app/logs

# 切换到非 root 用户
USER orderease

# 暴露端口
EXPOSE 8080

# 健康检查 (使用 wget 替代 curl)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:8080/order-ease-iui/ || exit 1

# 启动Go服务
ENTRYPOINT ["./orderease"]
