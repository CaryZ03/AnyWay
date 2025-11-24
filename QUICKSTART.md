# 快速开始指南

## ⚡ 5分钟快速启动

### 前置条件

确保已安装：
- Docker Desktop
- Python 3.11+
- Node.js 18+

### 步骤1：克隆项目

```bash
git clone https://github.com/CaryZ03/AnyWay.git
cd AnyWay
```

### 步骤2：启动数据库

```bash
docker-compose up -d
```

### 步骤3：启动后端

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"
python manage.py runserver
```

### 步骤4：启动前端

```bash
cd frontend
npm install
npm run dev
```

### 步骤5：访问应用

- 🌐 前端: http://localhost:5173
- 📡 后端API: http://localhost:8000
- 📚 API文档: http://localhost:8000/swagger/
- 🔧 Admin后台: http://localhost:8000/admin/ (admin/admin123)

---

## 🎯 核心功能测试

### 1. 测试API

访问 http://localhost:8000/swagger/ 可以直接测试所有API接口

### 2. 创建智能体

```bash
curl -X POST http://localhost:8000/api/v1/agents/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试智能体",
    "description": "这是一个测试智能体",
    "system_prompt": "你是一个友好的AI助手"
  }'
```

### 3. 查看智能体列表

```bash
curl http://localhost:8000/api/v1/agents/
```

---

## 🔍 验证部署

运行以下命令验证所有服务：

```bash
# 检查Docker容器
docker ps

# 检查后端健康
curl http://localhost:8000/health/

# 检查前端
curl http://localhost:5173
```

---

## 📖 下一步

- 查看完整 [部署文档](DEPLOYMENT.md)
- 阅读 [API文档](http://localhost:8000/swagger/)
- 查看 [项目README](README.md)

---

## ❓ 遇到问题？

查看 [常见问题](DEPLOYMENT.md#常见问题) 或提交 [Issue](https://github.com/CaryZ03/AnyWay/issues)
