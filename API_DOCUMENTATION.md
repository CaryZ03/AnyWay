# AnyWay AI Agent Platform - API 接口文档

## 📋 目录

- [基础信息](#基础信息)
- [统一响应格式](#统一响应格式)
- [健康检查](#健康检查)
- [智能体管理 API](#智能体管理-api)
- [工作流管理 API](#工作流管理-api)
- [知识库管理 API](#知识库管理-api)
- [插件管理 API](#插件管理-api)
- [LLM 服务 API](#llm-服务-api)
- [调用示例](#调用示例)

---

## 基础信息

### Base URL

- **开发环境**: `http://localhost:8000`
- **生产环境**: `http://your-domain.com` 或 `http://your-server-ip:18080`

### API 版本

所有 API 接口使用 `/api/v1/` 前缀。

### 认证方式

当前版本**无需认证**，所有接口可直接访问。后续版本将支持 JWT Token 认证。

### 请求格式

- **Content-Type**: `application/json`（除文件上传接口外）
- **文件上传**: `multipart/form-data`

### 响应格式

所有 API 响应统一使用 JSON 格式，详见 [统一响应格式](#统一响应格式)。

---

## 统一响应格式

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
  "message": "错误信息描述",
  "data": null,
  "success": false
}
```

### HTTP 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 健康检查

### GET /health/

检查服务健康状态。

**请求示例**:
```bash
curl -X GET http://localhost:8000/health/
```

**响应示例**:
```json
{
  "status": "ok"
}
```

---

## 智能体管理 API

### 1. 获取智能体列表

**接口**: `GET /api/v1/agents/`

**描述**: 获取所有未删除的智能体列表（简化信息）。

**请求参数**: 无

**响应示例**:
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

---

### 2. 创建智能体

**接口**: `POST /api/v1/agents/`

**描述**: 创建新的智能体。

**请求体**:
```json
{
  "name": "客服助手",
  "description": "智能客服机器人",
  "system_prompt": "你是一个专业的客服助手，请友好、耐心地回答用户问题。",
  "user_prompt_template": "用户问题：{question}",
  "model_config": {
    "model": "doubao-seed-1-6-251015",
    "temperature": 0.7,
    "max_tokens": 2000
  },
  "workflow_id": null,
  "knowledge_base_ids": [],
  "plugin_ids": [],
  "status": "draft"
}
```

**字段说明**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 智能体名称 |
| description | string | 否 | 智能体描述 |
| system_prompt | string | 否 | 系统提示词 |
| user_prompt_template | string | 否 | 用户提示词模板 |
| model_config | object | 否 | 模型配置（JSON对象） |
| workflow_id | integer | 否 | 关联工作流ID |
| knowledge_base_ids | array | 否 | 关联知识库ID列表 |
| plugin_ids | array | 否 | 关联插件ID列表 |
| status | string | 否 | 状态：`draft`（草稿）或 `published`（已发布），默认 `draft` |

**model_config 字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| model | string | 模型名称，如 `doubao-seed-1-6-251015` |
| temperature | float | 温度参数（0-2），默认 0.7 |
| max_tokens | integer | 最大生成token数 |

**响应示例**:
```json
{
  "code": 201,
  "message": "智能体创建成功",
  "data": {
    "id": 1,
    "name": "客服助手",
    "description": "智能客服机器人",
    "system_prompt": "你是一个专业的客服助手...",
    "user_prompt_template": "用户问题：{question}",
    "model_config": {
      "model": "doubao-seed-1-6-251015",
      "temperature": 0.7,
      "max_tokens": 2000
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

---

### 3. 获取智能体详情

**接口**: `GET /api/v1/agents/{id}/`

**描述**: 根据ID获取智能体详细信息。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 智能体ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "获取智能体详情成功",
  "data": {
    "id": 1,
    "name": "客服助手",
    "description": "智能客服机器人",
    "system_prompt": "你是一个专业的客服助手...",
    "user_prompt_template": "用户问题：{question}",
    "model_config": {
      "model": "doubao-seed-1-6-251015",
      "temperature": 0.7
    },
    "workflow_id": null,
    "knowledge_base_ids": [1, 2],
    "plugin_ids": [1],
    "status": "published",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "success": true
}
```

---

### 4. 更新智能体

**接口**: `PUT /api/v1/agents/{id}/` 或 `PATCH /api/v1/agents/{id}/`

**描述**: 更新智能体信息。`PUT` 需要提供完整数据，`PATCH` 支持部分更新。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 智能体ID |

**请求体**（PATCH 示例，只更新部分字段）:
```json
{
  "description": "更新后的描述",
  "system_prompt": "更新后的系统提示词",
  "status": "published"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "智能体更新成功",
  "data": {
    "id": 1,
    "name": "客服助手",
    "description": "更新后的描述",
    "system_prompt": "更新后的系统提示词",
    "status": "published",
    ...
  },
  "success": true
}
```

---

### 5. 删除智能体

**接口**: `DELETE /api/v1/agents/{id}/`

**描述**: 逻辑删除智能体（不会真正删除数据）。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 智能体ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "智能体删除成功",
  "data": null,
  "success": true
}
```

---

### 6. 发布智能体

**接口**: `POST /api/v1/agents/{id}/publish/`

**描述**: 将智能体状态从草稿改为已发布。只有已发布的智能体才能进行对话。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 智能体ID |

**请求体**: 无

**响应示例**:
```json
{
  "code": 200,
  "message": "智能体发布成功",
  "data": {
    "id": 1,
    "name": "客服助手",
    "status": "published",
    ...
  },
  "success": true
}
```

**错误响应**（系统提示词为空）:
```json
{
  "code": 400,
  "message": "系统提示词不能为空",
  "data": null,
  "success": false
}
```

---

### 7. 测试智能体

**接口**: `POST /api/v1/agents/{id}/test/`

**描述**: 发送测试消息给智能体（不需要发布即可测试）。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 智能体ID |

**请求体**:
```json
{
  "message": "你好，请介绍一下自己",
  "context": {}
}
```

**字段说明**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| message | string | 是 | 用户消息 |
| context | object | 否 | 上下文信息（JSON对象） |

**响应示例**:
```json
{
  "code": 200,
  "message": "测试成功",
  "data": {
    "id": 1,
    "agent": 1,
    "user_message": "你好，请介绍一下自己",
    "assistant_message": "你好！我是一个AI助手...",
    "context": {},
    "created_at": "2024-01-01T00:00:00Z"
  },
  "success": true
}
```

---

### 8. 与智能体对话

**接口**: `POST /api/v1/agents/{id}/chat/`

**描述**: 与已发布的智能体进行对话。会自动加载历史对话上下文。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 智能体ID |

**请求体**:
```json
{
  "message": "今天天气怎么样？",
  "context": {}
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "对话成功",
  "data": {
    "id": 2,
    "agent": 1,
    "user_message": "今天天气怎么样？",
    "assistant_message": "抱歉，我无法获取实时天气信息...",
    "context": {},
    "created_at": "2024-01-01T00:00:01Z"
  },
  "success": true
}
```

**错误响应**（智能体未发布）:
```json
{
  "code": 400,
  "message": "智能体未发布，无法对话",
  "data": null,
  "success": false
}
```

---

### 9. 为智能体添加插件

**接口**: `POST /api/v1/agents/{id}/add_plugins/`

**描述**: 将一个或多个插件ID添加到智能体的 `plugin_ids` 列表中。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 智能体ID |

**请求体**:
```json
{
  "plugin_ids": [1, 2, 3]
}
```

或者单个插件ID:
```json
{
  "plugin_ids": 1
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "插件添加成功",
  "data": {
    "id": 1,
    "name": "客服助手",
    "plugin_ids": [1, 2, 3],
    ...
  },
  "success": true
}
```

---

### 10. 从智能体删除插件

**接口**: `POST /api/v1/agents/{id}/remove_plugins/`

**描述**: 将一个或多个插件ID从智能体的 `plugin_ids` 列表中移除。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 智能体ID |

**请求体**:
```json
{
  "plugin_ids": [2, 3]
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "插件删除成功",
  "data": {
    "id": 1,
    "name": "客服助手",
    "plugin_ids": [1],
    ...
  },
  "success": true
}
```

---

## 工作流管理 API

### 1. 获取工作流列表

**接口**: `GET /api/v1/workflows/`

**描述**: 获取所有未删除的工作流列表。

**请求参数**: 无

**响应示例**:
```json
{
  "code": 200,
  "message": "获取工作流列表成功",
  "data": [
    {
      "id": 1,
      "name": "数据处理工作流",
      "description": "处理用户输入数据",
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "success": true
}
```

---

### 2. 创建工作流

**接口**: `POST /api/v1/workflows/`

**描述**: 创建新的工作流。

**请求体**:
```json
{
  "name": "数据处理工作流",
  "description": "处理用户输入数据",
  "definition": {
    "nodes": [
      {
        "id": "node1",
        "type": "input",
        "data": { "label": "输入节点" }
      },
      {
        "id": "node2",
        "type": "process",
        "data": { "label": "处理节点" }
      }
    ],
    "edges": [
      {
        "id": "edge1",
        "source": "node1",
        "target": "node2"
      }
    ]
  },
  "status": "active"
}
```

**字段说明**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 工作流名称 |
| description | string | 否 | 工作流描述 |
| definition | object | 是 | 工作流定义（JSON对象），必须包含 `nodes` 和 `edges` 字段 |
| status | string | 否 | 状态：`active`（激活）或 `inactive`（未激活） |

**响应示例**:
```json
{
  "code": 201,
  "message": "工作流创建成功",
  "data": {
    "id": 1,
    "name": "数据处理工作流",
    "description": "处理用户输入数据",
    "definition": { ... },
    "status": "active",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "success": true
}
```

---

### 3. 获取工作流详情

**接口**: `GET /api/v1/workflows/{id}/`

**描述**: 根据ID获取工作流详细信息。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 工作流ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "获取工作流详情成功",
  "data": {
    "id": 1,
    "name": "数据处理工作流",
    "description": "处理用户输入数据",
    "definition": {
      "nodes": [ ... ],
      "edges": [ ... ]
    },
    "status": "active",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "success": true
}
```

---

### 4. 更新工作流

**接口**: `PUT /api/v1/workflows/{id}/` 或 `PATCH /api/v1/workflows/{id}/`

**描述**: 更新工作流信息。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 工作流ID |

**请求体**: 同创建工作流

**响应示例**:
```json
{
  "code": 200,
  "message": "工作流更新成功",
  "data": { ... },
  "success": true
}
```

---

### 5. 删除工作流

**接口**: `DELETE /api/v1/workflows/{id}/`

**描述**: 逻辑删除工作流。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 工作流ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "工作流删除成功",
  "data": null,
  "success": true
}
```

---

### 6. 执行工作流

**接口**: `POST /api/v1/workflows/{id}/execute/`

**描述**: 执行指定的工作流。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 工作流ID |

**请求体**:
```json
{
  "input_data": {
    "key1": "value1",
    "key2": "value2"
  }
}
```

**字段说明**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| input_data | object | 是 | 输入数据（JSON对象） |

**响应示例**:
```json
{
  "code": 200,
  "message": "工作流执行成功",
  "data": {
    "id": 1,
    "workflow": 1,
    "input_data": { ... },
    "output_data": { ... },
    "status": "completed",
    "node_status": { ... },
    "error_message": null,
    "started_at": "2024-01-01T00:00:00Z",
    "completed_at": "2024-01-01T00:00:01Z",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "success": true
}
```

**错误响应**:
```json
{
  "code": 400,
  "message": "工作流执行失败: 错误信息",
  "data": null,
  "success": false
}
```

---

### 7. 获取执行历史

**接口**: `GET /api/v1/workflows/{id}/executions/`

**描述**: 获取工作流的执行历史记录。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 工作流ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "获取执行历史成功",
  "data": [
    {
      "id": 1,
      "workflow": 1,
      "input_data": { ... },
      "output_data": { ... },
      "status": "completed",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "success": true
}
```

---

## 知识库管理 API

### 1. 获取知识库列表

**接口**: `GET /api/v1/knowledge/`

**描述**: 获取所有未删除的知识库列表。

**请求参数**: 无

**响应示例**:
```json
{
  "code": 200,
  "message": "获取知识库列表成功",
  "data": [
    {
      "id": 1,
      "name": "产品文档库",
      "description": "产品相关文档",
      "embedding_model": "text-embedding-ada-002",
      "document_count": 5,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "success": true
}
```

---

### 2. 创建知识库

**接口**: `POST /api/v1/knowledge/`

**描述**: 创建新的知识库。

**请求体**:
```json
{
  "name": "产品文档库",
  "description": "产品相关文档",
  "embedding_model": "text-embedding-ada-002"
}
```

**字段说明**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 知识库名称 |
| description | string | 否 | 知识库描述 |
| embedding_model | string | 否 | 嵌入模型名称 |

**响应示例**:
```json
{
  "code": 201,
  "message": "知识库创建成功",
  "data": {
    "id": 1,
    "name": "产品文档库",
    "description": "产品相关文档",
    "embedding_model": "text-embedding-ada-002",
    "document_count": 0,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "success": true
}
```

---

### 3. 获取知识库详情

**接口**: `GET /api/v1/knowledge/{id}/`

**描述**: 根据ID获取知识库详细信息。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 知识库ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "获取知识库详情成功",
  "data": {
    "id": 1,
    "name": "产品文档库",
    "description": "产品相关文档",
    "embedding_model": "text-embedding-ada-002",
    "document_count": 5,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "success": true
}
```

---

### 4. 更新知识库

**接口**: `PUT /api/v1/knowledge/{id}/` 或 `PATCH /api/v1/knowledge/{id}/`

**描述**: 更新知识库信息。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 知识库ID |

**请求体**: 同创建知识库

**响应示例**:
```json
{
  "code": 200,
  "message": "知识库更新成功",
  "data": { ... },
  "success": true
}
```

---

### 5. 删除知识库

**接口**: `DELETE /api/v1/knowledge/{id}/`

**描述**: 逻辑删除知识库。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 知识库ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "知识库删除成功",
  "data": null,
  "success": true
}
```

---

### 6. 上传文档

**接口**: `POST /api/v1/knowledge/{id}/upload/`

**描述**: 上传文档到知识库。支持的文件类型：`.txt`、`.md`、`.markdown`，最大文件大小：10MB。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 知识库ID |

**请求格式**: `multipart/form-data`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | file | 是 | 文档文件 |

**响应示例**:
```json
{
  "code": 201,
  "message": "文档上传成功，正在处理中",
  "data": {
    "id": 1,
    "knowledge_base": 1,
    "filename": "product_guide.md",
    "file_type": "md",
    "file_size": 10240,
    "status": "pending",
    "error_message": null,
    "chunk_count": 0,
    "uploaded_at": "2024-01-01T00:00:00Z",
    "processed_at": null
  },
  "success": true
}
```

**错误响应**（文件类型不支持）:
```json
{
  "code": 400,
  "message": "不支持的文件类型。仅支持: .txt, .md, .markdown",
  "data": null,
  "success": false
}
```

---

### 7. 获取文档列表

**接口**: `GET /api/v1/knowledge/{id}/documents/`

**描述**: 获取知识库中的所有文档。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 知识库ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "获取文档列表成功",
  "data": [
    {
      "id": 1,
      "knowledge_base": 1,
      "filename": "product_guide.md",
      "file_type": "md",
      "file_size": 10240,
      "status": "processed",
      "chunk_count": 10,
      "uploaded_at": "2024-01-01T00:00:00Z",
      "processed_at": "2024-01-01T00:00:05Z"
    }
  ],
  "success": true
}
```

---

### 8. 搜索知识库

**接口**: `POST /api/v1/knowledge/{id}/search/`

**描述**: 在知识库中搜索相关内容（向量搜索）。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 知识库ID |

**请求体**:
```json
{
  "query": "产品功能",
  "top_k": 5
}
```

**字段说明**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | 是 | 搜索查询 |
| top_k | integer | 否 | 返回结果数量（1-20），默认 5 |

**响应示例**:
```json
{
  "code": 200,
  "message": "搜索完成",
  "data": [
    {
      "id": 1,
      "content": "产品功能包括...",
      "score": 0.95
    }
  ],
  "success": true
}
```

---

## 插件管理 API

### 1. 获取插件列表

**接口**: `GET /api/v1/plugins/`

**描述**: 获取所有未删除的插件列表。

**请求参数**: 无

**响应示例**:
```json
{
  "code": 200,
  "message": "获取插件列表成功",
  "data": [
    {
      "id": 1,
      "name": "天气查询插件",
      "description": "查询天气信息",
      "status": "enabled",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "success": true
}
```

---

### 2. 注册插件

**接口**: `POST /api/v1/plugins/`

**描述**: 注册新的插件（通过 OpenAPI 规范）。

**请求体**:
```json
{
  "openapi_spec": {
    "openapi": "3.0.0",
    "info": {
      "title": "天气查询插件",
      "description": "查询天气信息的插件",
      "version": "1.0.0"
    },
    "servers": [
      {
        "url": "https://api.weather.com"
      }
    ],
    "paths": {
      "/weather": {
        "get": {
          "summary": "查询天气",
          "parameters": [
            {
              "name": "city",
              "in": "query",
              "required": true,
              "schema": {
                "type": "string"
              }
            }
          ],
          "responses": {
            "200": {
              "description": "成功",
              "content": {
                "application/json": {
                  "schema": {
                    "type": "object"
                  }
                }
              }
            }
          }
        }
      }
    }
  },
  "status": "enabled"
}
```

**字段说明**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| openapi_spec | object | 是 | OpenAPI 3.0 规范（JSON对象），必须包含 `openapi`、`info`、`servers`、`paths` 字段 |
| status | string | 否 | 状态：`enabled`（启用）或 `disabled`（禁用），默认 `enabled` |

**响应示例**:
```json
{
  "code": 201,
  "message": "插件注册成功",
  "data": {
    "id": 1,
    "name": "天气查询插件",
    "description": "查询天气信息的插件",
    "base_url": "https://api.weather.com",
    "openapi_spec": { ... },
    "auth_config": {},
    "status": "enabled",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "success": true
}
```

---

### 3. 获取插件详情

**接口**: `GET /api/v1/plugins/{id}/`

**描述**: 根据ID获取插件详细信息。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 插件ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "获取插件详情成功",
  "data": {
    "id": 1,
    "name": "天气查询插件",
    "description": "查询天气信息的插件",
    "base_url": "https://api.weather.com",
    "openapi_spec": { ... },
    "auth_config": {},
    "status": "enabled",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "success": true
}
```

---

### 4. 更新插件

**接口**: `PUT /api/v1/plugins/{id}/` 或 `PATCH /api/v1/plugins/{id}/`

**描述**: 更新插件信息。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 插件ID |

**请求体**: 同注册插件

**响应示例**:
```json
{
  "code": 200,
  "message": "插件更新成功",
  "data": { ... },
  "success": true
}
```

---

### 5. 删除插件

**接口**: `DELETE /api/v1/plugins/{id}/`

**描述**: 逻辑删除插件。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 插件ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "插件删除成功",
  "data": null,
  "success": true
}
```

---

### 6. 启用插件

**接口**: `POST /api/v1/plugins/{id}/enable/`

**描述**: 启用指定的插件。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 插件ID |

**请求体**: 无

**响应示例**:
```json
{
  "code": 200,
  "message": "插件已启用",
  "data": {
    "id": 1,
    "name": "天气查询插件",
    "status": "enabled",
    ...
  },
  "success": true
}
```

---

### 7. 禁用插件

**接口**: `POST /api/v1/plugins/{id}/disable/`

**描述**: 禁用指定的插件。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 插件ID |

**请求体**: 无

**响应示例**:
```json
{
  "code": 200,
  "message": "插件已禁用",
  "data": {
    "id": 1,
    "name": "天气查询插件",
    "status": "disabled",
    ...
  },
  "success": true
}
```

---

## LLM 服务 API

### 1. LLM 聊天

**接口**: `POST /api/v1/llm/chat/`

**描述**: 直接调用 LLM 进行对话（不通过智能体）。

**请求体**:
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

**字段说明**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| messages | array | 是 | 消息列表，每个消息包含 `role`（`system`、`user`、`assistant`）和 `content` |
| model | string | 否 | 模型名称，默认 `gpt-3.5-turbo` |
| temperature | float | 否 | 温度参数（0-2），默认 0.7 |

**响应示例**:
```json
{
  "code": 200,
  "message": "聊天成功",
  "data": {
    "reply": "你好！我是AI助手，有什么可以帮助你的吗？"
  },
  "success": true
}
```

---

## 调用示例

### cURL 示例

#### 1. 获取智能体列表

```bash
curl -X GET http://localhost:8000/api/v1/agents/
```

#### 2. 创建智能体

```bash
curl -X POST http://localhost:8000/api/v1/agents/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "客服助手",
    "description": "智能客服机器人",
    "system_prompt": "你是一个专业的客服助手",
    "model_config": {
      "model": "doubao-seed-1-6-251015",
      "temperature": 0.7
    },
    "status": "draft"
  }'
```

#### 3. 与智能体对话

```bash
curl -X POST http://localhost:8000/api/v1/agents/1/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，请介绍一下自己"
  }'
```

#### 4. 上传文档

```bash
curl -X POST http://localhost:8000/api/v1/knowledge/1/upload/ \
  -F "file=@document.txt"
```

---

### Python 示例

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. 获取智能体列表
response = requests.get(f"{BASE_URL}/agents/")
print(response.json())

# 2. 创建智能体
agent_data = {
    "name": "客服助手",
    "description": "智能客服机器人",
    "system_prompt": "你是一个专业的客服助手",
    "model_config": {
        "model": "doubao-seed-1-6-251015",
        "temperature": 0.7
    },
    "status": "draft"
}
response = requests.post(f"{BASE_URL}/agents/", json=agent_data)
print(response.json())

# 3. 与智能体对话
chat_data = {
    "message": "你好，请介绍一下自己"
}
response = requests.post(f"{BASE_URL}/agents/1/chat/", json=chat_data)
print(response.json())

# 4. 上传文档
with open("document.txt", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{BASE_URL}/knowledge/1/upload/", files=files)
    print(response.json())
```

---

### JavaScript (Fetch) 示例

```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// 1. 获取智能体列表
async function getAgents() {
  const response = await fetch(`${BASE_URL}/agents/`);
  const data = await response.json();
  console.log(data);
}

// 2. 创建智能体
async function createAgent() {
  const agentData = {
    name: "客服助手",
    description: "智能客服机器人",
    system_prompt: "你是一个专业的客服助手",
    model_config: {
      model: "doubao-seed-1-6-251015",
      temperature: 0.7
    },
    status: "draft"
  };
  
  const response = await fetch(`${BASE_URL}/agents/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(agentData)
  });
  
  const data = await response.json();
  console.log(data);
}

// 3. 与智能体对话
async function chatWithAgent(agentId, message) {
  const response = await fetch(`${BASE_URL}/agents/${agentId}/chat/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ message })
  });
  
  const data = await response.json();
  console.log(data);
}

// 4. 上传文档
async function uploadDocument(knowledgeBaseId, file) {
  const formData = new FormData();
  formData.append("file", file);
  
  const response = await fetch(`${BASE_URL}/knowledge/${knowledgeBaseId}/upload/`, {
    method: "POST",
    body: formData
  });
  
  const data = await response.json();
  console.log(data);
}
```

---

## 在线 API 文档

系统提供了 Swagger UI 和 ReDoc 两种在线 API 文档：

- **Swagger UI**: `http://localhost:8000/swagger/`
- **ReDoc**: `http://localhost:8000/redoc/`
- **OpenAPI JSON**: `http://localhost:8000/swagger.json`

在 Swagger UI 中可以：
- 查看所有接口的详细说明
- 直接在浏览器中测试接口
- 查看请求和响应的数据结构
- 下载 OpenAPI 规范文件

---

## 注意事项

1. **模型配置**: 当前系统主要使用火山引擎（豆包）模型，模型名称如 `doubao-seed-1-6-251015`。如果配置了 OpenAI API Key，也可以使用 OpenAI 模型。

2. **文件上传限制**: 
   - 知识库文档仅支持 `.txt`、`.md`、`.markdown` 格式
   - 最大文件大小为 10MB

3. **智能体状态**: 
   - `draft`（草稿）：可以编辑和测试，但不能公开对话
   - `published`（已发布）：可以公开对话

4. **插件系统**: 插件需要提供完整的 OpenAPI 3.0 规范，系统会自动解析并生成工具函数供智能体调用。

5. **工作流定义**: 工作流的 `definition` 字段必须包含 `nodes` 和 `edges` 字段，且必须是有向无环图（DAG）。

6. **错误处理**: 所有接口都遵循统一的错误响应格式，请根据 `code` 和 `message` 字段处理错误。

---

## 更新日志

- **v1.0.0** (2024-01-01): 初始版本，包含智能体、工作流、知识库、插件、LLM 等核心功能 API。

---

## 技术支持

如有问题或建议，请访问项目仓库：https://github.com/CaryZ03/AnyWay


