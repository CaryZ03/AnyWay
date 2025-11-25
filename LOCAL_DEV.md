# 本地开发环境快速启动指南

## 前置要求
- Docker Desktop (运行中)
- Python 3.8+
- Node.js 16+

## 快速启动

### 1. 启动数据库服务
```powershell
docker-compose up -d mysql redis
```

### 2. 启动后端服务
```powershell
cd backend
python manage.py runserver 0.0.0.0:8000
```

### 3. 启动前端服务
```powershell
cd frontend
npm run dev
```

## 访问地址
- **前端应用**: http://localhost:5173
- **后端 API**: http://localhost:8000/api/v1/
- **后端管理**: http://localhost:8000/admin/
- **API 文档**: http://localhost:8000/swagger/

## 常用命令

### 查看服务状态
```powershell
docker-compose ps
```

### 停止服务
```powershell
# 停止数据库
docker-compose down

# 停止后端: Ctrl+C
# 停止前端: Ctrl+C
```

### 数据库迁移
```powershell
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 创建管理员用户
```powershell
cd backend
python manage.py createsuperuser
```

## 故障排查

### 前端无法连接后端
1. 检查后端是否运行在 8000 端口
2. 检查 CORS 配置
3. 查看浏览器控制台错误信息

### 数据库连接失败
1. 确认 Docker 服务正在运行
2. 检查 MySQL 容器状态: `docker ps | findstr mysql`
3. 查看容器日志: `docker logs aiagent-mysql`

### 端口被占用
```powershell
# 查看端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :5173
netstat -ano | findstr :3308

# 结束进程
taskkill /PID <进程ID> /F
```

## 开发提示
- 前端修改会自动热重载
- 后端修改需要重启服务
- 数据库数据持久化在 Docker volumes 中
