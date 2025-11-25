# AnyWay 后端本地启动脚本 (Windows)
# 用法: cd backend; ./start.ps1 或 powershell -ExecutionPolicy Bypass -File .\start.ps1

# 切到脚本所在目录
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $SCRIPT_DIR

Write-Host "=== 启动 Docker 服务 (MySQL + Redis) ===" -ForegroundColor Yellow
$projectRoot = Resolve-Path "$SCRIPT_DIR\.."
Push-Location $projectRoot
docker-compose up -d
Pop-Location

Write-Host "=== 安装 Python 依赖 ===" -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "=== 数据库迁移 ===" -ForegroundColor Yellow
python manage.py makemigrations agent workflow knowledge plugin llm
python manage.py migrate

Write-Host "=== 启动 Django 开发服务器 ===" -ForegroundColor Yellow
Write-Host "访问地址: http://localhost:8000" -ForegroundColor Cyan
Write-Host "按 Ctrl + C 停止服务" -ForegroundColor Cyan
python manage.py runserver
