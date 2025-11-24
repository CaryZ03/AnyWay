# AI智能体创作平台 - AnyWay

一个基于Django + Vue 3的AI智能体创作平台，支持智能体管理、工作流编排、知识库集成和插件扩展。

## 项目概述

本项目是一个企业级AI智能体创作平台，旨在帮助用户快速创建、配置和部署AI智能体。平台提供了完整的智能体生命周期管理，包括创建、测试、发布和对话功能。

### 核心功能

- **智能体管理**: 创建、编辑、发布和删除智能体
- **工作流编排**: 可视化工作流设计和执行
- **知识库集成**: 文档上传、分块和向量化
- **插件系统**: 支持OpenAPI规范的插件注册和调用
- **对话功能**: 与智能体进行实时对话
- **LLM集成**: 支持OpenAI等主流LLM服务

## 技术架构

### 后端技术栈
- **框架**: Django 5.0.1 + Django REST Framework
- **数据库**: MySQL 8.0
- **缓存**: Redis 7
- **任务队列**: Celery
- **API文档**: Swagger (drf-yasg)
- **AI集成**: OpenAI, LangChain

### 前端技术栈
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI组件**: Element Plus (待集成)
- **状态管理**: Pinia (待集成)

## 项目结构

```
AnyWay/
├── backend/              # Django后端
│   ├── aiagent/         # Django项目配置
│   ├── apps/            # 应用模块
│   │   ├── agent/       # 智能体管理
│   │   ├── workflow/    # 工作流管理
│   │   ├── knowledge/   # 知识库管理
│   │   ├── plugin/      # 插件管理
│   │   └── llm/         # LLM服务
│   ├── utils/           # 工具类
│   ├── scripts/         # 脚本文件
│   └── requirements.txt # Python依赖
├── frontend/            # Vue 3前端
│   ├── src/
│   │   ├── components/  # 组件
│   │   ├── views/       # 页面
│   │   └── types/       # TypeScript类型
│   └── package.json
├── docs/                # 文档
│   ├── api/            # API文档
│   ├── architecture/   # 架构文档
│   ├── database/       # 数据库文档
│   └── requirements/   # 需求文档
├── docker-compose.yml       # 开发环境Docker配置
├── docker-compose.prod.yml  # 生产环境Docker配置
├── deploy.sh               # Linux/Mac部署脚本
├── deploy.ps1              # Windows部署脚本
└── README.md               # 项目说明
```

## 快速开始

### 前置要求

- Docker & Docker Compose
- Python 3.11+ (本地开发)
- Node.js 18+ (本地开发)
- MySQL 8.0
- Redis 7

### 方式一: Docker一键部署（推荐）

#### 1. 克隆项目

```bash
git clone <repository-url>
cd AnyWay
```

#### 2. 配置环境变量

```bash
# 开发环境
cp backend/.env.example backend/.env

# 生产环境
cp .env.prod.example .env.prod
# 编辑 .env.prod 填写实际配置
```

#### 3. 启动服务

**开发环境**（仅启动MySQL和Redis）:
```bash
docker-compose up -d
```

**生产环境**（完整部署）:

Linux/Mac:
```bash
chmod +x deploy.sh
./deploy.sh
```

Windows PowerShell:
```powershell
.\deploy.ps1
```

或手动执行:
```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

#### 4. 访问服务

- 前端: http://localhost
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/swagger/
- Admin后台: http://localhost:8000/admin/

### 方式二: 本地开发

#### 后端开发

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env

# 启动数据库和Redis
cd ..
docker-compose up -d

# 数据库迁移
cd backend
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

#### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:5173

## API文档

### Swagger文档

启动后端服务后访问: http://localhost:8000/swagger/

### 主要API端点

#### 智能体管理
- `GET /api/v1/agents/` - 获取智能体列表
- `POST /api/v1/agents/` - 创建智能体
- `GET /api/v1/agents/{id}/` - 获取智能体详情
- `PUT /api/v1/agents/{id}/` - 更新智能体
- `DELETE /api/v1/agents/{id}/` - 删除智能体
- `POST /api/v1/agents/{id}/publish/` - 发布智能体
- `POST /api/v1/agents/{id}/chat/` - 与智能体对话

#### 工作流管理
- `GET /api/v1/workflows/` - 获取工作流列表
- `POST /api/v1/workflows/` - 创建工作流
- `POST /api/v1/workflows/{id}/execute/` - 执行工作流

#### 知识库管理
- `GET /api/v1/knowledge/` - 获取知识库列表
- `POST /api/v1/knowledge/` - 创建知识库
- `POST /api/v1/knowledge/{id}/upload/` - 上传文档

#### 插件管理
- `GET /api/v1/plugins/` - 获取插件列表
- `POST /api/v1/plugins/` - 注册插件
- `POST /api/v1/plugins/{id}/enable/` - 启用插件

详细API文档请查看 [backend/README.md](backend/README.md)

## 数据库设计

### 核心表结构

1. **agent** - 智能体表
2. **conversation** - 对话记录表
3. **workflow** - 工作流表
4. **workflow_execution** - 工作流执行记录表
5. **knowledge_base** - 知识库表
6. **document** - 文档表
7. **document_chunk** - 文档分块表
8. **plugin** - 插件表

详细数据库设计请查看 [docs/database/](docs/database/)

## 配置说明

### 环境变量

#### 后端配置 (backend/.env)

```env
# Django配置
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库配置
DB_NAME=aiagent
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379

# OpenAI配置
OPENAI_API_KEY=your-openai-api-key
```

#### 生产环境配置 (.env.prod)

```env
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.com
MYSQL_ROOT_PASSWORD=your-root-password
MYSQL_PASSWORD=your-mysql-password
OPENAI_API_KEY=your-openai-api-key
```

## 开发指南

### 后端开发

详见 [backend/README.md](backend/README.md)

### 前端开发

详见 [frontend/README.md](frontend/README.md)

## 测试

### 后端测试

```bash
cd backend
python manage.py test
```

### 前端测试

```bash
cd frontend
npm run test
```

## 部署

### Docker部署

使用提供的部署脚本：

```bash
# Linux/Mac
./deploy.sh

# Windows
.\deploy.ps1
```

### 手动部署

1. 构建镜像
```bash
docker-compose -f docker-compose.prod.yml build
```

2. 启动服务
```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

3. 查看日志
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

4. 停止服务
```bash
docker-compose -f docker-compose.prod.yml down
```

## 版本历史

### v1.0.0 (第1周版本)
- 项目框架搭建
- 数据库设计和建表
- 智能体CRUD API
- 工作流CRUD API
- 知识库CRUD API
- 插件CRUD API
- Docker配置
- 部署脚本
- API文档

## 后续计划

### 第2周
- [ ] 前端页面开发
- [ ] 智能体对话界面
- [ ] 工作流可视化编辑器

### 第3周
- [ ] 知识库向量化
- [ ] RAG检索增强
- [ ] 插件动态调用

### 第4周
- [ ] 用户认证和权限
- [ ] 性能优化
- [ ] 生产环境部署

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 团队

- 后端开发: Django + DRF
- 前端开发: Vue 3 + TypeScript
- 数据库设计: MySQL
- DevOps: Docker + Docker Compose

## 联系方式

如有问题，请提交Issue或联系项目维护者.
