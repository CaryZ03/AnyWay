# AnyWay AI Agent Platform

一个现代化的 AI 智能体管理平台，支持智能体的创建、配置、测试和部署。

## 项目结构

```
AnyWay/
├── backend/              # Django 后端
│   ├── apps/            # 应用模块
│   │   ├── agent/       # 智能体模块
│   │   ├── workflow/    # 工作流模块
│   │   ├── knowledge/   # 知识库模块
│   │   └── plugin/      # 插件模块
│   ├── aiagent/         # 项目配置
│   └── utils/           # 工具函数
├── frontend/            # Vue 3 前端
│   ├── src/
│   │   ├── api/         # API 接口
│   │   ├── components/  # 组件
│   │   ├── types/       # TypeScript 类型
│   │   └── utils/       # 工具函数
│   └── public/          # 静态资源
└── docs/                # 文档
```

## 技术栈

### 后端
- **框架**: Django 5.0 + Django REST Framework
- **数据库**: MySQL 8.0
- **缓存**: Redis 7
- **任务队列**: Celery
- **API 文档**: drf-yasg (Swagger)

### 前端
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **HTTP 客户端**: Axios
- **样式**: 原生 CSS (现代化设计)

## 快速开始

### 环境要求
- Docker Desktop
- Python 3.8+
- Node.js 16+

### 本地开发

1. **启动数据库服务**
```powershell
docker-compose up -d mysql redis
```

2. **启动后端**
```powershell
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

3. **启动前端**
```powershell
cd frontend
npm install
npm run dev
```

4. **访问应用**
- 前端: http://localhost:5173
- 后端 API: http://localhost:8000/api/v1/
- API 文档: http://localhost:8000/swagger/
- 管理后台: http://localhost:8000/admin/

## 功能特性

### 智能体管理
- ✅ 创建和配置智能体
- ✅ 设置系统提示词和用户提示模板
- ✅ 配置模型参数
- ✅ 关联工作流、知识库和插件
- ✅ 发布和测试智能体

### 工作流编排
- ✅ 可视化工作流编辑
- ✅ 节点和边的管理
- ✅ 工作流执行和测试

### 知识库
- ✅ 文档上传和管理
- ✅ 向量化存储
- ✅ 语义搜索

### 插件系统
- ✅ 插件注册和管理
- ✅ 参数配置
- ✅ 插件启用/禁用

## API 文档

访问 http://localhost:8000/swagger/ 查看完整的 API 文档。

### 主要 API 端点

#### 智能体
- `GET /api/v1/agents/` - 获取智能体列表
- `POST /api/v1/agents/` - 创建智能体
- `GET /api/v1/agents/{id}/` - 获取智能体详情
- `PATCH /api/v1/agents/{id}/` - 更新智能体
- `DELETE /api/v1/agents/{id}/` - 删除智能体
- `POST /api/v1/agents/{id}/publish/` - 发布智能体
- `POST /api/v1/agents/{id}/chat/` - 与智能体对话

#### 工作流
- `GET /api/v1/workflows/` - 获取工作流列表
- `POST /api/v1/workflows/` - 创建工作流
- `POST /api/v1/workflows/{id}/execute/` - 执行工作流

#### 知识库
- `GET /api/v1/knowledge/` - 获取知识库列表
- `POST /api/v1/knowledge/` - 创建知识库
- `POST /api/v1/knowledge/{id}/upload/` - 上传文档
- `POST /api/v1/knowledge/{id}/search/` - 搜索知识库

#### 插件
- `GET /api/v1/plugins/` - 获取插件列表
- `POST /api/v1/plugins/` - 注册插件
- `POST /api/v1/plugins/{id}/execute/` - 执行插件

## 生产部署

### 使用 Docker Compose

```powershell
# 构建并启动所有服务
docker-compose -f docker-compose.prod.yml up -d --build

# 创建管理员用户
docker exec -it aiagent-backend python manage.py createsuperuser

# 访问应用
# 前端: http://localhost:18080
# 后端: 通过 Nginx 代理访问
```

详细部署说明请参考 [DEPLOYMENT.md](./DEPLOYMENT.md)

## 开发指南

### 后端开发
- 遵循 Django 最佳实践
- 使用 DRF 序列化器进行数据验证
- 统一使用 `ApiResponse` 返回响应
- 编写单元测试

### 前端开发
- 使用 TypeScript 确保类型安全
- 组件化开发
- 统一使用 `request` 工具进行 API 调用
- 遵循 Vue 3 Composition API 规范

## 测试

### 后端测试
```powershell
cd backend
python manage.py test
```

### 前端测试
```powershell
cd frontend
npm run test
```

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

MIT License

## 联系方式

- 项目主页: [GitHub](https://github.com/your-repo/AnyWay)
- 问题反馈: [Issues](https://github.com/your-repo/AnyWay/issues)

## 更新日志

### v1.0.0 (2025-11-25)
- ✅ 完成基础架构搭建
- ✅ 实现智能体管理功能
- ✅ 实现工作流编排
- ✅ 实现知识库管理
- ✅ 实现插件系统
- ✅ 完成前后端联调
