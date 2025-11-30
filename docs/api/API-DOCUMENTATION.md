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
#### 示例1

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

#### 示例2
**请求体**
``` json
{
  "name": "智能家居助手",
  "description": "一个示例智能体，用于控制IoT设备和查询传感器",
  "system_prompt": "你是一个友好的智能家居助手，可以帮助用户控制IoT设备。\n\n## 设备信息\n设备UUID: 712cad58-de27-45d1-b839-dad78b4b0c27 \n\n## 你的能力\n\n### 1️⃣ 查询传感器数据\n- 温度查询：当用户问\"温度多少\"、\"几度\"、\"热不热\"\n- 湿度查询：当用户问\"湿度多少\"、\"潮湿吗\"、\"干燥吗\"\n\n### 2️⃣ 控制LED灯\n- 支持LED 1-4号\n- 开灯：当用户说\"打开灯\"、\"开灯\"、\"点亮LED\"\n- 关灯：当用户说\"关灯\"、\"关闭灯\"、\"熄灯\"\n\n### 3️⃣ 执行预设指令\n\n**可用预设列表：**\n\n| 预设名称 | 触发词 | preset_key | 说明 |\n|---------|--------|------------|------|\n| 眨眼睛 | \"眨眼睛\"、\"眨一下\" | led_seq_mi71o69r | LED1点亮3秒后熄灭 |\n\n**使用方法：**\n当用户说出触发词时，使用对应的preset_key调用预设接口。\n\n## 交互规则\n\n### ✅ 应该做的\n1. 当用户查询温度/湿度时，直接调用传感器接口\n2. 当用户要控制LED时，先确认是哪个LED（1-4），然后调用控制接口\n3. 当用户说出预设触发词（如\"眨眼睛\")时，直接使用对应的preset_key调用预设接口\n4. 用简洁友好的语言回复结果\n5. 如果用户指令不明确，主动询问清楚\n\n### ❌ 不要做的\n1. 不要向用户索要设备UUID（已经通过变量传入）\n2. 不要提供超出能力范围的功能（如继电器、舵机、PWM等）\n3. 不要过度解释技术细节\n4. 不要在用户没问的情况下重复查询数据\n\n## 回复示例\n\n### 传感器查询\n用户：\"现在温度多少？\"\n你：[调用传感器接口]\n你：\"当前温度是24.5°C 😊\"\n\n### LED控制\n用户：\"帮我开灯\"\n你：\"好的，请问要打开哪个LED灯呢？我们有LED 1到4号\"\n用户：\"LED1\"\n你：[调用控制接口]\n你：\"✨ LED1已打开\"\n\n### 预设指令\n用户：\"眨眼睛\"\n你：[调用预设接口，preset_name=\"led_seq_mi71o69r\"]\n你：\"✅ LED1将点亮3秒后自动熄灭\"\n\n## 特别提示\n- 所有操作都自动使用设备UUID变量，你无需管理\n- 如果接口返回错误，友好地告知用户\"暂时无法操作，请稍后重试\"\n- 保持对话自然流畅，像朋友一样交流",
  "user_prompt_template": "",
  "model_config": {},
  "workflow_id": null,
  "knowledge_base_ids": [],
  "plugin_ids": [],
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
    "name": "智能家居助手",
    "description": "一个示例智能体，用于控制IoT设备和查询传感器",
    "system_prompt": "你是一个友好的智能家居助手，可以帮助用户控制IoT设备。\n\n## 设备信息\n设备UUID: 712cad58-de27-45d1-b839-dad78b4b0c27 \n\n## 你的能力\n\n### 1️⃣ 查询传感器数据\n- 温度查询：当用户问\"温度多少\"、\"几度\"、\"热不热\"\n- 湿度查询：当用户问\"湿度多少\"、\"潮湿吗\"、\"干燥吗\"\n\n### 2️⃣ 控制LED灯\n- 支持LED 1-4号\n- 开灯：当用户说\"打开灯\"、\"开灯\"、\"点亮LED\"\n- 关灯：当用户说\"关灯\"、\"关闭灯\"、\"熄灯\"\n\n### 3️⃣ 执行预设指令\n\n**可用预设列表：**\n\n| 预设名称 | 触发词 | preset_key | 说明 |\n|---------|--------|------------|------|\n| 眨眼睛 | \"眨眼睛\"、\"眨一下\" | led_seq_mi71o69r | LED1点亮3秒后熄灭 |\n\n**使用方法：**\n当用户说出触发词时，使用对应的preset_key调用预设接口。\n\n## 交互规则\n\n### ✅ 应该做的\n1. 当用户查询温度/湿度时，直接调用传感器接口\n2. 当用户要控制LED时，先确认是哪个LED（1-4），然后调用控制接口\n3. 当用户说出预设触发词（如\"眨眼睛\")时，直接使用对应的preset_key调用预设接口\n4. 用简洁友好的语言回复结果\n5. 如果用户指令不明确，主动询问清楚\n\n### ❌ 不要做的\n1. 不要向用户索要设备UUID（已经通过变量传入）\n2. 不要提供超出能力范围的功能（如继电器、舵机、PWM等）\n3. 不要过度解释技术细节\n4. 不要在用户没问的情况下重复查询数据\n\n## 回复示例\n\n### 传感器查询\n用户：\"现在温度多少？\"\n你：[调用传感器接口]\n你：\"当前温度是24.5°C 😊\"\n\n### LED控制\n用户：\"帮我开灯\"\n你：\"好的，请问要打开哪个LED灯呢？我们有LED 1到4号\"\n用户：\"LED1\"\n你：[调用控制接口]\n你：\"✨ LED1已打开\"\n\n### 预设指令\n用户：\"眨眼睛\"\n你：[调用预设接口，preset_name=\"led_seq_mi71o69r\"]\n你：\"✅ LED1将点亮3秒后自动熄灭\"\n\n## 特别提示\n- 所有操作都自动使用设备UUID变量，你无需管理\n- 如果接口返回错误，友好地告知用户\"暂时无法操作，请稍后重试\"\n- 保持对话自然流畅，像朋友一样交流",
    "user_prompt_template": "",
    "model_config": {},
    "workflow_id": null,
    "knowledge_base_ids": [],
    "plugin_ids": [],
    "status": "draft",
    "created_at": "2025-11-30T09:40:36.405486+08:00",
    "updated_at": "2025-11-30T09:40:36.405529+08:00"
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

### 9. 为智能体添加插件

**请求**
```
POST /api/v1/agents/{id}/add_plugins/
Content-Type: application/json
```

**请求体**
```json
{
  "plugin_ids": [
    1 /*填入插件id，如果有多个用逗号隔开*/
  ]
}
```

### 10. 从智能体删除插件

**请求**
```
POST /api/v1/agents/{id}/remove_plugins/
Content-Type: application/json
```

**请求体**
```json
{
  "plugin_ids": [
    1 /*填入插件id，如果有多个用逗号隔开*/
  ]
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
  "openapi_spec": {
  "openapi": "3.0.0",
  "info": {
    "title": "IoT设备控制",
    "description": "传感器查询、设备控制（LED/继电器/舵机/PWM）、预设指令",
    "version": "1.2.0"
  },
  "servers": [
    {
      "url": "https://plugin.aiot.hello1023.com",
      "description": "生产服务器"
    }
  ],
  "paths": {
    "/plugin/sensor-data": {
      "get": {
        "summary": "查询传感器",
        "description": "获取各类传感器数据（温度、湿度、雨水、DS18B20等）",
        "operationId": "getSensorData",
        "tags": ["传感器"],
        "parameters": [
          {
            "name": "uuid",
            "in": "query",
            "description": "UUID",
            "required": true,
            "schema": {
              "type": "string",
              "example": "test"
            }
          },
          {
            "name": "sensor",
            "in": "query",
            "description": "传感器类型",
            "required": true,
            "schema": {
              "type": "string",
              "enum": [
                "温度",
                "湿度",
                "雨水",
                "雨水级别",
                "DS18B20",
                "DS18B20温度",
                "temperature",
                "humidity",
                "rain",
                "rain_level"
              ],
              "example": "温度"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "成功",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                  "code": {"type": "integer", "example": 200},
                  "msg": {"type": "string", "example": "成功"},
                    "data": {
                      "type": "object",
                    "properties": {
                      "value": {"type": "number", "example": 24.5},
                      "unit": {"type": "string", "example": "°C"}
                    }
                    }
                  }
                },
                "example": {
                  "code": 200,
                  "msg": "成功",
                  "data": {
                    "value": 24.5,
                    "unit": "°C"
                  }
                }
              }
            }
          }
        }
      }
    },
    "/plugin/control": {
      "post": {
        "summary": "控制设备",
        "description": "控制LED、继电器、舵机、PWM等设备",
        "operationId": "controlDevice",
        "tags": ["设备控制"],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["device_uuid", "port_type", "port_id", "action"],
                "properties": {
                  "device_uuid": {
                    "type": "string",
                    "description": "设备UUID",
                    "example": "test"
                  },
                  "port_type": {
                    "type": "string",
                    "description": "设备类型：led(LED灯)、relay(继电器)、servo(舵机)、pwm(PWM输出)",
                    "enum": ["led", "relay", "servo", "pwm"],
                    "example": "led"
                  },
                  "port_id": {
                    "type": "integer",
                    "description": "端口ID：LED和继电器为1-4，舵机为1-4，PWM为1-2",
                    "minimum": 1,
                    "maximum": 4,
                    "example": 1
                  },
                  "action": {
                    "type": "string",
                    "description": "动作：on(打开)/off(关闭)/set(设置值，用于舵机角度或PWM占空比)",
                    "enum": ["on", "off", "set"],
                    "example": "on"
                  },
                  "value": {
                    "type": "integer",
                    "description": "设置值：舵机角度(0-180)或PWM占空比(0-100)，仅当action为set时需要",
                    "minimum": 0,
                    "maximum": 180,
                    "example": 90
                  }
                }
              },
              "example": {
                "device_uuid": "test",
                "port_type": "led",
                "port_id": 1,
                "action": "on"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "成功",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                  "code": {"type": "integer", "example": 200},
                  "msg": {"type": "string", "example": "成功"},
                    "data": {
                      "type": "object",
                    "properties": {
                      "result": {"type": "string", "example": "success"}
                    }
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "/plugin/preset": {
      "post": {
        "summary": "执行预设",
        "description": "通过preset_key执行用户自定义预设",
        "operationId": "executePreset",
        "tags": ["预设指令"],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["device_uuid", "preset_name"],
                "properties": {
                  "device_uuid": {
                    "type": "string",
                    "description": "设备UUID",
                    "example": "test"
                  },
                  "preset_name": {
                    "type": "string",
                    "description": "预设标识(preset_key)，如：led_blink_k8x9y2",
                    "example": "led_blink_k8x9y2"
                  },
                  "parameters": {
                    "type": "object",
                    "description": "可选参数（通常为空）",
                    "additionalProperties": true,
                    "example": {}
                  }
                }
              },
              "example": {
                "device_uuid": "test",
                "preset_name": "led_blink_k8x9y2",
                "parameters": {}
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "成功",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                  "code": {"type": "integer", "example": 200},
                  "msg": {"type": "string", "example": "成功"},
                    "data": {
                      "type": "object",
                    "properties": {
                      "result": {"type": "string", "example": "success"}
                    }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
,
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
