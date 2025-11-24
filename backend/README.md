# AI智能体创作平台 - 后端服务

基于Django + Django REST Framework的AI智能体创作平台后端服务。

## 技术栈

- **框架**: Django 5.0.1
- **API**: Django REST Framework 3.14.0
- **数据库**: MySQL 8.0
- **缓存**: Redis 7
- **任务队列**: Celery
- **API文档**: drf-yasg (Swagger)
- **AI集成**: OpenAI, LangChain

## 项目结构

```
backend/
├── aiagent/              # Django项目配置
│   ├── settings.py       # 配置文件
│   ├── urls.py          # 主路由
│   ├── wsgi.py          # WSGI入口
│   └── celery.py        # Celery配置
├── apps/                # 应用模块
│   ├── agent/           # 智能体管理
│   ├── workflow/        # 工作流管理
│   ├── knowledge/       # 知识库管理
│   ├── plugin/          # 插件管理
│   └── llm/             # LLM服务集成
├── utils/               # 工具类
│   ├── response.py      # 统一响应格式
│   └── exception_handler.py  # 异常处理
├── scripts/             # 脚本文件
│   └── init.sql         # 数据库初始化
├── manage.py            # Django管理命令
├── requirements.txt     # Python依赖
├── Dockerfile           # Docker镜像构建
└── .env.example         # 环境变量示例
```

## 核心功能模块

### 1. 智能体管理 (apps/agent)
- ✅ 创建、查看、编辑、删除智能体
- ✅ 智能体发布
- ✅ 智能体测试
- ✅ 智能体对话
- ✅ 对话历史记录

**API端点**:
- `GET /api/v1/agents/` - 获取智能体列表
- `POST /api/v1/agents/` - 创建智能体
- `GET /api/v1/agents/{id}/` - 获取智能体详情
- `PUT /api/v1/agents/{id}/` - 更新智能体
- `DELETE /api/v1/agents/{id}/` - 删除智能体
- `POST /api/v1/agents/{id}/publish/` - 发布智能体
- `POST /api/v1/agents/{id}/test/` - 测试智能体
- `POST /api/v1/agents/{id}/chat/` - 与智能体对话

### 2. 工作流管理 (apps/workflow)
- ✅ 创建、查看、编辑、删除工作流
- ✅ 工作流执行引擎
- ✅ 执行历史记录
- ✅ DAG验证

**API端点**:
- `GET /api/v1/workflows/` - 获取工作流列表
- `POST /api/v1/workflows/` - 创建工作流
- `GET /api/v1/workflows/{id}/` - 获取工作流详情
- `PUT /api/v1/workflows/{id}/` - 更新工作流
- `DELETE /api/v1/workflows/{id}/` - 删除工作流
- `POST /api/v1/workflows/{id}/execute/` - 执行工作流
- `GET /api/v1/workflows/{id}/executions/` - 获取执行历史

### 3. 知识库管理 (apps/knowledge)
- ✅ 创建、查看、编辑、删除知识库
- ✅ 文档上传（TXT, Markdown）
- ✅ 文档分块处理
- ✅ 向量化（待实现）
- ✅ 知识库搜索（待实现）

**API端点**:
- `GET /api/v1/knowledge/` - 获取知识库列表
- `POST /api/v1/knowledge/` - 创建知识库
- `GET /api/v1/knowledge/{id}/` - 获取知识库详情
- `PUT /api/v1/knowledge/{id}/` - 更新知识库
- `DELETE /api/v1/knowledge/{id}/` - 删除知识库
- `POST /api/v1/knowledge/{id}/upload/` - 上传文档
- `GET /api/v1/knowledge/{id}/documents/` - 获取文档列表
- `POST /api/v1/knowledge/{id}/search/` - 搜索知识库

### 4. 插件管理 (apps/plugin)
- ✅ 注册、查看、编辑、删除插件
- ✅ 启用/禁用插件
- ✅ OpenAPI规范验证

**API端点**:
- `GET /api/v1/plugins/` - 获取插件列表
- `POST /api/v1/plugins/` - 注册插件
- `GET /api/v1/plugins/{id}/` - 获取插件详情
- `PUT /api/v1/plugins/{id}/` - 更新插件
- `DELETE /api/v1/plugins/{id}/` - 删除插件
- `POST /api/v1/plugins/{id}/enable/` - 启用插件
- `POST /api/v1/plugins/{id}/disable/` - 禁用插件

### 5. LLM服务 (apps/llm)
- ✅ OpenAI集成
- ✅ 聊天接口
- ✅ 文本嵌入（待实现）

**API端点**:
- `POST /api/v1/llm/chat/` - LLM聊天接口

## 快速开始

### 本地开发环境

#### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填写配置
```

#### 3. 启动数据库和Redis

```bash
# 在项目根目录
docker-compose up -d
```

#### 4. 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 5. 创建超级用户

```bash
python manage.py createsuperuser
```

#### 6. 启动开发服务器

```bash
python manage.py runserver
```

访问:
- API文档: http://localhost:8000/swagger/
- Admin后台: http://localhost:8000/admin/

### Docker部署

#### 开发环境

```bash
# 启动MySQL和Redis
docker-compose up -d
```

#### 生产环境

```bash
# 1. 配置环境变量
cp .env.prod.example .env.prod
# 编辑 .env.prod

# 2. 使用部署脚本（Linux/Mac）
chmod +x deploy.sh
./deploy.sh

# 或使用PowerShell脚本（Windows）
.\deploy.ps1

# 或手动部署
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

## 数据库设计

### 核心表

1. **agent** - 智能体表
   - 存储智能体配置、提示词、模型配置等
   - 关联工作流、知识库、插件

2. **conversation** - 对话记录表
   - 存储用户与智能体的对话历史

3. **workflow** - 工作流表
   - 存储工作流定义（节点和连线）

4. **workflow_execution** - 工作流执行记录表
   - 记录工作流执行状态和结果

5. **knowledge_base** - 知识库表
   - 存储知识库基本信息

6. **document** - 文档表
   - 存储上传的文档信息

7. **document_chunk** - 文档分块表
   - 存储文档分块和向量嵌入

8. **plugin** - 插件表
   - 存储插件信息和OpenAPI规范

## API文档

启动服务后访问:
- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## 开发指南

### 添加新的API

1. 在对应的app中创建serializer
2. 在views.py中创建ViewSet或APIView
3. 在urls.py中注册路由
4. 使用@swagger_auto_schema添加API文档

### 统一响应格式

使用`utils.response.ApiResponse`类:

```python
from utils.response import ApiResponse

# 成功响应
return ApiResponse.success(data=data, message='操作成功')

# 错误响应
return ApiResponse.error(message='操作失败')

# 创建成功
return ApiResponse.created(data=data, message='创建成功')
```

### 异常处理

自定义异常处理器会自动捕获异常并返回统一格式。

## 测试

```bash
# 运行测试
python manage.py test

# 运行特定app的测试
python manage.py test apps.agent
```

## 常见问题

### 1. 数据库连接失败

检查MySQL是否启动，环境变量配置是否正确。

### 2. Redis连接失败

检查Redis是否启动，端口是否正确。

### 3. 静态文件404

运行 `python manage.py collectstatic`

## 待实现功能

- [ ] 向量数据库集成（Pinecone/Milvus）
- [ ] 完整的工作流DAG执行引擎
- [ ] 插件动态调用
- [ ] 用户认证和权限管理
- [ ] API限流
- [ ] 日志监控
- [ ] 单元测试覆盖

## 许可证

MIT License
