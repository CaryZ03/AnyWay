# AnyWay 生产环境部署脚本 (PowerShell)
# 设置 UTF-8 编码以正确显示中文
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

Write-Host "=== AnyWay 生产环境部署 ===" -ForegroundColor Yellow

# 检查环境变量文件（优先使用 .env.prod，其次 .env）
$envFile = ".env"
if (Test-Path ".env.prod") {
    $envFile = ".env.prod"
    Write-Host "使用 .env.prod 文件" -ForegroundColor Green
} elseif (Test-Path ".env") {
    Write-Host "使用 .env 文件" -ForegroundColor Green
} else {
    Write-Host "警告: .env 或 .env.prod 文件不存在，将使用默认配置" -ForegroundColor Yellow
    Write-Host "建议: 创建 .env.prod 文件并配置 SECRET_KEY 等环境变量" -ForegroundColor Yellow
    $continue = Read-Host "是否继续？(y/n)"
    if ($continue -ne 'y' -and $continue -ne 'Y') {
        exit 1
    }
}

# 构建并启动服务（使用指定的环境变量文件）
Write-Host "正在构建并启动服务..." -ForegroundColor Cyan
if ($envFile -eq ".env.prod") {
    docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
} else {
    docker-compose -f docker-compose.prod.yml up -d --build
}

# 等待服务启动
Write-Host "等待服务启动..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# 检查服务状态
Write-Host "检查服务状态..." -ForegroundColor Cyan
docker-compose -f docker-compose.prod.yml ps

Write-Host ""
Write-Host "=== 部署完成 ===" -ForegroundColor Green
Write-Host "前端访问: http://localhost:18080" -ForegroundColor Cyan
Write-Host "后端 API: http://localhost:18080/api/v1/ (通过 Nginx 代理)" -ForegroundColor Cyan
Write-Host "管理后台: http://localhost:18080/admin/ (通过 Nginx 代理)" -ForegroundColor Cyan
Write-Host "API 文档: http://localhost:18080/swagger/ (通过 Nginx 代理)" -ForegroundColor Cyan
Write-Host ""
Write-Host "注意: 后端服务不直接暴露端口，所有请求通过前端 Nginx 代理" -ForegroundColor Yellow
Write-Host "注意: 如果 80 端口被占用，已自动使用 18080 端口" -ForegroundColor Yellow
Write-Host ""
Write-Host "查看日志: docker-compose -f docker-compose.prod.yml logs -f" -ForegroundColor Yellow
Write-Host "停止服务: docker-compose -f docker-compose.prod.yml down" -ForegroundColor Yellow

