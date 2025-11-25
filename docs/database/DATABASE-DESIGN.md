# 数据库设计文档

## 数据库概述

- **数据库类型**: MySQL 8.0
- **字符集**: utf8mb4
- **排序规则**: utf8mb4_unicode_ci
- **时区**: Asia/Shanghai

## ER图

```
┌─────────────┐       ┌──────────────┐
│   Agent     │──────>│ Conversation │
└─────────────┘       └──────────────┘
      │
      │ (关联)
      ├──────────────> Workflow
      ├──────────────> KnowledgeBase
      └──────────────> Plugin

┌──────────────┐       ┌─────────────────────┐
│  Workflow    │──────>│ WorkflowExecution   │
└──────────────┘       └─────────────────────┘

┌──────────────┐       ┌──────────┐       ┌───────────────┐
│KnowledgeBase │──────>│ Document │──────>│ DocumentChunk │
└──────────────┘       └──────────┘       └───────────────┘
```

## 表结构设计

### 1. agent - 智能体表

存储智能体的配置信息和提示词。

| 字段名 | 类型 | 约束 | 说明 | 对应用户故事 |
|--------|------|------|------|--------------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键ID | - |
| name | VARCHAR(100) | NOT NULL | 智能体名称 | US-001, US-002 |
| description | TEXT | NULL | 描述 | US-001 |
| system_prompt | TEXT | NULL | 系统提示词 | US-001, US-004 |
| user_prompt_template | TEXT | NULL | 用户提示词模板 | US-001 |
| model_config | JSON | DEFAULT {} | 模型配置 | US-001 |
| workflow_id | BIGINT | NULL | 关联工作流ID | US-013 |
| knowledge_base_ids | JSON | DEFAULT [] | 关联知识库ID列表 | US-013 |
| plugin_ids | JSON | DEFAULT [] | 关联插件ID列表 | US-013 |
| status | VARCHAR(20) | DEFAULT 'draft' | 状态(draft/published) | US-012 |
| created_at | DATETIME | AUTO | 创建时间 | US-002 |
| updated_at | DATETIME | AUTO | 更新时间 | US-003 |
| deleted | BOOLEAN | DEFAULT FALSE | 逻辑删除标记 | US-014 |

**索引**:
- PRIMARY KEY (id)
- INDEX idx_status (status)
- INDEX idx_created_at (created_at)

**设计理由**:
- 使用JSON字段存储灵活的配置信息（model_config）
- 使用JSON数组存储多对多关联（knowledge_base_ids, plugin_ids）
- 逻辑删除避免数据丢失

### 2. conversation - 对话记录表

存储用户与智能体的对话历史。

| 字段名 | 类型 | 约束 | 说明 | 对应用户故事 |
|--------|------|------|------|--------------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键ID | - |
| agent_id | BIGINT | FK, NOT NULL | 智能体ID | US-004, US-013 |
| user_message | TEXT | NOT NULL | 用户消息 | US-004, US-013 |
| assistant_message | TEXT | NOT NULL | 助手回复 | US-004, US-013 |
| context | JSON | DEFAULT {} | 上下文信息 | US-013 |
| created_at | DATETIME | AUTO | 创建时间 | - |

**索引**:
- PRIMARY KEY (id)
- INDEX idx_agent_created (agent_id, created_at)

**外键**:
- FOREIGN KEY (agent_id) REFERENCES agent(id) ON DELETE CASCADE

### 3. workflow - 工作流表

存储工作流的定义信息。

| 字段名 | 类型 | 约束 | 说明 | 对应用户故事 |
|--------|------|------|------|--------------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键ID | - |
| name | VARCHAR(100) | NOT NULL | 工作流名称 | US-008 |
| description | TEXT | NULL | 描述 | US-008 |
| definition | JSON | DEFAULT {} | 工作流定义(节点和连线) | US-008 |
| status | VARCHAR(20) | DEFAULT 'draft' | 状态(draft/active) | US-008 |
| created_at | DATETIME | AUTO | 创建时间 | US-017 |
| updated_at | DATETIME | AUTO | 更新时间 | US-015 |
| deleted | BOOLEAN | DEFAULT FALSE | 逻辑删除标记 | US-016 |

**索引**:
- PRIMARY KEY (id)
- INDEX idx_status (status)
- INDEX idx_created_at (created_at)

**设计理由**:
- definition字段使用JSON存储DAG结构（nodes和edges）
- 支持可视化编辑器的数据存储

### 4. workflow_execution - 工作流执行记录表

记录工作流的执行状态和结果。

| 字段名 | 类型 | 约束 | 说明 | 对应用户故事 |
|--------|------|------|------|--------------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键ID | - |
| workflow_id | BIGINT | FK, NOT NULL | 工作流ID | US-009 |
| input_data | JSON | DEFAULT {} | 输入数据 | US-009 |
| output_data | JSON | DEFAULT {} | 输出数据 | US-009 |
| status | VARCHAR(20) | DEFAULT 'pending' | 执行状态 | US-009 |
| node_status | JSON | DEFAULT {} | 节点执行状态 | US-009 |
| error_message | TEXT | NULL | 错误信息 | US-009 |
| started_at | DATETIME | NULL | 开始时间 | US-009 |
| completed_at | DATETIME | NULL | 完成时间 | US-009 |
| created_at | DATETIME | AUTO | 创建时间 | - |

**索引**:
- PRIMARY KEY (id)
- INDEX idx_workflow_status (workflow_id, status)
- INDEX idx_created_at (created_at)

**外键**:
- FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE

### 5. knowledge_base - 知识库表

存储知识库的基本信息。

| 字段名 | 类型 | 约束 | 说明 | 对应用户故事 |
|--------|------|------|------|--------------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键ID | - |
| name | VARCHAR(100) | NOT NULL | 知识库名称 | US-005 |
| description | TEXT | NULL | 描述 | US-005 |
| embedding_model | VARCHAR(100) | DEFAULT 'text-embedding-ada-002' | 嵌入模型 | US-006 |
| created_at | DATETIME | AUTO | 创建时间 | - |
| updated_at | DATETIME | AUTO | 更新时间 | - |
| deleted | BOOLEAN | DEFAULT FALSE | 逻辑删除标记 | - |

**索引**:
- PRIMARY KEY (id)
- INDEX idx_created_at (created_at)

### 6. document - 文档表

存储上传的文档信息。

| 字段名 | 类型 | 约束 | 说明 | 对应用户故事 |
|--------|------|------|------|--------------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键ID | - |
| knowledge_base_id | BIGINT | FK, NOT NULL | 知识库ID | US-006 |
| filename | VARCHAR(255) | NOT NULL | 文件名 | US-006, US-007 |
| file_path | VARCHAR(500) | NOT NULL | 文件路径 | US-006 |
| file_type | VARCHAR(50) | NOT NULL | 文件类型 | US-006 |
| file_size | BIGINT | NOT NULL | 文件大小(字节) | US-006 |
| content | TEXT | NULL | 文档内容 | US-006 |
| status | VARCHAR(20) | DEFAULT 'pending' | 处理状态 | US-006, US-007 |
| error_message | TEXT | NULL | 错误信息 | US-006 |
| chunk_count | INT | DEFAULT 0 | 分块数量 | US-006 |
| uploaded_at | DATETIME | AUTO | 上传时间 | US-007 |
| processed_at | DATETIME | NULL | 处理时间 | US-007 |

**索引**:
- PRIMARY KEY (id)
- INDEX idx_kb_status (knowledge_base_id, status)
- INDEX idx_uploaded_at (uploaded_at)

**外键**:
- FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_base(id) ON DELETE CASCADE

### 7. document_chunk - 文档分块表

存储文档分块和向量嵌入。

| 字段名 | 类型 | 约束 | 说明 | 对应用户故事 |
|--------|------|------|------|--------------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键ID | - |
| document_id | BIGINT | FK, NOT NULL | 文档ID | US-006 |
| content | TEXT | NOT NULL | 分块内容 | US-006 |
| chunk_index | INT | NOT NULL | 分块索引 | US-006 |
| embedding | JSON | NULL | 向量嵌入 | US-006 |
| metadata | JSON | DEFAULT {} | 元数据 | US-006 |
| created_at | DATETIME | AUTO | 创建时间 | - |

**索引**:
- PRIMARY KEY (id)
- INDEX idx_doc_index (document_id, chunk_index)

**外键**:
- FOREIGN KEY (document_id) REFERENCES document(id) ON DELETE CASCADE

**设计理由**:
- embedding字段存储向量数据（后续可迁移到专用向量数据库）
- chunk_index确保分块顺序

### 8. plugin - 插件表

存储插件信息和OpenAPI规范。

| 字段名 | 类型 | 约束 | 说明 | 对应用户故事 |
|--------|------|------|------|--------------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键ID | - |
| name | VARCHAR(100) | NOT NULL | 插件名称 | US-010 |
| description | TEXT | NULL | 描述 | US-010 |
| openapi_spec | JSON | NOT NULL | OpenAPI规范 | US-010 |
| base_url | VARCHAR(500) | NOT NULL | 基础URL | US-010 |
| auth_config | JSON | DEFAULT {} | 认证配置 | US-010 |
| status | VARCHAR(20) | DEFAULT 'enabled' | 状态(enabled/disabled) | US-011 |
| created_at | DATETIME | AUTO | 创建时间 | - |
| updated_at | DATETIME | AUTO | 更新时间 | - |
| deleted | BOOLEAN | DEFAULT FALSE | 逻辑删除标记 | - |

**索引**:
- PRIMARY KEY (id)
- INDEX idx_status (status)
- INDEX idx_created_at (created_at)

**设计理由**:
- openapi_spec存储完整的OpenAPI规范，支持动态调用
- auth_config支持多种认证方式（API Key, OAuth等）

## 数据库初始化

### 创建数据库

```sql
CREATE DATABASE IF NOT EXISTS aiagent 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE aiagent;
SET time_zone = '+08:00';
```

### Django迁移

```bash
# 生成迁移文件
python manage.py makemigrations

# 执行迁移
python manage.py migrate
```

## 性能优化建议

1. **索引优化**
   - 为常用查询字段添加索引
   - 复合索引优化多条件查询

2. **分区表**
   - 对话记录表按时间分区
   - 执行记录表按时间分区

3. **缓存策略**
   - 使用Redis缓存热点数据
   - 智能体配置缓存

4. **读写分离**
   - 主从复制
   - 读操作分流到从库

## 数据备份策略

1. **全量备份**: 每天凌晨3点
2. **增量备份**: 每小时一次
3. **备份保留**: 30天
4. **异地备份**: 云存储

## 数据迁移计划

### 向量数据库迁移

后续将document_chunk表的embedding字段迁移到专用向量数据库：
- Pinecone
- Milvus
- Weaviate

优势：
- 更高效的向量检索
- 支持大规模向量数据
- 专业的相似度搜索
