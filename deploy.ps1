# AI智能体创作平台 - Windows部署脚本
# PowerShell脚本

Write-Host "🚀 开始部署AI智能体创作平台..." -ForegroundColor Green

# 检查环境变量文件
if (-not (Test-Path .env.prod)) {
    Write-Host "⚠️  未找到 .env.prod 文件" -ForegroundColor Yellow
    Write-Host "请复制 .env.prod.example 为 .env.prod 并填写配置"
    exit 1
}

# 1. 拉取最新代码
Write-Host "📥 拉取最新代码..." -ForegroundColor Green
try {
    git pull origin main
} catch {
    Write-Host "跳过git pull（可能不在git仓库中）" -ForegroundColor Yellow
}

# 2. 构建Docker镜像
Write-Host "🔨 构建Docker镜像..." -ForegroundColor Green
docker-compose -f docker-compose.prod.yml build

# 3. 停止旧容器
Write-Host "🛑 停止旧容器..." -ForegroundColor Green
docker-compose -f docker-compose.prod.yml down

# 4. 启动新容器
Write-Host "▶️  启动新容器..." -ForegroundColor Green
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# 5. 等待服务就绪
Write-Host "⏳ 等待服务就绪..." -ForegroundColor Green
Start-Sleep -Seconds 15

# 6. 检查服务状态
Write-Host "✅ 检查服务状态..." -ForegroundColor Green
docker-compose -f docker-compose.prod.yml ps

# 7. 显示日志
Write-Host "📋 最近的日志:" -ForegroundColor Green
docker-compose -f docker-compose.prod.yml logs --tail=50

Write-Host ""
Write-Host "🎉 部署完成！" -ForegroundColor Green
Write-Host ""
Write-Host "服务地址:"
Write-Host "  - 前端: http://localhost"
Write-Host "  - 后端API: http://localhost:8000"
Write-Host "  - API文档: http://localhost:8000/swagger/"
Write-Host ""
Write-Host "查看日志: docker-compose -f docker-compose.prod.yml logs -f"
Write-Host "停止服务: docker-compose -f docker-compose.prod.yml down"
