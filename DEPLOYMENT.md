# AnyWay AI Agent Platform - 部署文档

## 目录

- [系统要求](#系统要求)
- [一键部署](#一键部署)
- [手动部署](#手动部署)
- [环境配置](#环境配置)
- [服务管理](#服务管理)
- [故障排查](#故障排查)
- [性能优化](#性能优化)
- [安全加固](#安全加固)
- [备份与恢复](#备份与恢复)

## 系统要求

### 硬件要求

**最低配置**（适合测试环境）：
- CPU: 2核
- 内存: 4GB
- 磁盘: 20GB

**推荐配置**（生产环境）：
- CPU: 4核或以上
- 内存: 8GB或以上
- 磁盘: 50GB或以上（SSD优先）

### 软件要求

- **操作系统**: Ubuntu 20.04 LTS / 22.04 LTS（推荐）
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **端口**: 18080（前端）、3306（MySQL）、6379（Redis）

## 一键部署

### 快速开始

```bash
# 1. 进入项目目录
cd /root/pku_hlw/AnyWay

# 2. 给予执行权限
chmod +x deploy.sh

# 3. 执行部署脚本
./deploy.sh
```

### 部署流程说明

一键部署脚本会自动完成以下步骤：

1. ✅ 检查系统环境（Ubuntu版本、权限等）
2. ✅ 安装Docker和Docker Compose（如未安装）
3. ✅ 检查端口占用情况
4. ✅ 配置环境变量（自动生成安全密钥）
5. ✅ 创建必要的目录
6. ✅ 构建Docker镜像
7. ✅ 启动所有服务
8. ✅ 初始化数据库
9. ✅ 创建管理员账号
10. ✅ 配置防火墙（可选）

### 部署时间

- 首次部署: 约10-20分钟（取决于网络速度）
- 后续部署: 约2-5分钟

## 手动部署

如果需要更精细的控制，可以手动执行以下步骤：

### 1. 安装Docker

```bash
# 更新包索引
sudo apt-get update

# 安装依赖
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# 添加Docker官方GPG密钥
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 设置Docker仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 启动Docker
sudo systemctl start docker
sudo systemctl enable docker

# 添加当前用户到docker组
sudo usermod -aG docker $USER
newgrp docker
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
# 或
nano .env
```

**必须配置的变量**：

```bash
# Django密钥（使用以下命令生成）
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# 数据库密码（强密码）
MYSQL_ROOT_PASSWORD=your_strong_root_password
MYSQL_PASSWORD=your_strong_app_password

# 允许访问的主机
ALLOWED_HOSTS=localhost,127.0.0.1,your-server-ip

# CORS配置
CORS_ALLOWED_ORIGINS=http://your-server-ip:18080

# OpenAI API Key（必需）
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. 创建必要的目录

```bash
mkdir -p backend/logs backend/media backend/staticfiles
```

### 4. 构建并启动服务

```bash
# 构建镜像（首次部署或代码更新后需要）
docker compose -f docker-compose.prod.yml build

# 启动所有服务
docker compose -f docker-compose.prod.yml up -d

# 查看启动日志
docker compose -f docker-compose.prod.yml logs -f
```

### 5. 初始化数据库

```bash
# 等待MySQL启动完成（约30秒）
sleep 30

# 执行数据库迁移
docker exec aiagent-backend python manage.py migrate

# 创建超级用户
docker exec -it aiagent-backend python manage.py createsuperuser
```

### 6. 验证部署

```bash
# 检查所有容器状态
docker compose -f docker-compose.prod.yml ps

# 应该看到以下容器都在运行：
# - aiagent-mysql
# - aiagent-redis
# - aiagent-backend
# - aiagent-celery-worker
# - aiagent-frontend
```

## 环境配置

### 环境变量说明

| 变量名 | 说明 | 示例 | 必需 |
|--------|------|------|------|
| `SECRET_KEY` | Django密钥 | `django-insecure-xxx` | ✅ |
| `ALLOWED_HOSTS` | 允许访问的主机 | `localhost,127.0.0.1,example.com` | ✅ |
| `CORS_ALLOWED_ORIGINS` | CORS允许的源 | `http://example.com:18080` | ✅ |
| `MYSQL_ROOT_PASSWORD` | MySQL root密码 | `StrongPassword123!` | ✅ |
| `MYSQL_PASSWORD` | 应用数据库密码 | `AppPassword456!` | ✅ |
| `OPENAI_API_KEY` | OpenAI API密钥 | `sk-xxx` | ✅ |
| `OPENAI_API_BASE` | OpenAI API地址 | `https://api.openai.com/v1` | ❌ |

### 域名配置

如果使用域名访问，需要修改以下配置：

1. **修改 `.env` 文件**：

```bash
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com,www.your-domain.com
CORS_ALLOWED_ORIGINS=http://your-domain.com,https://your-domain.com
```

2. **配置Nginx反向代理**（推荐用于HTTPS）：

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    location / {
        proxy_pass http://localhost:18080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **配置SSL证书**（使用Let's Encrypt）：

```bash
# 安装Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

## 服务管理

### 常用命令

```bash
# 查看服务状态
docker compose -f docker-compose.prod.yml ps

# 查看日志
docker compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend

# 启动服务
docker compose -f docker-compose.prod.yml start

# 停止服务
docker compose -f docker-compose.prod.yml stop

# 重启服务
docker compose -f docker-compose.prod.yml restart

# 重启特定服务
docker compose -f docker-compose.prod.yml restart backend

# 停止并删除容器
docker compose -f docker-compose.prod.yml down

# 停止并删除容器和数据卷（⚠️ 会删除数据库数据）
docker compose -f docker-compose.prod.yml down -v
```

### 更新部署

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重新构建镜像
docker compose -f docker-compose.prod.yml build --no-cache

# 3. 重启服务
docker compose -f docker-compose.prod.yml up -d

# 4. 执行数据库迁移（如有）
docker exec aiagent-backend python manage.py migrate
```

### 进入容器

```bash
# 进入后端容器
docker exec -it aiagent-backend bash

# 进入MySQL容器
docker exec -it aiagent-mysql mysql -u root -p

# 进入Redis容器
docker exec -it aiagent-redis redis-cli
```

## 故障排查

### 常见问题

#### 1. 端口已被占用

**问题**：启动服务时提示端口已被占用

**解决方案**：

```bash
# 查看端口占用
sudo lsof -i :18080
sudo lsof -i :3306
sudo lsof -i :6379

# 停止占用端口的进程
sudo kill -9 <PID>

# 或修改docker-compose.prod.yml中的端口映射
```

#### 2. MySQL连接失败

**问题**：后端无法连接到MySQL

**解决方案**：

```bash
# 1. 检查MySQL容器状态
docker ps | grep aiagent-mysql

# 2. 查看MySQL日志
docker logs aiagent-mysql

# 3. 确认MySQL已完全启动
docker exec aiagent-mysql mysqladmin ping -h localhost -u root -p

# 4. 检查数据库用户权限
docker exec -it aiagent-mysql mysql -u root -p
# 在MySQL中执行：
SHOW DATABASES;
SELECT User, Host FROM mysql.user;
```

#### 3. 前端无法访问后端API

**问题**：前端页面打开了，但无法加载数据

**解决方案**：

```bash
# 1. 检查后端服务状态
docker logs aiagent-backend

# 2. 测试API是否可访问
curl http://localhost:18080/api/v1/

# 3. 检查CORS配置
# 确保.env中的CORS_ALLOWED_ORIGINS包含前端地址

# 4. 检查Nginx配置（在frontend容器中）
docker exec aiagent-frontend cat /etc/nginx/conf.d/default.conf
```

#### 4. Celery任务不执行

**问题**：异步任务无法执行

**解决方案**：

```bash
# 1. 检查Celery Worker状态
docker logs aiagent-celery-worker

# 2. 检查Redis连接
docker exec aiagent-redis redis-cli ping

# 3. 重启Celery Worker
docker compose -f docker-compose.prod.yml restart celery-worker
```

#### 5. 静态文件无法加载

**问题**：前端页面样式错乱或图片无法显示

**解决方案**：

```bash
# 1. 收集静态文件
docker exec aiagent-backend python manage.py collectstatic --noinput

# 2. 检查前端构建
docker compose -f docker-compose.prod.yml build frontend --no-cache
docker compose -f docker-compose.prod.yml up -d frontend
```

### 日志查看

```bash
# 查看所有服务日志
docker compose -f docker-compose.prod.yml logs

# 实时查看日志
docker compose -f docker-compose.prod.yml logs -f

# 查看最近100行日志
docker compose -f docker-compose.prod.yml logs --tail=100

# 查看特定时间的日志
docker compose -f docker-compose.prod.yml logs --since 2024-01-01T00:00:00
```

### 健康检查

```bash
# 检查所有容器健康状态
docker ps --format "table {{.Names}}\t{{.Status}}"

# 测试后端API
curl -I http://localhost:18080/api/v1/

# 测试前端
curl -I http://localhost:18080/

# 测试MySQL
docker exec aiagent-mysql mysqladmin ping -h localhost -u root -p

# 测试Redis
docker exec aiagent-redis redis-cli ping
```

## 性能优化

### 1. 数据库优化

**配置MySQL参数**（在docker-compose.prod.yml中添加）：

```yaml
mysql:
  command:
    - --max-connections=500
    - --innodb-buffer-pool-size=1G
    - --innodb-log-file-size=256M
    - --query-cache-size=64M
```

**创建索引**：

```bash
# 进入MySQL
docker exec -it aiagent-mysql mysql -u root -p aiagent

# 查看慢查询
SHOW VARIABLES LIKE 'slow_query%';

# 分析表
ANALYZE TABLE table_name;
```

### 2. Redis优化

**配置Redis持久化**：

```yaml
redis:
  command:
    - redis-server
    - --appendonly yes
    - --maxmemory 512mb
    - --maxmemory-policy allkeys-lru
```

### 3. 应用优化

**增加Gunicorn worker数量**（在docker-compose.prod.yml中）：

```yaml
backend:
  command: >
    sh -c "python manage.py migrate &&
           gunicorn --bind 0.0.0.0:8000 
                    --workers 8
                    --threads 4
                    --worker-class gthread
                    --timeout 120
                    --max-requests 1000
                    --max-requests-jitter 50
                    aiagent.wsgi:application"
```

**推荐的worker配置**：
- Workers数量 = (2 × CPU核心数) + 1
- 例如：4核CPU → 9个workers

### 4. 前端优化

**启用Gzip压缩**（在frontend/nginx.conf中）：

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
```

**配置浏览器缓存**：

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

## 安全加固

### 1. 防火墙配置

```bash
# 安装UFW
sudo apt-get install -y ufw

# 允许SSH
sudo ufw allow 22/tcp

# 允许HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 允许应用端口（如果需要外网直接访问）
sudo ufw allow 18080/tcp

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

### 2. 修改默认密码

```bash
# 定期更新数据库密码
docker exec -it aiagent-mysql mysql -u root -p
# 在MySQL中执行：
ALTER USER 'aiagent'@'%' IDENTIFIED BY 'new_strong_password';
FLUSH PRIVILEGES;

# 同步更新.env文件中的密码
```

### 3. 限制访问

**只允许特定IP访问**（在.env中配置）：

```bash
ALLOWED_HOSTS=your-domain.com,specific-ip-address
```

**配置Nginx IP白名单**：

```nginx
location / {
    allow 192.168.1.0/24;
    deny all;
    proxy_pass http://localhost:18080;
}
```

### 4. 启用HTTPS

参考前面的SSL证书配置部分。

### 5. 定期更新

```bash
# 更新系统包
sudo apt-get update && sudo apt-get upgrade -y

# 更新Docker镜像
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

## 备份与恢复

### 1. 数据库备份

**手动备份**：

```bash
# 备份所有数据库
docker exec aiagent-mysql mysqldump -u root -p aiagent > backup_$(date +%Y%m%d_%H%M%S).sql

# 备份到指定目录
mkdir -p /root/backups
docker exec aiagent-mysql mysqldump -u root -p aiagent > /root/backups/aiagent_$(date +%Y%m%d).sql
```

**自动备份脚本**（backup.sh）：

```bash
#!/bin/bash
BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d_%H%M%S)
MYSQL_PASSWORD="your_mysql_root_password"

mkdir -p $BACKUP_DIR

# 备份数据库
docker exec aiagent-mysql mysqldump -u root -p$MYSQL_PASSWORD aiagent > $BACKUP_DIR/aiagent_$DATE.sql

# 备份媒体文件
tar -czf $BACKUP_DIR/media_$DATE.tar.gz backend/media/

# 删除7天前的备份
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

**配置定时备份**：

```bash
# 编辑crontab
crontab -e

# 添加每天凌晨2点备份
0 2 * * * /root/pku_hlw/AnyWay/backup.sh >> /var/log/aiagent-backup.log 2>&1
```

### 2. 数据恢复

```bash
# 恢复数据库
docker exec -i aiagent-mysql mysql -u root -p aiagent < backup_20240101_120000.sql

# 恢复媒体文件
tar -xzf media_20240101_120000.tar.gz -C backend/
```

### 3. 完整备份

```bash
# 创建完整备份脚本
cat > full_backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 停止服务
cd /root/pku_hlw/AnyWay
docker compose -f docker-compose.prod.yml stop

# 备份Docker卷
docker run --rm \
  -v aiagent_mysql_data:/data \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/mysql_volume_$DATE.tar.gz -C /data .

docker run --rm \
  -v aiagent_redis_data:/data \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/redis_volume_$DATE.tar.gz -C /data .

# 备份配置文件
tar -czf $BACKUP_DIR/config_$DATE.tar.gz .env docker-compose.prod.yml

# 启动服务
docker compose -f docker-compose.prod.yml start

echo "Full backup completed: $DATE"
EOF

chmod +x full_backup.sh
```

## 监控与维护

### 1. 系统监控

```bash
# 查看系统资源使用
docker stats

# 查看磁盘使用
df -h
du -sh /var/lib/docker

# 清理Docker磁盘空间
docker system prune -a --volumes
```

### 2. 日志轮转

**配置Docker日志大小**（在docker-compose.prod.yml中）：

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 3. 健康检查脚本

```bash
cat > health_check.sh << 'EOF'
#!/bin/bash

# 检查前端
if curl -f http://localhost:18080 > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend is down"
    docker compose -f docker-compose.prod.yml restart frontend
fi

# 检查后端
if curl -f http://localhost:18080/api/v1/ > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is down"
    docker compose -f docker-compose.prod.yml restart backend
fi

# 检查数据库
if docker exec aiagent-mysql mysqladmin ping -h localhost --silent 2>/dev/null; then
    echo "✅ MySQL is healthy"
else
    echo "❌ MySQL is down"
    docker compose -f docker-compose.prod.yml restart mysql
fi

# 检查Redis
if docker exec aiagent-redis redis-cli ping | grep -q PONG; then
    echo "✅ Redis is healthy"
else
    echo "❌ Redis is down"
    docker compose -f docker-compose.prod.yml restart redis
fi
EOF

chmod +x health_check.sh

# 配置定时检查（每5分钟）
crontab -e
# 添加：
*/5 * * * * /root/pku_hlw/AnyWay/health_check.sh >> /var/log/aiagent-health.log 2>&1
```

## 技术支持

### 获取帮助

- **查看日志**: `docker compose -f docker-compose.prod.yml logs`
- **GitHub Issues**: [提交问题](https://github.com/your-repo/AnyWay/issues)
- **文档**: 查看项目README.md

### 联系方式

如有问题，请通过以下方式联系：

- 项目主页: [GitHub](https://github.com/your-repo/AnyWay)
- 问题反馈: [Issues](https://github.com/your-repo/AnyWay/issues)

---

**最后更新**: 2025-11-26

