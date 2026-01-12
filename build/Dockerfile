# OrderEase 合一版镜像构建文件
# 构建命令: docker build -t orderease:latest -f Dockerfile ../../

# 阶段1: 构建后台管理UI
FROM node:16-alpine AS backend-ui-build
WORKDIR /app/backend-ui
COPY OrderEase-BackedUI/package*.json ./
RUN npm install
COPY OrderEase-BackedUI/ .
# 覆盖 .env 文件，设置生产环境配置（前后端在同一服务器，使用相对路径）
RUN echo "VITE_API_BASE_URL=" > .env && \
    echo "VITE_API_PREFIX=/api/order-ease/v1" >> .env
RUN npm run build

# 阶段2: 构建前台UI
FROM node:18-alpine AS frontend-ui-build
WORKDIR /app/frontend-ui
COPY OrderEase-FrontUI/package*.json ./
RUN npm ci && npm cache clean --force
COPY OrderEase-FrontUI/ .
RUN npm run build

# 阶段3: 构建Go后端
FROM golang:1.22-alpine AS go-builder
WORKDIR /app/src
COPY OrderEase-Golang/src/ .
ENV GOPROXY=https://goproxy.cn,direct
RUN go mod tidy
RUN go test -v ./...  # 运行 Go 单元测试
RUN CGO_ENABLED=0 GOOS=linux go build -o ../orderease main.go

# 阶段4: 最终运行阶段
FROM alpine:latest

# 安装必要的运行时依赖
RUN apk add --no-cache ca-certificates tzdata wget

# 设置工作目录
WORKDIR /app

# 从Go构建阶段复制二进制文件和配置文件
COPY --from=go-builder /app/orderease .
COPY --from=go-builder /app/src/config/ ./config/

# 从UI构建阶段复制静态文件到static目录
COPY --from=backend-ui-build /app/backend-ui/dist ./static/order-ease-adminiui/
COPY --from=frontend-ui-build /app/frontend-ui/dist ./static/order-ease-iui/

# 创建必要的目录
RUN mkdir -p uploads/products logs

# 暴露端口 (Go服务提供所有内容)
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:8080/order-ease-iui/ || exit 1

# 启动Go服务
ENTRYPOINT ["./orderease"]
