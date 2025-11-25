# AnyWay 快速启动指南

## 生产环境部署

### 1. 准备环境变量（可选但推荐）

在项目根目录创建 `.env` 文件：

```env
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
MYSQL_ROOT_PASSWORD=root_password
MYSQL_PASSWORD=aiagent_password
CORS_ALLOWED_ORIGINS=http://localhost,https://your-domain.com
OPENAI_API_KEY=your-openai-api-key
```

### 2. 启动服务

**Windows (PowerShell):**
```powershell
# 方式1: 使用部署脚本（推荐）
.\deploy.ps1

# 方式2: 直接使用 docker-compose
docker-compose -f docker-compose.prod.yml up -d --build
```

**Linux/Mac:**
```bash
# 方式1: 使用部署脚本（推荐）
chmod +x deploy.sh
./deploy.sh

# 方式2: 直接使用 docker-compose
docker-compose -f docker-compose.prod.yml up -d --build
```

### 3. 创建管理员用户

```bash
docker exec -it aiagent-backend python manage.py createsuperuser
```

### 4. 访问应用

- **前端**: http://localhost
- **后端 API**: http://localhost:8000/api/v1/
- **管理后台**: http://localhost:8000/admin/
- **API 文档**: http://localhost:8000/swagger/

---

## 常用命令

### 查看服务状态
```bash
docker-compose -f docker-compose.prod.yml ps
```

### 查看日志
```bash
# 所有服务
docker-compose -f docker-compose.prod.yml logs -f

# 特定服务
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### 停止服务
```bash
docker-compose -f docker-compose.prod.yml down
```

### 重启服务
```bash
docker-compose -f docker-compose.prod.yml restart
```

### 更新代码后重新部署
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 开发环境（本地运行）

### 1. 启动数据库和缓存
```bash
docker-compose up -d
```

### 2. 启动后端（本地）
```bash
cd backend
python manage.py runserver 9000
```

### 3. 启动前端（本地）
```bash
cd frontend
npm run dev
```

---

## 故障排查

### 服务无法启动
```bash
# 查看详细日志
docker-compose -f docker-compose.prod.yml logs

# 检查端口占用
netstat -tulpn | grep -E ':(80|8000)'
```

### 数据库连接失败
- 检查 MySQL 容器是否运行: `docker ps | grep mysql`
- 检查环境变量配置
- 查看 MySQL 日志: `docker logs aiagent-mysql`

### 前端无法访问后端
- 检查 Nginx 配置
- 检查后端服务状态
- 查看前端日志: `docker logs aiagent-frontend`

