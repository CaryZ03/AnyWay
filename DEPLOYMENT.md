# AnyWay - AI智能体创作平台部署指南

## 📋 目录

- [环境要求](#环境要求)
- [本地开发部署](#本地开发部署)
- [生产环境部署](#生产环境部署)
- [常见问题](#常见问题)

---

## 🔧 环境要求

### 必需软件

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Python** 3.11+ (本地开发)
- **Node.js** 18+ (本地开发)
- **Git**

### 推荐配置

- CPU: 4核+
- 内存: 8GB+
- 磁盘: 20GB+

---

## 🚀 本地开发部署

### 1. 克隆项目

```bash
git clone https://github.com/CaryZ03/AnyWay.git
cd AnyWay
```

### 2. 启动基础服务（MySQL + Redis）

```bash
# 启动数据库和缓存服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

**服务端口：**
- MySQL: `3308`
- Redis: `6379`

### 3. 配置后端环境

```bash
cd backend

# 安装Python依赖
pip install -r requirements.txt

# 配置环境变量（已有.env文件，无需修改）
# 数据库端口: 3308
# 数据库密码: root_password

# 执行数据库迁移
python manage.py migrate

# 创建管理员账户
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"

# 启动后端服务
python manage.py runserver
```

**后端访问地址：**
- API: http://localhost:8000
- Swagger文档: http://localhost:8000/swagger/
- Admin后台: http://localhost:8000/admin/
  - 用户名: `admin`
  - 密码: `admin123`

### 4. 启动前端服务

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

**前端访问地址：**
- 前端应用: http://localhost:5173

### 5. 验证部署

访问以下地址确认服务正常：

- ✅ 前端: http://localhost:5173
- ✅ 后端API: http://localhost:8000/health/
- ✅ Swagger文档: http://localhost:8000/swagger/

---

## 🏭 生产环境部署

### 方式一：Docker Compose 一键部署（推荐）

#### 1. 配置环境变量

```bash
# 复制环境变量模板
cp .env.prod.example .env.prod

# 编辑配置文件
nano .env.prod
```

**必须修改的配置：**
```env
# Django密钥（生产环境必须修改）
SECRET_KEY=your-production-secret-key-here

# 允许的域名
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# 数据库密码
MYSQL_ROOT_PASSWORD=your-secure-root-password
MYSQL_PASSWORD=your-secure-mysql-password

# OpenAI API Key（如需使用AI功能）
OPENAI_API_KEY=sk-your-real-openai-api-key

# CORS配置
CORS_ALLOWED_ORIGINS=https://your-domain.com
```

#### 2. 构建并启动服务

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Windows PowerShell:**
```powershell
.\deploy.ps1
```

**或手动执行：**
```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

#### 3. 查看服务状态

```bash
# 查看所有容器
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs -f backend
```

#### 4. 初始化数据库

```bash
# 进入后端容器
docker-compose -f docker-compose.prod.yml exec backend bash

# 执行迁移
python manage.py migrate

# 创建管理员
python manage.py createsuperuser

# 退出容器
exit
```

#### 5. 访问服务

- 前端: http://your-domain.com
- 后端API: http://your-domain.com:8000
- API文档: http://your-domain.com:8000/swagger/

### 方式二：手动部署

#### 后端部署

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export DEBUG=False
export SECRET_KEY=your-secret-key
export ALLOWED_HOSTS=your-domain.com
export DB_HOST=your-mysql-host
export DB_PORT=3306
export DB_PASSWORD=your-password

# 执行迁移
python manage.py migrate

# 收集静态文件
python manage.py collectstatic --noinput

# 使用Gunicorn启动
gunicorn aiagent.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

#### 前端部署

```bash
cd frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 使用nginx或其他web服务器托管dist目录
```

---

## 🔄 服务管理

### 启动服务

```bash
# 开发环境
docker-compose up -d

# 生产环境
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### 停止服务

```bash
# 开发环境
docker-compose down

# 生产环境
docker-compose -f docker-compose.prod.yml down
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
```

### 查看日志

```bash
# 查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f mysql
```

### 更新代码

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

# 执行数据库迁移（如有）
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

---

## 🐛 常见问题

### 1. 端口冲突

**问题：** MySQL 3306端口被占用

**解决：** 
- 开发环境已配置为3308端口
- 如需修改，编辑 `docker-compose.yml` 中的端口映射

### 2. 数据库连接失败

**问题：** `Access denied for user 'root'`

**解决：**
```bash
# 检查.env文件中的数据库密码
# 确保与docker-compose.yml中的密码一致
# 默认密码: root_password
```

### 3. Swagger文档加载失败

**问题：** `Failed to load API definition`

**解决：**
```bash
# 确保已执行数据库迁移
python manage.py migrate

# 重启后端服务
```

### 4. 前端无法连接后端

**问题：** CORS错误

**解决：**
- 检查后端 `.env` 文件中的 `CORS_ALLOWED_ORIGINS` 配置
- 确保包含前端地址：`http://localhost:5173`

### 5. Docker镜像拉取失败

**问题：** 网络连接超时

**解决：**
```bash
# 配置Docker镜像加速器
# 或使用代理
```

### 6. 依赖安装失败

**问题：** `mysqlclient` 安装失败

**解决：**
- Windows: 安装 Microsoft C++ Build Tools
- Linux: `sudo apt-get install python3-dev default-libmysqlclient-dev build-essential`
- Mac: `brew install mysql`

---

## 📊 系统架构

```
┌─────────────┐
│   用户      │
└──────┬──────┘
       │
       ↓
┌─────────────┐      ┌──────────────┐
│  Frontend   │─────→│   Backend    │
│  (Vue 3)    │      │  (Django)    │
│  Port: 5173 │      │  Port: 8000  │
└─────────────┘      └──────┬───────┘
                            │
                ┌───────────┼───────────┐
                ↓           ↓           ↓
         ┌──────────┐ ┌─────────┐ ┌─────────┐
         │  MySQL   │ │  Redis  │ │ Celery  │
         │Port: 3308│ │Port:6379│ │ Worker  │
         └──────────┘ └─────────┘ └─────────┘
```

---

## 📝 API文档

完整的API文档请访问：
- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/

主要API端点：

| 模块 | 端点 | 说明 |
|------|------|------|
| 智能体 | `/api/v1/agents/` | 智能体CRUD、发布、对话 |
| 工作流 | `/api/v1/workflows/` | 工作流管理和执行 |
| 知识库 | `/api/v1/knowledge/` | 知识库和文档管理 |
| 插件 | `/api/v1/plugins/` | 插件注册和管理 |
| LLM | `/api/v1/llm/` | LLM服务调用 |

---

## 🔐 安全建议

### 生产环境必做

1. **修改默认密码**
   - 数据库root密码
   - Django SECRET_KEY
   - Admin管理员密码

2. **启用HTTPS**
   - 配置SSL证书
   - 强制HTTPS重定向

3. **限制访问**
   - 配置防火墙规则
   - 仅开放必要端口（80, 443）
   - 数据库端口不对外开放

4. **定期备份**
   - 数据库定期备份
   - 代码版本控制

5. **监控和日志**
   - 配置日志收集
   - 设置监控告警

---

## 📞 技术支持

如遇问题，请：
1. 查看本文档的常见问题部分
2. 查看项目 [Issues](https://github.com/CaryZ03/AnyWay/issues)
3. 提交新的 Issue

---

## 📄 许可证

MIT License

---

**最后更新：** 2025-11-24
