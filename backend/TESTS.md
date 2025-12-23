# 单元测试说明

## 当前覆盖概览
- Agent
  - API 基础：创建/发布/软删除/列表，LLM 对话（含 plugin 工具链）
  - 插件链路：绑定插件后，LLM tool_calls -> 插件 HTTP -> 二次 LLM 回复，全链路已通过 mock 验证
- 健康检查与 Swagger
  - `/health/`、`/swagger/` 基本可访问性
- Knowledge
  - API：知识库 CRUD、文档上传与列表、搜索占位
  - 任务：`split_text` 分块逻辑（含 overlap）
  - 序列化校验：上传文件类型/大小，文档计数，搜索 top_k 边界
- Plugin
  - API：注册、列表/详情、更新、启用/禁用、逻辑删除
  - Service：OpenAPI 解析为 functions/API 映射、成功/失败调用、格式化输出、操作缺失/HTTP 异常
- Workflow
  - API：CRUD、执行成功/失败回退
  - Services：验证器（节点/边/循环/拓扑）、变量替换、节点执行（start/intent/llm/http/knowledge，含异常与重试）、执行失败路径
- LLM
  - VolcanoService：基础回复、tool_calls 二次调用、api_map 缺失、tool 调用异常回退
  - OpenAIService：未配置占位、embedding 正常默认向量、embedding 客户端异常
- Pytest 配置
  - `pytest.ini` 注册 `django_db`
  - `conftest.py` 默认使用 sqlite 内存并自动 migrate

## 运行方式
在已激活虚拟环境下，从项目根目录执行：
```bash
python -m pytest -q
```
如需单文件或子集（示例）：
```bash
python -m pytest apps/agent/tests/test_agent_plugins_full_chain.py -q
python -m pytest apps/workflow/tests -q
```

## 主要 Mock/依赖注意点
- LLM 调用：测试内通过 `patch.dict` 注入 `ARK_API_KEY`/`ARK_API_BASE`，并 mock `requests.Session.post` 避免真实外呼。
- 插件 HTTP：使用 `patch('requests.get')`/`patch('requests.request')` 返回假响应，覆盖成功与异常路径。
- Workflow HTTP/知识库节点：mock `requests.request`/`requests.post`，覆盖超时重试与成功解析。
- 媒体/存储：`override_settings` 指定 `MEDIA_ROOT` 临时目录并清理，避免污染本地。

## 近期补测建议
- 知识库检索节点：服务端 4xx/5xx 或超时的重试/回退策略可再补充。
- WorkflowEngine：如果后续新增节点类型（如 plugin 节点落地），按现有模式添加成功/失败用例。
- LLM：若引入新的 provider，沿用 Volcano/OpenAI 的模式补充空 key、异常、tool_calls 分支。

---

# 集成测试计划（建议步骤）
1) 环境准备
- 使用 docker-compose 或本地 sqlite，确保迁移执行完毕，加载必要种子数据（示例 Agent/Plugin/Workflow）。
- 准备测试配置文件（.env.test），包含必要的外部依赖假值；如需真实 LLM/插件接口，可使用 wiremock/httpretty 搭建本地假服务。

2) API 级集成测试
- 覆盖核心业务流：
  - Agent 对话（含 workflow 分支、plugin tool_calls 分支），验证端到端响应与持久化。
  - Knowledge 文档上传→检索→删除的完整链路。
  - Workflow 执行：从创建→执行→节点状态落库→失败回退。
  - Plugin CRUD+调用：注册→启用→调用 operationId →禁用/删除。
- 使用 real DB（sqlite 内存可行），通过 `pytest` + DRF APIClient，尽量减少 mock，仅对不可控外部 HTTP 设定 stub。

3) 外部依赖模拟
- LLM/插件/知识库外呼：
  - 方案 A：在 pytest 会话级 fixture 中启动简单 http server（如 responses/httpx mock 或本地 Flask）返回固定 JSON；
  - 方案 B：使用 wiremock/docker 提供可配置 stub，便于并行测试。

4) 数据准备与隔离
- 使用 factory 或 fixture 生成 Agent/Plugin/Workflow/KnowledgeBase 组合，确保各用例互不影响；
- 针对文件上传，使用临时目录并在 teardown 清理。

5) 断言维度
- HTTP 状态码、响应结构与关键字段；
- 数据库副作用（会话记录、执行记录、文档/插件状态）；
- 日志/错误消息在异常场景下符合预期。

6) 覆盖清单（示例）
- Agent：无 workflow 时走 LLM；workflow 成功/失败回退；绑定插件 tool_calls 流程。
- Knowledge：上传→切片任务（如有异步则补充 celery stub）→检索→删除。
- Workflow：含 http/knowledge/intent/llm 节点的执行成功与失败；重试策略验证。
- Plugin：注册→调用 operation→错误返回处理。

7) 持续集成
- 在 CI 中新增 `pytest -q` job；如集成测试耗时，可拆分 fast/slow 标记，先跑单测+快链路，再跑带外部 stub 的集成套件。

