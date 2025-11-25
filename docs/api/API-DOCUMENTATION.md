# API文档

## 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **认证方式**: 暂无（后续将添加JWT认证）
- **响应格式**: JSON

## 统一响应格式

所有API响应遵循统一格式：

### 成功响应
```json
{
  "code": 200,
  "message": "操作成功",
  "data": { ... },
  "success": true
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "错误信息",
  "data": null,
  "success": false
}
```

## 智能体管理 API

### 1. 获取智能体列表

**请求**
```
GET /api/v1/agents/
```

**响应**
```json
{
  "code": 200,
  "message": "获取智能体列表成功",
  "data": [
    {
      "id": 1,
      "name": "客服助手",
      "description": "智能客服机器人",
      "status": "published",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "success": true
}
```

### 2. 创建智能体

**请求**
```
POST /api/v1/agents/
Content-Type: application/json
```

**请求体**
```json
{
  "name": "客服助手",
  "description": "智能客服机器人",
  "system_prompt": "你是一个专业的客服助手",
  "user_prompt_template": "用户问题：{question}",
  "model_config": {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7
  },
  "status": "draft"
}
```

**响应**
```json
{
  "code": 201,
  "message": "智能体创建成功",
  "data": {
    "id": 1,
    "name": "客服助手",
    "description": "智能客服机器人",
    "system_prompt": "你是一个专业的客服助手",
    "user_prompt_template": "用户问题：{question}",
    "model_config": {
      "model": "gpt-3.5-turbo",
      "temperature": 0.7
    },
    "workflow_id": null,
    "knowledge_base_ids": [],
    "plugin_ids": [],
    "status": "draft",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "success": true
}
```

### 3. 获取智能体详情

**请求**
```
GET /api/v1/agents/{id}/
```

### 4. 更新智能体

**请求**
```
PUT /api/v1/agents/{id}/
Content-Type: application/json
```

**请求体**（部分更新）
```json
{
  "name": "新名称",
  "description": "新描述"
}
```

### 5. 删除智能体

**请求**
```
DELETE /api/v1/agents/{id}/
```

**响应**
```json
{
  "code": 200,
  "message": "智能体删除成功",
  "data": null,
  "success": true
}
```

### 6. 发布智能体

**请求**
```
POST /api/v1/agents/{id}/publish/
```

**响应**
```json
{
  "code": 200,
  "message": "智能体发布成功",
  "data": { ... },
  "success": true
}
```

### 7. 测试智能体

**请求**
```
POST /api/v1/agents/{id}/test/
Content-Type: application/json
```

**请求体**
```json
{
  "message": "你好，请介绍一下自己",
  "context": {}
}
```

**响应**
```json
{
  "code": 200,
  "message": "测试成功",
  "data": {
    "id": 1,
    "agent": 1,
    "user_message": "你好，请介绍一下自己",
    "assistant_message": "你好！我是客服助手...",
    "context": {},
    "created_at": "2024-01-01T00:00:00Z"
  },
  "success": true
}
```

### 8. 与智能体对话

**请求**
```
POST /api/v1/agents/{id}/chat/
Content-Type: application/json
```

**请求体**
```json
{
  "message": "我想咨询一个问题",
  "context": {
    "session_id": "xxx"
  }
}
```

## 工作流管理 API

### 1. 获取工作流列表

**请求**
```
GET /api/v1/workflows/
```

### 2. 创建工作流

**请求**
```
POST /api/v1/workflows/
Content-Type: application/json
```

**请求体**
```json
{
  "name": "客服工作流",
  "description": "客服处理流程",
  "definition": {
    "nodes": [
      {
        "id": "start",
        "type": "start",
        "config": {}
      },
      {
        "id": "llm",
        "type": "llm",
        "config": {
          "model": "gpt-3.5-turbo"
        }
      },
      {
        "id": "end",
        "type": "end",
        "config": {}
      }
    ],
    "edges": [
      {
        "source": "start",
        "target": "llm"
      },
      {
        "source": "llm",
        "target": "end"
      }
    ]
  },
  "status": "draft"
}
```

### 3. 执行工作流

**请求**
```
POST /api/v1/workflows/{id}/execute/
Content-Type: application/json
```

**请求体**
```json
{
  "input_data": {
    "question": "什么是AI？"
  }
}
```

**响应**
```json
{
  "code": 200,
  "message": "工作流执行成功",
  "data": {
    "id": 1,
    "workflow": 1,
    "input_data": {
      "question": "什么是AI？"
    },
    "output_data": {
      "result": "AI是人工智能..."
    },
    "status": "completed",
    "node_status": {
      "start": {
        "status": "completed"
      },
      "llm": {
        "status": "completed",
        "output": "..."
      },
      "end": {
        "status": "completed"
      }
    },
    "started_at": "2024-01-01T00:00:00Z",
    "completed_at": "2024-01-01T00:00:05Z",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "success": true
}
```

### 4. 获取执行历史

**请求**
```
GET /api/v1/workflows/{id}/executions/
```

## 知识库管理 API

### 1. 获取知识库列表

**请求**
```
GET /api/v1/knowledge/
```

### 2. 创建知识库

**请求**
```
POST /api/v1/knowledge/
Content-Type: application/json
```

**请求体**
```json
{
  "name": "产品知识库",
  "description": "产品相关文档",
  "embedding_model": "text-embedding-ada-002"
}
```

### 3. 上传文档

**请求**
```
POST /api/v1/knowledge/{id}/upload/
Content-Type: multipart/form-data
```

**请求体**
```
file: [文件]
```

**响应**
```json
{
  "code": 201,
  "message": "文档上传成功，正在处理中",
  "data": {
    "id": 1,
    "knowledge_base": 1,
    "filename": "product.txt",
    "file_type": "txt",
    "file_size": 1024,
    "status": "pending",
    "chunk_count": 0,
    "uploaded_at": "2024-01-01T00:00:00Z"
  },
  "success": true
}
```

### 4. 获取文档列表

**请求**
```
GET /api/v1/knowledge/{id}/documents/
```

### 5. 搜索知识库

**请求**
```
POST /api/v1/knowledge/{id}/search/
Content-Type: application/json
```

**请求体**
```json
{
  "query": "产品功能介绍",
  "top_k": 5
}
```

## 插件管理 API

### 1. 获取插件列表

**请求**
```
GET /api/v1/plugins/
```

### 2. 注册插件

**请求**
```
POST /api/v1/plugins/
Content-Type: application/json
```

**请求体**
```json
{
  "name": "天气查询插件",
  "description": "查询天气信息",
  "base_url": "https://api.weather.com",
  "openapi_spec": {
    "openapi": "3.0.0",
    "info": {
      "title": "Weather API",
      "version": "1.0.0"
    },
    "paths": {
      "/weather": {
        "get": {
          "summary": "获取天气",
          "parameters": [
            {
              "name": "city",
              "in": "query",
              "required": true,
              "schema": {
                "type": "string"
              }
            }
          ]
        }
      }
    }
  },
  "auth_config": {
    "type": "api_key",
    "api_key": "your-api-key"
  },
  "status": "enabled"
}
```

### 3. 启用插件

**请求**
```
POST /api/v1/plugins/{id}/enable/
```

### 4. 禁用插件

**请求**
```
POST /api/v1/plugins/{id}/disable/
```

## LLM服务 API

### 1. LLM聊天

**请求**
```
POST /api/v1/llm/chat/
Content-Type: application/json
```

**请求体**
```json
{
  "messages": [
    {
      "role": "system",
      "content": "你是一个AI助手"
    },
    {
      "role": "user",
      "content": "你好"
    }
  ],
  "model": "gpt-3.5-turbo",
  "temperature": 0.7
}
```

**响应**
```json
{
  "code": 200,
  "message": "聊天成功",
  "data": {
    "reply": "你好！有什么我可以帮助你的吗？"
  },
  "success": true
}
```

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 在线文档

启动服务后访问：
- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/
