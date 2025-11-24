#!/bin/bash

# AI智能体创作平台 - 快速启动脚本
# 用于本地开发环境快速启动

set -e

echo "🚀 AI智能体创作平台 - 快速启动"
echo "================================"

# 检查Python版本
echo "📌 检查Python版本..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python版本: $python_version"

# 检查是否在虚拟环境中
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  建议使用虚拟环境"
    read -p "是否创建虚拟环境? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 创建虚拟环境..."
        python -m venv venv
        source venv/bin/activate
        echo "✅ 虚拟环境已激活"
    fi
fi

# 安装依赖
echo "📦 安装Python依赖..."
pip install -r requirements.txt

# 检查环境变量文件
if [ ! -f .env ]; then
    echo "📝 创建环境变量文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件配置数据库等信息"
    read -p "按回车键继续..."
fi

# 检查Docker服务
echo "🐳 检查Docker服务..."
if ! docker-compose ps | grep -q "aiagent-mysql.*Up"; then
    echo "启动MySQL和Redis..."
    cd ..
    docker-compose up -d
    cd backend
    echo "⏳ 等待数据库就绪..."
    sleep 10
fi

# 数据库迁移
echo "🗄️  执行数据库迁移..."
python manage.py makemigrations
python manage.py migrate

# 询问是否创建超级用户
if ! python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(is_superuser=True).exists())" | grep -q "True"; then
    echo "👤 创建超级用户..."
    python manage.py createsuperuser
fi

# 收集静态文件
echo "📁 收集静态文件..."
python manage.py collectstatic --noinput

echo ""
echo "✅ 启动完成！"
echo ""
echo "🌐 启动开发服务器..."
echo "   访问地址:"
echo "   - API: http://localhost:8000"
echo "   - Swagger: http://localhost:8000/swagger/"
echo "   - Admin: http://localhost:8000/admin/"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 启动开发服务器
python manage.py runserver
