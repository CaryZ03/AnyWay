#!/bin/bash
# AnyWay 服务器部署脚本

set -e

# 配置变量
PROJECT_DIR="/var/www/anyway"
SERVICE_PORT="18080"
DB_NAME="aiagent_prod"
DB_USER="aiagent_user"
DB_PASSWORD="your_secure_password"

echo "=== AnyWay 服务器部署开始 ==="

# 1. 创建项目目录
echo "创建项目目录..."
sudo mkdir -p $PROJECT_DIR
sudo mkdir -p /var/log/anyway
sudo mkdir -p /var/www/anyway/media

# 2. 安装系统依赖
echo "安装系统依赖..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv mysql-server nginx

# 3. 配置数据库
echo "配置数据库..."
sudo mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS $DB_NAME;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF

# 4. 部署代码 (假设代码已在当前目录)
echo "部署代码..."
sudo cp -r . $PROJECT_DIR/
sudo chown -R $USER:$USER $PROJECT_DIR

# 5. 创建虚拟环境
echo "创建虚拟环境..."
cd $PROJECT_DIR
python3 -m venv venv
source venv/bin/activate

# 6. 安装 Python 依赖
echo "安装 Python 依赖..."
pip install -r requirements.txt
pip install gunicorn

# 7. 配置环境变量
echo "配置环境变量..."
cat > .env <<EOF
DEBUG=False
SECRET_KEY=your-production-secret-key-here
ALLOWED_HOSTS=39.102.211.118,localhost,127.0.0.1
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=3306
REDIS_HOST=localhost
REDIS_PORT=6379
CORS_ALLOWED_ORIGINS=http://39.102.211.118:3000,http://localhost:3000
MEDIA_ROOT=/var/www/anyway/media/
STATIC_ROOT=/var/www/anyway/static/
LOGGING_FILE=/var/log/anyway/django.log
EOF

# 8. 数据库迁移
echo "执行数据库迁移..."
python manage.py makemigrations
python manage.py migrate

# 9. 创建超级用户 (非交互)
echo "创建超级用户..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"

# 10. 收集静态文件
echo "收集静态文件..."
python manage.py collectstatic --noinput

# 11. 创建 Systemd 服务
echo "创建系统服务..."
sudo cat > /etc/systemd/system/anyway.service <<EOF
[Unit]
Description=AnyWay Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:$SERVICE_PORT aiagent.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 12. 启动服务
echo "启动服务..."
sudo systemctl daemon-reload
sudo systemctl enable anyway
sudo systemctl start anyway

# 13. 配置防火墙
echo "配置防火墙..."
sudo ufw allow $SERVICE_PORT
sudo ufw allow 22
sudo ufw --force enable

# 14. 检查服务状态
echo "检查服务状态..."
sudo systemctl status anyway
netstat -tlnp | grep $SERVICE_PORT

echo "=== 部署完成 ==="
echo "API 地址: http://39.102.211.118:$SERVICE_PORT"
echo "管理后台: http://39.102.211.118:$SERVICE_PORT/admin/"
echo "用户名: admin / 密码: admin123"
