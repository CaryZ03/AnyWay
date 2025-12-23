# 单元与集成测试说明

## 脚本使用说明
- 全量（单元+集成）：
```powershell
conda activate Aiagent
./run_tests.ps1          # 输出详细
./run_tests.ps1 -Quiet   # 精简输出
```
- 分模块（单元+集成）：
```powershell
conda activate Aiagent
./run_app_tests.ps1 -App agent     # agent 模块
./run_app_tests.ps1 -App plugin    # plugin 模块
./run_app_tests.ps1 -App knowledge # knowledge 模块
./run_app_tests.ps1 -App workflow  # workflow 模块
./run_app_tests.ps1 -App llm       # llm 模块
./run_app_tests.ps1 -App aiagent   # aiagent 健康/Swagger
./run_app_tests.ps1 -App all       # 等同于全量
# 可选 -Quiet 开关，减少输出
```

## 当前单元测试覆盖
- Agent：API 基础 CRUD/发布/软删/列表，LLM 对话（含插件工具链 mock）、插件工具全链路单测。
- 健康/Swagger：`/health/`、`/swagger/` 基础可用。
- Knowledge：API CRUD、上传/列表/搜索占位；tasks `split_text`；序列化校验（文件类型/大小、文档计数、top_k 边界）。
- Plugin：API CRUD/启用禁用/删除；Service OpenAPI 解析、调用成功/失败、格式化、HTTP 异常。
- Workflow：API CRUD、执行成功/失败；验证器（节点/边/循环/拓扑）、变量替换；节点执行 start/intent/llm/http/knowledge（含异常与重试）。
- LLM：Volcano 基础回复、tool_calls 二次调用/缺 api_map/调用异常回退；OpenAI 未配置占位、embedding 默认向量、embedding 客户端异常。
- Pytest 配置：`pytest.ini` 注册 `django_db`；`conftest.py` 默认 sqlite 内存并自动 migrate。

## 当前集成测试覆盖
- Agent：插件工具链对话（注册插件→绑定→tool_call→插件 HTTP→二次 LLM，均 mock）。
- Workflow：
  - 简单执行流（mock 引擎回填）。
  - intent→http→knowledge→end 复杂链路（LLM/HTTP/KB mock）。
  - HTTP 节点抛异常返回 5xx；执行失败回退（WorkflowExecutionError 500）。
- Knowledge：文档创建→上传→列表→搜索占位；不存在知识库检索 4xx；搜索缺 query / top_k 过大 400 校验。
- Plugin：CRUD/启用禁用/逻辑删除；插件 `/call/` 端点（mock HTTP）。

## 运行方式
- 一键全量（单元+集成）：
```powershell
./run_tests.ps1
```
- 按模块（单元+集成）：
```powershell
./run_app_tests.ps1 -App agent
./run_app_tests.ps1 -App plugin
./run_app_tests.ps1 -App knowledge
./run_app_tests.ps1 -App workflow
./run_app_tests.ps1 -App llm
./run_app_tests.ps1 -App aiagent  # health/swagger
./run_app_tests.ps1 -App all      # 等同于全量
```
- 直接使用 pytest：
```powershell
python -m pytest -q
python -m pytest apps/agent/tests/integration/test_agent_plugin_flow.py -q
```

## Mock/依赖注意点
- LLM：测试内 `patch.dict` 注入 `ARK_API_KEY`/`ARK_API_BASE` 并 mock `requests.Session.post`。
- 插件 HTTP：`patch('requests.get')`/`patch('requests.request')` 返回假响应，覆盖成功与异常。
- Workflow HTTP/KB 节点：`patch('requests.request')`/`patch('requests.post')` 覆盖超时重试与失败。
- 媒体/存储：`override_settings` 指定临时 `MEDIA_ROOT` 并清理。

## 当前空缺与后续计划（无真实 API_KEY 场景）
- 知识库检索/HTTP 节点外呼的 4xx/超时回退可进一步补充（集成与单测）。
- Workflow 若新增节点类型（如 plugin 节点）或引入真实异步处理，按现有模式补测试。
- LLM 新 provider：参照 Volcano/OpenAI 追加空 key、异常、tool_call 分支。
- 如需真实外呼，需配置 `ARK_API_KEY`/`ARK_API_BASE` 或相应 provider 的 key，并替换 mock。

# 集成测试计划（建议）
1) 环境：sqlite/docker-compose，`.env.test` 提供假值；必要时使用 stub 服务。
2) API 端到端：Agent（workflow/插件分支）、Knowledge（上传→检索→删除）、Workflow（执行与节点状态）、Plugin（注册→调用→删除）。
3) 外部依赖：responses/httpx mock 或 wiremock/docker stub。
4) 数据隔离：fixture/factory，临时上传目录。
5) 断言：状态码、响应结构、副作用（DB）、异常消息。
6) CI：`pytest -q` Job；可用 fast/slow 标记分层。
