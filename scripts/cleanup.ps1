# OrderEase Docker 清理脚本
# 用法: .\cleanup.ps1 [-RemoveAll] [-Force]
# 功能: 清理旧的 Docker 镜像、容器、网络和卷

param(
    [switch]$RemoveAll,    # 清理所有未使用的资源（包括卷）
    [switch]$Force,        # 强制清理，不提示确认
    [switch]$DryRun        # 仅预览，不实际执行清理
)

# 颜色输出
function Write-Info { Write-Host "[INFO] $args" -ForegroundColor Cyan }
function Write-Success { Write-Host "[SUCCESS] $args" -ForegroundColor Green }
function Write-Warning { Write-Host "[WARNING] $args" -ForegroundColor Yellow }
function Write-Error { Write-Host "[ERROR] $args" -ForegroundColor Red }
function Write-DryRun { Write-Host "[DRY-RUN] $args" -ForegroundColor Magenta }

# 显示标题
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    OrderEase Docker 清理脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker
Write-Info "检查 Docker 环境..."
try {
    $null = docker --version 2>&1
    $null = docker info 2>&1
} catch {
    Write-Error "Docker 未运行或未安装"
    exit 1
}
Write-Success "Docker 环境正常"

# 获取当前资源使用情况
Write-Host ""
Write-Info "当前 Docker 资源使用情况："
docker system df
Write-Host ""

# 统计待清理资源
Write-Info "统计可清理资源..."

# 悬空镜像（无标签的镜像）
$danglingImages = docker images -f "dangling=true" -q 2>$null
$danglingCount = if ($danglingImages) { ($danglingImages -split "`n").Count } else { 0 }

# 已停止的容器
$stoppedContainers = docker ps -f "status=exited" -q 2>$null
$stoppedCount = if ($stoppedContainers) { ($stoppedContainers -split "`n").Count } else { 0 }

# 未使用的网络
$unusedNetworks = docker network ls -f "dangling=true" -q 2>$null
$networkCount = if ($unusedNetworks) { ($unusedNetworks -split "`n").Count } else { 0 }

# 未使用的卷
$unusedVolumes = docker volume ls -f "dangling=true" -q 2>$null
$volumeCount = if ($unusedVolumes) { ($unusedVolumes -split "`n").Count } else { 0 }

# 旧的 OrderEase 镜像（非 latest 版本）
$oldOrderEaseImages = docker images --format "{{.Repository}}:{{.Tag}}" | 
    Where-Object { $_ -like "siyuanh640/orderease:*" -and $_ -ne "siyuanh640/orderease:latest" }
$oldImageCount = if ($oldOrderEaseImages) { $oldOrderEaseImages.Count } else { 0 }

Write-Host ""
Write-Host "可清理资源统计：" -ForegroundColor Cyan
Write-Host "  悬空镜像 (dangling): $danglingCount" -ForegroundColor Yellow
Write-Host "  已停止容器: $stoppedCount" -ForegroundColor Yellow
Write-Host "  未使用网络: $networkCount" -ForegroundColor Yellow
Write-Host "  未使用卷: $volumeCount" -ForegroundColor Yellow
Write-Host "  旧版 OrderEase 镜像: $oldImageCount" -ForegroundColor Yellow
Write-Host ""

# 如果没有可清理的资源
if (($danglingCount + $stoppedCount + $networkCount + $volumeCount + $oldImageCount) -eq 0) {
    Write-Success "没有需要清理的资源"
    exit 0
}

# 确认清理
if (-not $Force -and -not $DryRun) {
    $confirm = Read-Host "确认清理以上资源? (y/N)"
    if ($confirm -ne "y") {
        Write-Info "已取消清理"
        exit 0
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "开始清理..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 清理已停止的容器
if ($stoppedCount -gt 0) {
    Write-Info "清理已停止的容器 ($stoppedCount)..."
    if ($DryRun) {
        Write-DryRun "将执行: docker container prune -f"
    } else {
        docker container prune -f | Out-Null
        Write-Success "已清理已停止的容器"
    }
}

# 2. 清理悬空镜像
if ($danglingCount -gt 0) {
    Write-Info "清理悬空镜像 ($danglingCount)..."
    if ($DryRun) {
        Write-DryRun "将执行: docker image prune -f"
    } else {
        docker image prune -f | Out-Null
        Write-Success "已清理悬空镜像"
    }
}

# 3. 清理旧版 OrderEase 镜像
if ($oldImageCount -gt 0) {
    Write-Info "清理旧版 OrderEase 镜像 ($oldImageCount)..."
    foreach ($image in $oldOrderEaseImages) {
        if ($DryRun) {
            Write-DryRun "将执行: docker rmi $image"
        } else {
            try {
                docker rmi $image 2>$null
                Write-Success "已删除镜像: $image"
            } catch {
                Write-Warning "无法删除镜像 $image (可能正在被使用)"
            }
        }
    }
}

# 4. 清理未使用的网络
if ($networkCount -gt 0) {
    Write-Info "清理未使用的网络 ($networkCount)..."
    if ($DryRun) {
        Write-DryRun "将执行: docker network prune -f"
    } else {
        docker network prune -f | Out-Null
        Write-Success "已清理未使用的网络"
    }
}

# 5. 清理未使用的卷（仅在 -RemoveAll 模式下）
if ($RemoveAll -and $volumeCount -gt 0) {
    Write-Warning "警告: 将清理未使用的卷，卷中的数据将丢失！"
    if (-not $Force -and -not $DryRun) {
        $confirmVolume = Read-Host "确认清理未使用的卷? (y/N)"
        if ($confirmVolume -ne "y") {
            Write-Info "跳过卷的清理"
        } else {
            Write-Info "清理未使用的卷 ($volumeCount)..."
            if ($DryRun) {
                Write-DryRun "将执行: docker volume prune -f"
            } else {
                docker volume prune -f | Out-Null
                Write-Success "已清理未使用的卷"
            }
        }
    } else {
        Write-Info "清理未使用的卷 ($volumeCount)..."
        if ($DryRun) {
            Write-DryRun "将执行: docker volume prune -f"
        } else {
            docker volume prune -f | Out-Null
            Write-Success "已清理未使用的卷"
        }
    }
}

# 6. 全面清理（仅在 -RemoveAll 模式下）
if ($RemoveAll) {
    Write-Host ""
    Write-Info "执行全面系统清理..."
    if ($DryRun) {
        Write-DryRun "将执行: docker system prune -a -f --volumes"
    } else {
        docker system prune -a -f --volumes | Out-Null
        Write-Success "系统全面清理完成"
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
if ($DryRun) {
    Write-Host "    预览完成（未实际执行）" -ForegroundColor Magenta
} else {
    Write-Host "    清理完成！" -ForegroundColor Green
}
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 显示清理后的资源使用情况
if (-not $DryRun) {
    Write-Info "清理后的 Docker 资源使用情况："
    docker system df
    Write-Host ""
}

# 提示常用命令
Write-Host "常用清理命令参考：" -ForegroundColor Cyan
Write-Host "  .\cleanup.ps1              # 基础清理（推荐）" -ForegroundColor Yellow
Write-Host "  .\cleanup.ps1 -Force       # 强制清理，不提示确认" -ForegroundColor Yellow
Write-Host "  .\cleanup.ps1 -DryRun      # 仅预览，不执行" -ForegroundColor Yellow
Write-Host "  .\cleanup.ps1 -RemoveAll   # 全面清理（包括卷）" -ForegroundColor Yellow
Write-Host ""
