# AnyWay 生产环境部署指南

本文档说明如何在生产环境中部署 AnyWay AI Agent Platform。

---

## 1. 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 4GB 可用内存
- 至少 10GB 可用磁盘空间

---

## 2. 环境配置

### 2.1 创建环境变量文件

在项目根目录创建 `.env` 文件：

```bash
cp .env.example .env
```

### 2.2 配置环境变量

编辑 `.env` 文件，至少修改以下关键配置：

```env
# Django 密钥（必须修改！）
SECRET_KEY=your-very-long-random-secret-key-here

# 允许的主机（修改为你的域名）
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# 数据库密码（必须修改！）
MYSQL_ROOT_PASSWORD=strong-root-password
MYSQL_PASSWORD=strong-database-password

# CORS 配置（修改为你的前端域名）
CORS_ALLOWED_ORIGINS=https://your-domain.com

# OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key
```

**重要安全提示：**
- `SECRET_KEY` 必须使用强随机字符串（至少 50 个字符）
- 数据库密码必须足够强
- 不要将 `.env` 文件提交到版本控制系统

---

## 3. 部署步骤

### 3.1 构建并启动服务

```bash
# 在项目根目录
cd /path/to/AnyWay

# 构建并启动所有服务（后台运行）
docker-compose -f docker-compose.prod.yml up -d --build
```

### 3.2 查看服务状态

```bash
# 查看所有服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### 3.3 创建管理员用户

```bash
# 进入后端容器
docker exec -it aiagent-backend bash

# 创建管理员用户
python manage.py createsuperuser

# 或者使用非交互方式
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'your-password')"
```

---

## 4. 验证部署

### 4.1 检查服务状态

所有服务应该显示为 `Up` 状态：

```bash
docker-compose -f docker-compose.prod.yml ps
```

### 4.2 访问应用

- **前端**: http://your-domain.com 或 http://localhost
- **后端 API**: http://your-domain.com/api/v1/ 或 http://localhost:8000/api/v1/
- **管理后台**: http://your-domain.com/admin/ 或 http://localhost:8000/admin/
- **API 文档**: http://your-domain.com/swagger/ 或 http://localhost:8000/swagger/

### 4.3 健康检查

```bash
# 检查后端健康状态
curl http://localhost:8000/health/

# 检查前端是否正常
curl http://localhost/
```

---

## 5. 常用操作

### 5.1 停止服务

```bash
docker-compose -f docker-compose.prod.yml down
```

### 5.2 重启服务

```bash
docker-compose -f docker-compose.prod.yml restart
```

### 5.3 更新代码后重新部署

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose -f docker-compose.prod.yml up -d --build
```

### 5.4 查看日志

```bash
# 所有服务日志
docker-compose -f docker-compose.prod.yml logs -f

# 特定服务日志
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f celery-worker
```

### 5.5 数据库备份

```bash
# 备份数据库
docker exec aiagent-mysql mysqldump -u root -p${MYSQL_ROOT_PASSWORD} aiagent > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复数据库
docker exec -i aiagent-mysql mysql -u root -p${MYSQL_ROOT_PASSWORD} aiagent < backup.sql
```

---

## 6. 生产环境优化建议

### 6.1 使用 HTTPS

建议使用 Nginx 反向代理并配置 SSL 证书：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 6.2 配置防火墙

只开放必要的端口：
- 80 (HTTP)
- 443 (HTTPS)
- 22 (SSH，如果需要)

不要暴露：
- 8000 (后端，通过 Nginx 代理访问)
- 3306 (MySQL，仅容器内访问)
- 6379 (Redis，仅容器内访问)

### 6.3 监控和日志

- 配置日志轮转
- 使用监控工具（如 Prometheus + Grafana）
- 设置告警

### 6.4 性能优化

- 调整 Gunicorn workers 数量（根据 CPU 核心数）
- 配置 Redis 持久化
- 使用 CDN 加速静态资源

---

## 7. 故障排查

### 7.1 服务无法启动

```bash
# 查看详细日志
docker-compose -f docker-compose.prod.yml logs

# 检查容器状态
docker-compose -f docker-compose.prod.yml ps

# 检查端口占用
netstat -tulpn | grep -E ':(80|8000|3306|6379)'
```

### 7.2 数据库连接失败

- 检查 MySQL 容器是否正常运行
- 检查环境变量中的数据库密码是否正确
- 检查网络连接

### 7.3 前端无法访问后端

- 检查 Nginx 配置
- 检查后端服务是否正常运行
- 检查 CORS 配置

---

## 8. 服务说明

### 8.1 服务列表

| 服务 | 容器名 | 端口 | 说明 |
|------|--------|------|------|
| Frontend | aiagent-frontend | 80 | Vue 前端 + Nginx |
| Backend | aiagent-backend | 8000 | Django + Gunicorn |
| Celery Worker | aiagent-celery-worker | - | 异步任务处理 |
| MySQL | aiagent-mysql | - | 数据库（仅容器内访问） |
| Redis | aiagent-redis | - | 缓存（仅容器内访问） |

### 8.2 数据持久化

以下数据会持久化到 Docker volumes：
- `mysql_data`: MySQL 数据
- `redis_data`: Redis 数据
- `./backend/media`: 上传的文件
- `./backend/logs`: 日志文件

---

## 9. 更新日志

- 2025-11-25: 初始部署文档

