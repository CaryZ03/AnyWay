# API接口测试指南

## 📋 完整接口测试清单

### 前置条件
- 确保后端服务运行: `python manage.py runserver`
- 确保数据库服务运行: `docker-compose ps`

---

## 1️⃣ 健康检查接口

### GET /health/

**Postman配置:**
```
Method: GET
URL: http://localhost:8000/health/
```

**预期响应:**
```json
{
  "status": "ok"
}
```

---

## 2️⃣ 智能体管理接口

### 2.1 获取智能体列表

**Postman配置:**
```
Method: GET
URL: http://localhost:8000/api/v1/agents/
```

**预期响应:**
```json
{
  "code": 200,
  "message": "获取智能体列表成功",
  "data": [],
  "success": true
}
```

### 2.2 创建智能体

**Postman配置:**
```
Method: POST
URL: http://localhost:8000/api/v1/agents/
Headers:
  Content-Type: application/json
Body (raw JSON):
```
```json
{
  "name": "测试智能体",
  "description": "这是一个测试智能体",
  "system_prompt": "你是一个友好的AI助手",
  "model_config": {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7
  }
}
```

**预期响应:**
```json
{
  "code": 201,
  "message": "智能体创建成功",
  "data": {
    "id": 1,
    "name": "测试智能体",
    ...
  },
  "success": true
}
```

### 2.3 获取智能体详情

**Postman配置:**
```
Method: GET
URL: http://localhost:8000/api/v1/agents/1/
```
*注意: 将 `1` 替换为实际的智能体ID*

### 2.4 更新智能体

**Postman配置:**
```
Method: PUT 或 PATCH
URL: http://localhost:8000/api/v1/agents/1/
Headers:
  Content-Type: application/json
Body (raw JSON):
```
```json
{
  "description": "更新后的描述",
  "system_prompt": "你是一个更加友好的AI助手"
}
```

### 2.5 发布智能体

**Postman配置:**
```
Method: POST
URL: http://localhost:8000/api/v1/agents/1/publish/
Headers:
  Content-Type: application/json
```

### 2.6 测试智能体对话

**Postman配置:**
```
Method: POST
URL: http://localhost:8000/api/v1/agents/1/test/
Headers:
  Content-Type: application/json
Body (raw JSON):
```
```json
{
  "message": "你好，请介绍一下自己",
  "context": {}
}
```

### 2.7 与智能体对话（需先发布）

**Postman配置:**
```
Method: POST
URL: http://localhost:8000/api/v1/agents/1/chat/
Headers:
  Content-Type: application/json
Body (raw JSON):
```
```json
{
  "message": "今天天气怎么样？",
  "context": {}
}
```

### 2.8 删除智能体

**Postman配置:**
```
Method: DELETE
URL: http://localhost:8000/api/v1/agents/1/
```

---

## 3️⃣ 工作流管理接口

### 3.1 获取工作流列表

**Postman配置:**
```
Method: GET
URL: http://localhost:8000/api/v1/workflows/
```

### 3.2 创建工作流

**Postman配置:**
```
Method: POST
URL: http://localhost:8000/api/v1/workflows/
Headers:
  Content-Type: application/json
Body (raw JSON):
```
```json
{
  "name": "测试工作流",
  "description": "这是一个测试工作流",
  "definition": {
    "nodes": [
      {
        "id": "node1",
        "type": "start",
        "name": "开始节点"
      },
      {
        "id": "node2",
        "type": "llm",
        "name": "LLM节点",
        "config": {
          "model": "gpt-3.5-turbo"
        }
      }
    ],
    "edges": [
      {
        "source": "node1",
        "target": "node2"
      }
    ]
  }
}
```

### 3.3 获取工作流详情

**Postman配置:**
```
Method: GET
URL: http://localhost:8000/api/v1/workflows/1/
```

### 3.4 更新工作流

**Postman配置:**
```
Method: PUT 或 PATCH
URL: http://localhost:8000/api/v1/workflows/1/
Headers:
  Content-Type: application/json
Body (raw JSON):
```
```json
{
  "description": "更新后的工作流描述"
}
```

### 3.5 执行工作流

**Postman配置:**
```
Method: POST
URL: http://localhost:8000/api/v1/workflows/1/execute/
Headers:
  Content-Type: application/json
Body (raw JSON):
```
```json
{
  "input_data": {
    "message": "测试输入"
  }
}
```

### 3.6 删除工作流

**Postman配置:**
```
Method: DELETE
URL: http://localhost:8000/api/v1/workflows/1/
```

---

## 4️⃣ 知识库管理接口

### 4.1 获取知识库列表

**Postman配置:**
```
Method: GET
URL: http://localhost:8000/api/v1/knowledge/
```

### 4.2 创建知识库

**Postman配置:**
```
Method: POST
URL: http://localhost:8000/api/v1/knowledge/
Headers:
  Content-Type: application/json
Body (raw JSON):
```
```json
{
  "name": "测试知识库",
  "description": "这是一个测试知识库",
  "embedding_model": "text-embedding-ada-002",
  "chunk_size": 500,
  "chunk_overlap": 50
}
```

### 4.3 获取知识库详情

**Postman配置:**
```
Method: GET
URL: http://localhost:8000/api/v1/knowledge/1/
```

### 4.4 更新知识库

**Postman配置:**
```
Method: PUT 或 PATCH
URL: http://localhost:8000/api/v1/knowledge/1/
Headers:
  Content-Type: application/json
Body (raw JSON):
```
```json
{
  "description": "更新后的知识库描述"
}
```

### 4.5 上传文档到知识库

**Postman配置:**
```
Method: POST
URL: http://localhost:8000/api/v1/knowledge/1/upload/
Headers:
  (不设置Content-Type，让Postman自动设置)
Body (form-data):
  Key: file
  Type: File
  Value: 选择一个文档文件
```

### 4.6 删除知识库

**Postman配置:**
```
Method: DELETE
URL: http://localhost:8000/api/v1/knowledge/1/
```

---

## 5️⃣ 插件管理接口

### 5.1 获取插件列表

**Postman配置:**
```
Method: GET
URL: http://localhost:8000/api/v1/plugins/
```

### 5.2 注册插件

**Postman配置:**
```
Method: POST
URL: http://localhost:8000/api/v1/plugins/
Headers:
  Content-Type: application/json
Body (raw JSON):
```
```json
{
  "name": "测试插件",
  "description": "这是一个测试插件",
  "base_url": "https://api.example.com",
  "openapi_spec": {
    "openapi": "3.0.0",
    "info": {
      "title": "Test Plugin API",
      "version": "1.0.0"
    },
    "paths": {
      "/test": {
        "get": {
          "summary": "Test endpoint",
          "responses": {
            "200": {
              "description": "Success"
            }
          }
        }
      }
    }
  },
  "auth_config": {}
}
```

### 5.3 获取插件详情

**Postman配置:**
```
Method: GET
URL: http://localhost:8000/api/v1/plugins/1/
```

### 5.4 更新插件

**Postman配置:**
```
Method: PUT 或 PATCH
URL: http://localhost:8000/api/v1/plugins/1/
Headers:
  Content-Type: application/json
Body (raw JSON):
```
```json
{
  "description": "更新后的插件描述"
}
```

### 5.5 启用插件

**Postman配置:**
```
Method: POST
URL: http://localhost:8000/api/v1/plugins/1/enable/
Headers:
  Content-Type: application/json
```

### 5.6 禁用插件

**Postman配置:**
```
Method: POST
URL: http://localhost:8000/api/v1/plugins/1/disable/
Headers:
  Content-Type: application/json
```

### 5.7 删除插件

**Postman配置:**
```
Method: DELETE
URL: http://localhost:8000/api/v1/plugins/1/
```

---

## 6️⃣ LLM服务接口

### 6.1 LLM聊天

**Postman配置:**
```
Method: POST
URL: http://localhost:8000/api/v1/llm/chat/
Headers:
  Content-Type: application/json
Body (raw JSON):
```
```json
{
  "messages": [
    {
      "role": "system",
      "content": "你是一个友好的AI助手"
    },
    {
      "role": "user",
      "content": "你好，请介绍一下自己"
    }
  ],
  "model": "gpt-3.5-turbo",
  "temperature": 0.7
}
```

**注意:** 需要在 `backend/.env` 中配置有效的 `OPENAI_API_KEY`

---

## 📊 测试结果记录表

| 接口 | 方法 | 端点 | 状态 | 备注 |
|------|------|------|------|------|
| 健康检查 | GET | /health/ | ⬜ |  |
| 获取智能体列表 | GET | /api/v1/agents/ | ⬜ |  |
| 创建智能体 | POST | /api/v1/agents/ | ⬜ |  |
| 获取智能体详情 | GET | /api/v1/agents/{id}/ | ⬜ |  |
| 更新智能体 | PUT/PATCH | /api/v1/agents/{id}/ | ⬜ |  |
| 发布智能体 | POST | /api/v1/agents/{id}/publish/ | ⬜ |  |
| 测试智能体 | POST | /api/v1/agents/{id}/test/ | ⬜ |  |
| 智能体对话 | POST | /api/v1/agents/{id}/chat/ | ⬜ |  |
| 删除智能体 | DELETE | /api/v1/agents/{id}/ | ⬜ |  |
| 获取工作流列表 | GET | /api/v1/workflows/ | ⬜ |  |
| 创建工作流 | POST | /api/v1/workflows/ | ⬜ |  |
| 执行工作流 | POST | /api/v1/workflows/{id}/execute/ | ⬜ |  |
| 获取知识库列表 | GET | /api/v1/knowledge/ | ⬜ |  |
| 创建知识库 | POST | /api/v1/knowledge/ | ⬜ |  |
| 上传文档 | POST | /api/v1/knowledge/{id}/upload/ | ⬜ |  |
| 获取插件列表 | GET | /api/v1/plugins/ | ⬜ |  |
| 注册插件 | POST | /api/v1/plugins/ | ⬜ |  |
| 启用插件 | POST | /api/v1/plugins/{id}/enable/ | ⬜ |  |
| LLM聊天 | POST | /api/v1/llm/chat/ | ⬜ |  |

---

## 🔧 快速测试命令（PowerShell）

### 测试健康检查
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health/" -Method Get
```

### 测试获取智能体列表
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/agents/" -Method Get
```

### 测试创建智能体
```powershell
$body = @{
    name = "测试智能体"
    description = "测试"
    system_prompt = "你是AI助手"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/agents/" -Method Post -Body $body -ContentType "application/json"
```

---

## 📚 在线API文档

访问 Swagger UI 查看完整的交互式API文档：
```
http://localhost:8000/swagger/
```

在Swagger中可以：
- 查看所有接口的详细说明
- 直接在浏览器中测试接口
- 查看请求和响应的数据结构
- 下载OpenAPI规范文件

---

## ⚠️ 常见问题

### 1. 连接被拒绝
- 检查后端服务是否运行: `python manage.py runserver`
- 检查端口是否正确: 默认8000

### 2. 404 Not Found
- 检查URL是否正确
- 确保URL末尾有斜杠 `/`

### 3. 500 Internal Server Error
- 查看后端日志
- 检查数据库连接
- 确保已执行数据库迁移

### 4. CORS错误
- 检查 `backend/.env` 中的 `CORS_ALLOWED_ORIGINS` 配置

---

**最后更新:** 2025-11-24
