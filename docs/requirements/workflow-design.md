## 工作流节点设计与大模型调用说明

### 节点类型一览

- **开始节点 (`start`)**：接收用户输入，统一包装为 JSON：`{"user_input": "用户原始问题"}`，后续所有节点都在此基础上增量增加字段。
- **意图识别节点 (`intent`)**：调用豆包大模型，根据配置的意图列表为当前问题打上意图标签。
- **大模型节点 (`llm`)**：在完整上下文（包括意图识别结果等）的基础上调用豆包，生成最终回答。
- **结束节点 (`end`)**：从当前上下文中读取 `answer` 字段，作为工作流的最终输出返回给前端与用户。

### 工作流后端定义结构

`Workflow.definition` 字段保存前端编辑后的 JSON：

```json
{
  "nodes": [
    { "id": "start", "type": "start", "config": {} },
    { "id": "intent-1", "type": "intent", "config": { "intents": [] } },
    { "id": "llm-1", "type": "llm", "config": { "model": "doubao-seed-1-6-251015" } },
    { "id": "end", "type": "end", "config": {} }
  ],
  "edges": [
    { "id": "e-start-intent-1", "source": "start", "target": "intent-1" },
    { "id": "e-intent-1-llm-1", "source": "intent-1", "target": "llm-1" },
    { "id": "e-llm-1-end", "source": "llm-1", "target": "end" }
  ],
  "config": {
    "timeout": 60,
    "retry": 0,
    "parallel": false
  }
}
```

### 意图识别节点 (`intent`) JSON 约定

- **系统 Prompt（后端自动生成，大意）**：
  - 介绍自己是“意图分类助手”；
  - 给出必须遵循的 JSON 模板；
  - 强调“只能返回 JSON，不要多余文字”。
- **用户 Prompt（后端自动生成）**：
  - 包含：意图列表 JSON + 当前用户输入；
  - 再次提醒“只返回 JSON，不要输出任何解释”。
- **要求大模型严格返回 JSON：**

```json
{
  "intent_id": "意图ID",
  "intent_name": "意图名称",
  "reason": "简要说明你为何选择该意图"
}
```

后端在 `WorkflowEngine._execute_intent_node` 中对回复做 `json.loads` 解析，解析失败会抛错并标记节点执行失败。

### 大模型节点 (`llm`) JSON 约定

- **系统 Prompt（默认值，可在前端节点配置中编辑）**：
  - 说明自己是“对话型 AI 助手”；
  - 要求基于工作流上下文给出最终回答。
- **用户 Prompt（前端由用户填写）**：
  - 后端会在模板后面追加当前上下文 JSON，并再次给出固定的 JSON 输出格式要求。
- **要求大模型严格返回 JSON：**

```json
{
  "answer": "最终的自然语言回答",
  "thoughts": "可选的思考过程说明"
}
```

后端在 `WorkflowEngine._execute_llm_node` 中做 `json.loads` 解析，并将 `answer` 等字段合并回工作流上下文。

### API Key 使用

- 大模型调用统一复用 `apps.llm.services.VolcanoService`，从 `.env` 中读取：
  - `ARK_API_KEY`
  - `ARK_API_BASE`
- 工作流引擎内所有 LLM 调用都经由 `get_llm_service('volcano')`，不需要额外配置。


