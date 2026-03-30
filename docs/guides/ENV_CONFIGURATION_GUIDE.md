# OrderEase 环境变量配置指南

本文档详细说明 OrderEase 部署时所需的环境变量配置，包括本地部署、生产部署和 CI/CD 环境。

## 目录

- [环境变量概览](#环境变量概览)
- [本地部署环境变量配置](#本地部署环境变量配置)
- [CI/CD 环境变量配置](#ci-cd-环境变量配置)
- [生成安全密钥](#生成安全密钥)
- [常见问题排查](#常见问题排查)

---

## 环境变量概览

### 必需的环境变量

| 变量名 | 说明 | 示例值 | 是否必需 |
|--------|------|--------|----------|
| `DB_HOST` | 数据库主机地址 | `mysql` (Docker) / `localhost` | 是 |
| `DB_PORT` | 数据库端口 | `3306` | 是 |
| `DB_USERNAME` | 数据库用户名 | `root` | 是 |
| `DB_PASSWORD` | 数据库密码 | `RootPassword123!` | 是 |
| `DB_NAME` | 数据库名称 | `orderease` | 是 |
| `JWT_SECRET` | JWT 签名密钥（≥32字节） | `random_secret_key_32_bytes_minimum` | 是 |
| `JWT_EXPIRATION` | JWT 过期时间（秒） | `7200` (2小时) | 否 |
| `WECHAT_MINIPROGRAM_ENABLED` | 启用微信小程序登录 | `true` / `false` | 否 |
| `WECHAT_MINIPROGRAM_APP_ID` | 微信小程序 AppID | `wx1234567890abcdef` | 条件必需* |
| `WECHAT_MINIPROGRAM_APP_SECRET` | 微信小程序 AppSecret | `your_app_secret_here` | 条件必需* |
| `TZ` | 时区 | `Asia/Shanghai` | 否 |

> **条件必需***: 当 `WECHAT_MINIPROGRAM_ENABLED=true` 时必需
| `SERVER_HOST` | 服务器监听地址 | `0.0.0.0` | 否 |
| `SERVER_PORT` | 服务器端口 | `8080` | 否 |

### 环境变量说明

#### 数据库配置

```bash
DB_HOST=mysql          # Docker 内部网络使用服务名，本地部署使用 localhost
DB_PORT=3306           # MySQL 默认端口
DB_USERNAME=root       # 数据库用户名
DB_PASSWORD=<密码>     # 数据库密码（≥16位，包含大小写字母、数字和特殊字符）
DB_NAME=orderease      # 数据库名称
```

#### JWT 认证配置

```bash
JWT_SECRET=<密钥>      # JWT 签名密钥，≥32字节
JWT_EXPIRATION=7200    # Token 过期时间，单位：秒（默认7200秒=2小时）
```

#### 服务器配置

```bash
SERVER_HOST=0.0.0.0    # 监听所有网络接口
SERVER_PORT=8080       # 应用服务端口
TZ=Asia/Shanghai       # 时区配置
```

#### 微信小程序配置

```bash
WECHAT_MINIPROGRAM_ENABLED=true           # 是否启用微信小程序登录
WECHAT_MINIPROGRAM_APP_ID=wx1234567890    # 小程序 AppID（从微信公众平台获取）
WECHAT_MINIPROGRAM_APP_SECRET=xxx         # 小程序 AppSecret（从微信公众平台获取）
```

**获取方式：**
1. 登录 `https://mp.weixin.qq.com/`
2. 进入「开发」→「开发管理」→「开发设置」
3. 在「开发者ID」中查看 AppID 和 AppSecret

---

## 本地部署环境变量配置

### 方法一：使用 .env 文件（推荐）

1. **从模板创建 .env 文件**

```bash
# Linux/Mac
cd deploy
cp .env.template .env

# Windows PowerShell
cd deploy
Copy-Item .env.template .env
```

2. **编辑 .env 文件，填入实际值**

```bash
# 数据库配置
DB_HOST=mysql
DB_PORT=3306
DB_USERNAME=root
DB_PASSWORD=YourStrongPassword123!
DB_NAME=orderease

# JWT 认证配置
JWT_SECRET=your_jwt_secret_key_minimum_32_characters_long
JWT_EXPIRATION=7200

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8080

# 时区配置
TZ=Asia/Shanghai
```

3. **确认 .env 文件位置**

```
OrderEase-Deploy/
├── deploy/
│   ├── .env              # 环境变量文件（不要提交到 Git）
│   ├── .env.template     # 环境变量模板（可以提交）
│   ├── docker-compose.yml
│   └── config/
```

### 方法二：在 docker-compose.yml 中直接配置

如果不想使用 .env 文件，可以在 `docker-compose.yml` 中直接配置：

```yaml
services:
  orderease-app:
    environment:
      - DB_HOST=mysql
      - DB_PORT=3306
      - DB_USERNAME=root
      - DB_PASSWORD=YourStrongPassword123!
      - DB_NAME=orderease
      - JWT_SECRET=your_jwt_secret_key_minimum_32_characters_long
      - JWT_EXPIRATION=7200
      - TZ=Asia/Shanghai
```

⚠️ **警告**：直接在 docker-compose.yml 中配置敏感信息存在安全风险，建议仅在本地测试环境使用。

### 测试环境配置示例

```bash
# deploy/.env（测试环境）
DB_HOST=mysql
DB_PORT=3306
DB_USERNAME=root
DB_PASSWORD=RootPassword123!
DB_NAME=orderease
JWT_SECRET=test_jwt_secret_for_local_testing_minimum_32_bytes
JWT_EXPIRATION=7200
TZ=Asia/Shanghai
```

### 生产环境配置示例

```bash
# deploy/.env（生产环境）
DB_HOST=mysql
DB_PORT=3306
DB_USERNAME=root
DB_PASSWORD=P@ssw0rd!Secure#2026$Strong
DB_NAME=orderease
JWT_SECRET=$(openssl rand -base64 32)  # 生成随机密钥
JWT_EXPIRATION=7200
TZ=Asia/Shanghai
```

---

## CI/CD 环境变量配置

### GitHub Actions 配置

OrderEase 使用 GitHub Actions 进行 CI/CD，需要在 GitHub 仓库中配置 Secrets。

#### 配置步骤

1. **进入 GitHub 仓库设置**

   ```
   仓库页面 → Settings → Secrets and variables → Actions
   ```

2. **添加必需的 Secrets**

   点击 "New repository secret"，添加以下 Secret：

   | Secret 名称 | 说明 | 示例值 |
   |-------------|------|--------|
   | `JWT_SECRET` | JWT 签名密钥 | 使用 openssl 生成（见下方） |
   | `DOCKER_USERNAME` | Docker Hub 用户名 | `your-docker-username` |
   | `DOCKER_PASSWORD` | Docker Hub 密码/Token | `dckr_pat_xxxxx` |

3. **JWT_SECRET 生成方法**

   ```bash
   # 方法一：使用 OpenSSL（推荐）
   openssl rand -base64 32

   # 方法二：使用 OpenSSL 生成十六进制
   openssl rand -hex 32

   # 方法三：使用 Python
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"

   # 方法四：在线生成器
   # https://generate-random.org/api-key-generator
   ```

4. **验证配置**

   在 `.github/workflows/build-test-deploy.yml` 中，环境变量已正确配置：

   ```yaml
   integration-test:
     env:
       MYSQL_ROOT_PASSWORD: RootPassword123!
       JWT_SECRET: ${{ secrets.JWT_SECRET }}
   ```

#### CI/CD 环境变量流程

```
GitHub Secrets (JWT_SECRET)
        ↓
GitHub Actions Workflow
        ↓
Docker Container Environment (-e JWT_SECRET)
        ↓
OrderEase Application (reads JWT_SECRET)
```

#### 常见 CI/CD 错误

**错误 1: JWT_SECRET 未配置**
```
Error: Container fails to start with JWT validation error
```
**解决方案**: 在 GitHub Secrets 中添加 `JWT_SECRET`

**错误 2: 数据库连接失败**
```
Error 1045 (28000): Access denied for user 'root'
```
**解决方案**: 检查容器环境变量是否正确传递

---

## 生成安全密钥

### 数据库密码生成

```bash
# 生成 16 位随机密码
openssl rand -base64 12

# 生成 20 位随机密码（包含特殊字符）
openssl rand -base64 16 | tr -d "=+/" | cut -c1-20

# 使用 Python 生成
python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*') for _ in range(20)))"
```

### JWT 密钥生成

```bash
# 推荐：生成 32 字节以上的 Base64 编码密钥
openssl rand -base64 32

# 或生成 64 位十六进制密钥
openssl rand -hex 32

# 或生成 43 个 URL 安全字符（推荐用于 JWT）
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 密钥安全要求

| 用途 | 最小长度 | 字符要求 | 推荐长度 |
|------|----------|----------|----------|
| 数据库密码 | 16 位 | 大小写字母+数字+特殊字符 | 20+ 位 |
| JWT_SECRET | 32 字节 | 随机字节（Base64 编码后约 43 字符） | 32+ 字节 |

---

## 常见问题排查

### 问题 1: 容器启动失败 - 数据库密码错误

**错误信息**:
```
Error 1045 (28000): Access denied for user 'root'@'172.18.0.3' (using password: YES)
```

**排查步骤**:

1. **检查 .env 文件是否存在**
   ```bash
   ls deploy/.env
   ```

2. **检查环境变量是否正确传递**
   ```bash
   docker inspect orderease-app | grep -A 20 "Env"
   ```

3. **检查 MySQL 容器的环境变量**
   ```bash
   docker inspect orderease-mysql | grep MYSQL_ROOT_PASSWORD
   ```

4. **确保密码一致**
   - MySQL 容器: `MYSQL_ROOT_PASSWORD`
   - 应用容器: `DB_PASSWORD`
   - 这两个值必须相同

**解决方案**:

```bash
# 停止服务
docker-compose down

# 清理 MySQL 数据（重新初始化）
rm -rf deploy/data/mysql

# 检查并修正 .env 文件
cat deploy/.env | grep DB_PASSWORD
cat deploy/.env | grep MYSQL_ROOT_PASSWORD  # 如果存在

# 重新启动
docker-compose up -d
```

### 问题 2: JWT 认证失败

**错误信息**:
```
Error: token validation failed
```

**排查步骤**:

1. **检查 JWT_SECRET 是否设置**
   ```bash
   docker exec orderease-app printenv | grep JWT_SECRET
   ```

2. **检查 JWT_SECRET 长度**
   - 必须至少 32 字节
   - 确保没有多余的空格或换行符

**解决方案**:

```bash
# 重新生成 JWT_SECRET
JWT_SECRET=$(openssl rand -base64 32)

# 更新 .env 文件
sed -i "s/JWT_SECRET=.*/JWT_SECRET=$JWT_SECRET/" deploy/.env

# 重启容器
docker-compose restart orderease-app
```

### 问题 3: .env 文件被 Git 追踪

**问题**: .env 文件包含敏感信息，不应提交到版本控制。

**解决方案**:

```bash
# 1. 从 Git 中移除 .env 文件
git rm --cached deploy/.env

# 2. 更新 .gitignore
echo "deploy/.env" >> .gitignore

# 3. 提交更改
git add .gitignore
git commit -m "chore: exclude .env file from version control"
```

### 问题 4: GitHub Actions 失败 - JWT_SECRET 未设置

**错误信息**:
```
Error: JWT_SECRET is not set in container environment
```

**解决方案**:

1. 进入 GitHub 仓库：`Settings → Secrets and variables → Actions`
2. 点击 "New repository secret"
3. Name: `JWT_SECRET`
4. Value: `<生成的32字节以上密钥>`
5. 点击 "Add secret"
6. 重新运行 GitHub Actions workflow

---

## 安全最佳实践

### 1. 密钥管理原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **最小权限** | 只授予必要的权限 | 数据库用户只访问必要的数据库 |
| **密钥轮换** | 定期更换密钥 | 每 3-6 个月更换一次 |
| **密钥分离** | 不同环境使用不同密钥 | 开发/测试/生产使用不同的 JWT_SECRET |
| **密钥存储** | 使用安全的密钥管理服务 | AWS Secrets Manager、HashiCorp Vault |

### 2. 环境隔离

```bash
# 开发环境
DB_PASSWORD=dev_password_123
JWT_SECRET=dev_jwt_secret_for_development_only

# 测试环境
DB_PASSWORD=test_password_456
JWT_SECRET=test_jwt_secret_for_testing_only

# 生产环境
DB_PASSWORD=prod_secure_password_789!@#
JWT_SECRET=$(openssl rand -base64 32)  # 每次部署生成新密钥
```

### 3. 密钥检查清单

- [ ] .env 文件已添加到 .gitignore
- [ ] 不同环境使用不同的密钥
- [ ] 密钥长度符合安全要求（数据库≥16位，JWT≥32字节）
- [ ] GitHub Secrets 已配置必需的密钥
- [ ] 密钥不包含在日志或错误信息中
- [ ] 定期轮换密钥（建议每 3-6 个月）

---

## 附录：完整配置示例

### 开发环境 (.env.development)

```bash
# 开发环境配置
DB_HOST=localhost
DB_PORT=3306
DB_USERNAME=root
DB_PASSWORD=dev_password_123
DB_NAME=orderease_dev
JWT_SECRET=dev_jwt_secret_for_development_only_minimum_32_bytes
JWT_EXPIRATION=7200
TZ=Asia/Shanghai
```

### 测试环境 (.env.test)

```bash
# 测试环境配置（CI/CD）
DB_HOST=mysql
DB_PORT=3306
DB_USERNAME=root
DB_PASSWORD=RootPassword123!
DB_NAME=orderease
JWT_SECRET=test_jwt_secret_for_ci_cd_minimum_32_bytes
JWT_EXPIRATION=7200
TZ=Asia/Shanghai
```

### 生产环境 (.env.production)

```bash
# 生产环境配置
DB_HOST=mysql.internal
DB_PORT=3306
DB_USERNAME=orderease_user
DB_PASSWORD=P@ssw0rd!Secure#2026$Strong$Random
DB_NAME=orderease_prod
JWT_SECRET=$(openssl rand -base64 32)  # 每次部署生成新密钥
JWT_EXPIRATION=7200
TZ=Asia/Shanghai
```

---

**文档版本**: 1.0
**更新日期**: 2026-02-03
**适用版本**: OrderEase v1.0+
