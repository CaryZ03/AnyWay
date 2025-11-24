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

### ⚡ 5分钟快速启动

```bash
# 1. 克隆项目
git clone https://github.com/CaryZ03/AnyWay.git
cd AnyWay

# 2. 启动数据库
docker-compose up -d

# 3. 启动后端
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# 4. 启动前端（新终端）
cd frontend
npm install
npm run dev
```

### 📖 详细文档

- **[快速开始指南](QUICKSTART.md)** - 5分钟快速上手
- **[完整部署文档](DEPLOYMENT.md)** - 本地开发和生产部署详细说明
- **[API文档](http://localhost:8000/swagger/)** - 在线API文档（需先启动后端）

### 🌐 访问地址

- 前端: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/swagger/
- Admin后台: http://localhost:8000/admin/ (admin/admin123)

## API文档

完整的API文档请访问：
- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/

主要API模块：

| 模块 | 端点 | 说明 |
|------|------|------|
| 智能体 | `/api/v1/agents/` | 智能体CRUD、发布、对话 |
| 工作流 | `/api/v1/workflows/` | 工作流管理和执行 |
| 知识库 | `/api/v1/knowledge/` | 知识库和文档管理 |
| 插件 | `/api/v1/plugins/` | 插件注册和管理 |
| LLM | `/api/v1/llm/` | LLM服务调用 |

## 数据库设计

核心数据表：Agent（智能体）、Conversation（对话）、Workflow（工作流）、KnowledgeBase（知识库）、Document（文档）、Plugin（插件）

详细设计文档请查看 [docs/database/](docs/database/)

## 配置说明

### 环境变量

开发环境配置文件：`backend/.env`
生产环境配置文件：`.env.prod`

主要配置项：
- Django密钥和调试模式
- 数据库连接信息
- Redis配置
- CORS跨域设置
- OpenAI API Key

详细配置说明请查看 [DEPLOYMENT.md](DEPLOYMENT.md)

## 开发指南

- **后端开发**: 查看 [backend/README.md](backend/README.md)
- **前端开发**: 查看 [frontend/README.md](frontend/README.md)
- **部署文档**: 查看 [DEPLOYMENT.md](DEPLOYMENT.md)

## 开发进度

### ✅ 已完成
- 项目基础架构
- 数据库设计和迁移
- RESTful API实现
- Swagger API文档
- Docker容器化
- 本地开发环境配置

### 🚧 进行中
- 前端页面开发
- AI功能集成
- 工作流可视化

### 📋 计划中
- 用户认证系统
- 知识库向量化
- 插件市场
- 性能优化

## 贡献指南

欢迎提交Issue和Pull Request！

## 技术支持

- 📖 查看 [文档](DEPLOYMENT.md)
- 🐛 提交 [Issue](https://github.com/CaryZ03/AnyWay/issues)
- 💬 参与 [Discussions](https://github.com/CaryZ03/AnyWay/discussions)

## 许可证

MIT License

---

**开发团队**: Django + Vue 3 + Docker  
**最后更新**: 2025-11-24
