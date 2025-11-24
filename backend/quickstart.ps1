# AI智能体创作平台 - 快速启动脚本 (Windows)
# 用于本地开发环境快速启动

Write-Host "🚀 AI智能体创作平台 - 快速启动" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# 检查Python版本
Write-Host "📌 检查Python版本..." -ForegroundColor Cyan
$pythonVersion = python --version
Write-Host "Python版本: $pythonVersion" -ForegroundColor Yellow

# 检查是否在虚拟环境中
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  建议使用虚拟环境" -ForegroundColor Yellow
    $createVenv = Read-Host "是否创建虚拟环境? (y/n)"
    if ($createVenv -eq "y" -or $createVenv -eq "Y") {
        Write-Host "📦 创建虚拟环境..." -ForegroundColor Cyan
        python -m venv venv
        .\venv\Scripts\Activate.ps1
        Write-Host "✅ 虚拟环境已激活" -ForegroundColor Green
    }
}

# 安装依赖
Write-Host "📦 安装Python依赖..." -ForegroundColor Cyan
pip install -r requirements.txt

# 检查环境变量文件
if (-not (Test-Path .env)) {
    Write-Host "📝 创建环境变量文件..." -ForegroundColor Cyan
    Copy-Item .env.example .env
    Write-Host "⚠️  请编辑 .env 文件配置数据库等信息" -ForegroundColor Yellow
    Read-Host "按回车键继续"
}

# 检查Docker服务
Write-Host "🐳 检查Docker服务..." -ForegroundColor Cyan
$dockerStatus = docker-compose ps 2>&1
if ($dockerStatus -notmatch "aiagent-mysql.*Up") {
    Write-Host "启动MySQL和Redis..." -ForegroundColor Cyan
    Set-Location ..
    docker-compose up -d
    Set-Location backend
    Write-Host "⏳ 等待数据库就绪..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}

# 数据库迁移
Write-Host "🗄️  执行数据库迁移..." -ForegroundColor Cyan
python manage.py makemigrations
python manage.py migrate

# 询问是否创建超级用户
$hasSuperuser = python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(is_superuser=True).exists())" 2>&1
if ($hasSuperuser -notmatch "True") {
    Write-Host "👤 创建超级用户..." -ForegroundColor Cyan
    python manage.py createsuperuser
}

# 收集静态文件
Write-Host "📁 收集静态文件..." -ForegroundColor Cyan
python manage.py collectstatic --noinput

Write-Host ""
Write-Host "✅ 启动完成！" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 启动开发服务器..." -ForegroundColor Cyan
Write-Host "   访问地址:" -ForegroundColor Yellow
Write-Host "   - API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "   - Swagger: http://localhost:8000/swagger/" -ForegroundColor Yellow
Write-Host "   - Admin: http://localhost:8000/admin/" -ForegroundColor Yellow
Write-Host ""
Write-Host "按 Ctrl+C 停止服务器" -ForegroundColor Yellow
Write-Host ""

# 启动开发服务器
python manage.py runserver
