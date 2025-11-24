# 开发环境搭建指南

## 第1周任务完成情况

### ✅ 已完成

1. **项目结构搭建**
   - ✅ Django后端项目框架
   - ✅ Vue 3前端项目框架（已存在）
   - ✅ Docker Compose配置

2. **数据库设计**
   - ✅ 8个核心表设计
   - ✅ ER图设计
   - ✅ 数据库初始化脚本

3. **后端API实现**
   - ✅ 智能体CRUD API
   - ✅ 工作流CRUD API
   - ✅ 知识库CRUD API
   - ✅ 插件CRUD API
   - ✅ LLM服务集成
   - ✅ 统一响应格式
   - ✅ 异常处理

4. **Docker化部署**
   - ✅ 后端Dockerfile
   - ✅ docker-compose.yml（开发环境）
   - ✅ docker-compose.prod.yml（生产环境）
   - ✅ 部署脚本（Linux/Mac/Windows）

5. **文档**
   - ✅ 项目README
   - ✅ 后端README
   - ✅ API文档
   - ✅ 数据库设计文档
   - ✅ Swagger自动文档

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- MySQL 8.0
- Redis 7

### 本地开发步骤

#### 1. 启动基础服务

```bash
# 启动MySQL和Redis
docker-compose up -d

# 查看服务状态
docker-compose ps
```

#### 2. 后端开发

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，配置数据库等信息

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

访问：
- API: http://localhost:8000
- Swagger文档: http://localhost:8000/swagger/
- Admin后台: http://localhost:8000/admin/

#### 3. 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问: http://localhost:5173

### 测试API

#### 使用Swagger UI

访问 http://localhost:8000/swagger/ 可以直接测试所有API。

#### 使用curl

```bash
# 创建智能体
curl -X POST http://localhost:8000/api/v1/agents/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试智能体",
    "description": "这是一个测试",
    "system_prompt": "你是一个AI助手",
    "status": "draft"
  }'

# 获取智能体列表
curl http://localhost:8000/api/v1/agents/

# 发布智能体
curl -X POST http://localhost:8000/api/v1/agents/1/publish/

# 测试对话
curl -X POST http://localhost:8000/api/v1/agents/1/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好"
  }'
```

## 开发规范

### 代码风格

#### Python (PEP 8)
```python
# 使用4个空格缩进
# 类名使用大驼峰
class AgentService:
    pass

# 函数名使用小写+下划线
def get_agent_list():
    pass

# 常量使用大写+下划线
MAX_RETRY_COUNT = 3
```

#### TypeScript
```typescript
// 使用2个空格缩进
// 接口名使用大驼峰
interface Agent {
  id: number;
  name: string;
}

// 函数名使用小驼峰
function getAgentList(): Agent[] {
  return [];
}
```

### Git提交规范

```bash
# 格式: <type>(<scope>): <subject>

# 类型(type)
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试
chore: 构建/工具链

# 示例
git commit -m "feat(agent): 添加智能体发布功能"
git commit -m "fix(workflow): 修复工作流执行错误"
git commit -m "docs(api): 更新API文档"
```

### 分支管理

```
main          # 主分支，生产环境
├── develop   # 开发分支
    ├── feature/agent-crud      # 功能分支
    ├── feature/workflow-engine # 功能分支
    └── bugfix/fix-xxx          # 修复分支
```

## 常见问题

### 1. 数据库连接失败

**问题**: `django.db.utils.OperationalError: (2003, "Can't connect to MySQL server")`

**解决**:
```bash
# 检查MySQL是否启动
docker-compose ps

# 查看MySQL日志
docker-compose logs mysql

# 检查.env配置
cat backend/.env
```

### 2. Redis连接失败

**问题**: `redis.exceptions.ConnectionError`

**解决**:
```bash
# 检查Redis是否启动
docker-compose ps

# 测试Redis连接
docker exec -it aiagent-redis redis-cli ping
```

### 3. 端口被占用

**问题**: `Error: Port 8000 is already in use`

**解决**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### 4. 依赖安装失败

**问题**: `pip install` 失败

**解决**:
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或配置pip
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 5. 迁移文件冲突

**问题**: 多人开发时迁移文件冲突

**解决**:
```bash
# 删除冲突的迁移文件
rm backend/apps/*/migrations/00*.py

# 重新生成
python manage.py makemigrations

# 或使用merge
python manage.py makemigrations --merge
```

## 开发工具推荐

### IDE
- **PyCharm Professional** (Python)
- **VS Code** (全栈)
- **WebStorm** (前端)

### VS Code插件
- Python
- Django
- Volar (Vue 3)
- ESLint
- Prettier
- GitLens
- Docker

### 数据库工具
- **DBeaver** (免费)
- **Navicat** (付费)
- **MySQL Workbench** (官方)

### API测试工具
- **Postman**
- **Insomnia**
- **Swagger UI** (内置)

## 性能优化建议

### 后端优化

1. **数据库查询优化**
```python
# 使用select_related减少查询
agents = Agent.objects.select_related('workflow').all()

# 使用prefetch_related优化多对多
agents = Agent.objects.prefetch_related('documents').all()

# 只查询需要的字段
agents = Agent.objects.values('id', 'name').all()
```

2. **缓存使用**
```python
from django.core.cache import cache

# 缓存查询结果
def get_agent(agent_id):
    cache_key = f'agent_{agent_id}'
    agent = cache.get(cache_key)
    if not agent:
        agent = Agent.objects.get(id=agent_id)
        cache.set(cache_key, agent, 3600)
    return agent
```

3. **异步任务**
```python
# 使用Celery处理耗时任务
@shared_task
def process_document(document_id):
    # 文档处理逻辑
    pass
```

### 前端优化

1. **懒加载**
```typescript
// 路由懒加载
const AgentList = () => import('./views/AgentList.vue')
```

2. **组件缓存**
```vue
<keep-alive>
  <router-view />
</keep-alive>
```

## 调试技巧

### Django调试

```python
# 使用django-debug-toolbar
pip install django-debug-toolbar

# settings.py
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# 使用pdb调试
import pdb; pdb.set_trace()

# 使用logging
import logging
logger = logging.getLogger(__name__)
logger.info('Debug message')
```

### Vue调试

```typescript
// 使用Vue DevTools
// Chrome扩展: Vue.js devtools

// 使用console
console.log('Debug:', data)
console.table(list)

// 使用debugger
debugger;
```

## 下一步计划

### 第2周任务
1. 前端页面开发
   - 智能体列表页
   - 智能体创建/编辑页
   - 智能体对话页
   - 工作流编辑器

2. 前后端联调
   - API集成
   - 错误处理
   - 加载状态

### 第3周任务
1. 知识库功能完善
   - 向量化实现
   - 相似度搜索
   - RAG集成

2. 工作流引擎完善
   - DAG执行
   - 节点类型扩展
   - 错误处理

### 第4周任务
1. 用户认证
   - JWT认证
   - 权限管理
   - 用户管理

2. 生产部署
   - 性能优化
   - 监控告警
   - 备份策略

## 学习资源

### Django
- [Django官方文档](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django最佳实践](https://django-best-practices.readthedocs.io/)

### Vue 3
- [Vue 3官方文档](https://vuejs.org/)
- [Vue Router](https://router.vuejs.org/)
- [Pinia](https://pinia.vuejs.org/)

### Docker
- [Docker官方文档](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### AI/LLM
- [OpenAI API](https://platform.openai.com/docs/)
- [LangChain](https://python.langchain.com/)

## 联系与支持

如有问题，请：
1. 查看文档
2. 搜索已有Issue
3. 提交新Issue
4. 联系团队成员
