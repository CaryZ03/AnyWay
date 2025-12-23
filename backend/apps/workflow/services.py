"""
Workflow 校验与执行引擎。

参考 teacher's backend 中的 WorkflowExecutor / WorkflowValidator，并按 AnyWay
项目自己的数据结构（Workflow.definition）做了适配：

- Workflow.definition: {"nodes": [...], "edges": [...], "config": {...}}
- 节点类型: start / intent / llm / http / knowledge / plugin / end

节点输出存储：
- 每个节点的输出会存储到 context[node.id] 中
- 后续节点可以通过 {node_id} 或 {node_id.field} 引用前面节点的输出
- 例如：{llm.response} 可以引用 id 为 "llm" 的节点的 response 字段

变量替换支持：
- {node_id} - 引用节点完整输出（如果是字典会转为JSON字符串）
- {node_id.field} - 引用节点输出的特定字段，支持嵌套（如 {llm.response}）
- {input.param} - 引用工作流输入参数
"""
from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import requests
from django.utils import timezone

from apps.llm.services import get_llm_service
from apps.plugin.models import Plugin
from apps.plugin.services import PluginService

from .models import Workflow, WorkflowExecution

logger = logging.getLogger(__name__)


class WorkflowExecutionError(Exception):
    """工作流执行相关的错误。"""


@dataclass
class _Node:
    id: str
    type: str
    config: Dict[str, Any]


@dataclass
class _Edge:
    id: str
    source: str
    target: str


class WorkflowValidator:
    """
    简单的 DAG 校验器：
    - 必须有且只有一个 start 节点
    - 必须有且只有一个 end 节点
    - 所有边的 source / target 必须存在
    - 不允许有环
    """

    @staticmethod
    def _build_nodes_edges(definition: Dict[str, Any]) -> Tuple[List[_Node], List[_Edge]]:
        raw_nodes = definition.get("nodes") or []
        raw_edges = definition.get("edges") or []
        nodes: List[_Node] = []
        edges: List[_Edge] = []

        for n in raw_nodes:
            if not isinstance(n, dict):
                continue

            node_id = n.get("id")
            node_type = n.get("type")
            if not node_id or not node_type:
                continue

            nodes.append(
                _Node(
                    id=str(node_id),
                    type=str(node_type),
                    config=n.get("config") or n.get("data") or {},
                )
            )

        for e in raw_edges:
            if not isinstance(e, dict):
                continue

            edge_id = e.get("id") or f"{e.get('source')}->{e.get('target')}"
            source = e.get("source")
            target = e.get("target")
            if not source or not target:
                continue

            edges.append(
                _Edge(
                    id=str(edge_id),
                    source=str(source),
                    target=str(target),
                )
            )

        return nodes, edges

    @staticmethod
    def validate(definition: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        errors: List[str] = []
        warnings: List[str] = []

        nodes, edges = WorkflowValidator._build_nodes_edges(definition)
        if not nodes:
            errors.append("工作流必须至少包含一个节点")
            return errors, warnings

        start_nodes = [n for n in nodes if n.type == "start"]
        end_nodes = [n for n in nodes if n.type == "end"]

        if len(start_nodes) == 0:
            errors.append("工作流必须包含一个开始节点（type = 'start'）")
        elif len(start_nodes) > 1:
            errors.append(f"工作流只能包含一个开始节点，当前有 {len(start_nodes)} 个")

        if len(end_nodes) == 0:
            errors.append("工作流必须包含一个结束节点（type = 'end'）")
        elif len(end_nodes) > 1:
            errors.append(f"工作流只能包含一个结束节点，当前有 {len(end_nodes)} 个")

        if errors:
            return errors, warnings

        node_ids = {n.id for n in nodes}
        for e in edges:
            if e.source not in node_ids:
                errors.append(f"边 '{e.id}' 的源节点 '{e.source}' 不存在")
            if e.target not in node_ids:
                errors.append(f"边 '{e.id}' 的目标节点 '{e.target}' 不存在")

        if errors:
            return errors, warnings

        # 检测环（DFS）
        graph: Dict[str, List[str]] = {n.id: [] for n in nodes}
        for e in edges:
            if e.source in graph:
                graph[e.source].append(e.target)

        state: Dict[str, int] = {n.id: 0 for n in nodes}  # 0=未访问,1=访问中,2=已访问

        def dfs(node_id: str) -> bool:
            if state[node_id] == 1:
                return True
            if state[node_id] == 2:
                return False
            state[node_id] = 1
            for nxt in graph.get(node_id, []):
                if dfs(nxt):
                    return True
            state[node_id] = 2
            return False

        for n in nodes:
            if state[n.id] == 0 and dfs(n.id):
                errors.append("工作流中存在循环依赖，必须是无环图(DAG)")
                break

        # 可达性检测：从 start 出发，检查是否有不可达节点
        start_id = start_nodes[0].id
        visited = {start_id}
        queue = [start_id]
        while queue:
            cur = queue.pop(0)
            for nxt in graph.get(cur, []):
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)
        unreachable = node_ids - visited
        if unreachable:
            warnings.append(
                f"以下节点从开始节点不可达: {', '.join(sorted(unreachable))}"
            )

        return errors, warnings

    @staticmethod
    def assert_valid(definition: Dict[str, Any]) -> None:
        errors, _warnings = WorkflowValidator.validate(definition)
        if errors:
            raise WorkflowExecutionError("工作流验证失败: " + "; ".join(errors))

    @staticmethod
    def topological_order(definition: Dict[str, Any]) -> List[_Node]:
        """返回拓扑排序后的节点列表。"""
        nodes, edges = WorkflowValidator._build_nodes_edges(definition)
        node_map = {n.id: n for n in nodes}
        in_degree: Dict[str, int] = {n.id: 0 for n in nodes}
        graph: Dict[str, List[str]] = {n.id: [] for n in nodes}

        for e in edges:
            if e.source in graph and e.target in in_degree:
                graph[e.source].append(e.target)
                in_degree[e.target] += 1

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        ordered: List[_Node] = []

        while queue:
            cur = queue.pop(0)
            node = node_map.get(cur)
            if node:
                ordered.append(node)
            for nxt in graph.get(cur, []):
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)

        return ordered


class WorkflowEngine:
    """工作流执行引擎，按 DAG 顺序依次执行各类节点。"""

    def __init__(self) -> None:
        self.context: Dict[str, Any] = {}
        self.node_status: Dict[str, Any] = {}

    def _replace_variables(self, text: str) -> str:
        """
        变量替换，支持以下格式：
        - {node_id} - 引用节点输出
        - {node_id.field} - 引用节点输出的特定字段
        - {input.param} - 引用工作流输入参数
        
        Args:
            text: 待替换的文本
            
        Returns:
            str: 替换后的文本
        """
        if not isinstance(text, str):
            return text
        
        # 匹配变量：{node_id} 或 {node_id.field} 或 {input.param}
        pattern = r'\{([^}]+)\}'
        
        def replace_match(match):
            var_path = match.group(1)
            
            # 处理 {input.param} 格式
            if var_path.startswith("input."):
                param_name = var_path[6:]  # 去掉 "input."
                input_data = self.context.get("input", {})
                if isinstance(input_data, dict):
                    value = input_data.get(param_name)
                    if value is not None:
                        return str(value)
            
            # 处理 {node_id} 或 {node_id.field} 格式
            parts = var_path.split(".", 1)
            node_id = parts[0]
            
            if node_id in self.context:
                node_output = self.context[node_id]
                
                # 如果是 {node_id.field} 格式
                if len(parts) > 1:
                    field_path = parts[1]
                    # 支持嵌套字段访问，如 node_id.data.result
                    value = node_output
                    for field in field_path.split("."):
                        if isinstance(value, dict):
                            value = value.get(field)
                        else:
                            return match.group(0)  # 无法访问，返回原文本
                    if value is not None:
                        return str(value)
                else:
                    # {node_id} 格式，返回整个输出（如果是字符串）
                    if isinstance(node_output, str):
                        return node_output
                    elif isinstance(node_output, dict):
                        # 如果是字典，尝试转换为JSON字符串
                        return json.dumps(node_output, ensure_ascii=False)
            
            # 变量未找到，返回原文本
            return match.group(0)
        
        result = re.sub(pattern, replace_match, text)
        return result

    def execute(
        self, workflow: Workflow, input_data: Dict[str, Any], execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """
        执行指定工作流。

        :param workflow: Workflow 实例（包含 definition）
        :param input_data: 执行输入数据，前端 / 智能体会传入 {user_input: "..."} 等结构
        :param execution: WorkflowExecution 记录，用于追踪执行过程
        :return: 最终输出（通常包含 answer 字段）
        """
        definition = workflow.definition or {}
        if not isinstance(definition, dict):
            raise WorkflowExecutionError("工作流定义格式错误，definition 必须是对象")

        # 校验 DAG 基本合法性
        WorkflowValidator.assert_valid(definition)

        # 初始化执行上下文
        self.context = {}
        self.node_status = {}
        if isinstance(input_data, dict):
            self.context.update(input_data)
        else:
            self.context["input"] = input_data

        logger.info(
            "开始执行工作流 %s，输入: %s",
            workflow.id,
            json.dumps(self.context, ensure_ascii=False),
        )

        execution.status = "running"
        execution.started_at = timezone.now()
        execution.node_status = {}
        execution.error_message = None
        execution.save(
            update_fields=["status", "started_at", "node_status", "error_message"]
        )

        error: Exception | None = None

        ordered_nodes = WorkflowValidator.topological_order(definition)
        for node in ordered_nodes:
            start_ts = timezone.now()
            node_result: Dict[str, Any] | None = None
            node_error: str | None = None
            status = "success"

            try:
                node_result = self._execute_node(node)
                # 将节点输出存储到context[node.id]，方便后续节点通过变量引用
                if node_result is not None:
                    self.context[node.id] = node_result
            except Exception as exc:  # noqa: BLE001 - 需要兜底任何异常
                error = exc
                status = "failed"
                node_error = str(exc)
                logger.error(
                    "节点 %s(%s) 执行失败: %s",
                    node.id,
                    node.type,
                    str(exc),
                    exc_info=True,
                )

            end_ts = timezone.now()
            duration_ms = int((end_ts - start_ts).total_seconds() * 1000)

            self.node_status[node.id] = {
                "node_id": node.id,
                "type": node.type,
                "status": status,
                "started_at": start_ts.isoformat(),
                "completed_at": end_ts.isoformat(),
                "duration_ms": duration_ms,
                "output": node_result,
                "error": node_error,
            }

            # 如果某个节点失败，则终止后续执行
            if status == "failed":
                break

        # 组装最终输出：使用 end 节点的输出
        # 找到 end 节点的ID
        end_node_id = None
        for n in ordered_nodes:
            if n.type == "end":
                end_node_id = n.id
                break
        
        if end_node_id and end_node_id in self.context:
            # 使用 end 节点的输出作为最终输出
            final_output = self.context[end_node_id]
            # 确保是字典类型
            if not isinstance(final_output, dict):
                final_output = {"output": final_output}
        elif "answer" in self.context:
            # 如果没有end节点输出，但存在answer字段，使用answer
            final_output: Dict[str, Any] = {"answer": self.context.get("answer")}
        else:
            # 没有 end 节点输出和 answer 时，返回完整上下文（便于调试）
            final_output = dict(self.context)

        execution.output_data = final_output
        execution.node_status = self.node_status
        execution.completed_at = timezone.now()
        execution.status = "failed" if error else "completed"
        if error:
            execution.error_message = str(error)
        execution.save(
            update_fields=[
                "status",
                "output_data",
                "node_status",
                "completed_at",
                "error_message",
            ]
        )

        if error:
            raise WorkflowExecutionError(str(error))

        logger.info("工作流 %s 执行完成，状态: %s", workflow.id, execution.status)
        return final_output

    # === 各类节点执行逻辑 ===

    def _execute_node(self, node: _Node) -> Dict[str, Any] | None:
        node_type = node.type
        cfg = node.config or {}

        if node_type == "start":
            return self._execute_start_node(cfg)
        if node_type == "intent":
            return self._execute_intent_node(cfg)
        if node_type == "llm":
            return self._execute_llm_node(cfg)
        if node_type == "http":
            return self._execute_http_node(cfg)
        if node_type == "knowledge":
            return self._execute_knowledge_node(cfg)
        if node_type == "plugin":
            return self._execute_plugin_node(cfg)
        if node_type == "end":
            return self._execute_end_node(cfg)

        raise WorkflowExecutionError(f"不支持的节点类型: {node_type}")

    def _execute_start_node(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        开始节点：将输入统一包装为上下文。
        - 如果已有 user_input，则直接透传；
        - 否则将整个 context 视为 user_input 的载体。
        """
        user_input = self.context.get("user_input")
        if user_input is None:
            # 尽量从 input / message 等字段中推断
            user_input = (
                self.context.get("input")
                or self.context.get("message")
                or json.dumps(self.context, ensure_ascii=False)
            )
            self.context["user_input"] = user_input

        return {"user_input": user_input}

    def _execute_intent_node(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        意图识别节点：
        - 使用火山引擎(豆包)对当前 user_input 做意图分类
        - 返回 JSON: {intent_id, intent_name, reason}
        """
        intents = config.get("intents") or []
        if not intents:
            raise WorkflowExecutionError("意图识别节点未配置 intents 列表")

        user_input = self.context.get("user_input")
        if not user_input:
            raise WorkflowExecutionError("意图识别节点无法获取 user_input")

        model_name = config.get("model") or "doubao-seed-1-6-251015"
        temperature = float(config.get("temperature") or 0.2)

        intents_json = json.dumps(intents, ensure_ascii=False, indent=2)

        system_prompt = (
            "你是一个意图分类助手，负责将用户输入归类到给定的意图列表中。\n"
            "你必须严格按照要求返回 JSON，不要输出任何多余的文字。"
        )
        user_prompt = (
            "下面是可选的意图列表（JSON 数组，每个元素包含 id、name、description、examples 等字段）：\n"
            f"{intents_json}\n\n"
            "请根据上述意图列表，对下方用户输入进行分类，并严格返回如下 JSON 格式：\n"
            '{\n  "intent_id": "意图ID",\n  "intent_name": "意图名称",\n  "reason": "简要说明你为何选择该意图"\n}\n'
            "注意：\n"
            "1. 只能从给定意图列表中选择一个最合适的意图；\n"
            '2. 如果确实无法匹配，请将 intent_id 设为 "unknown"，intent_name 设为 "未知"；\n'
            "3. 一定只返回 JSON，不要有任何额外解释。\n\n"
            f"用户输入：{user_input}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        llm_service = get_llm_service("volcano")
        raw = llm_service.chat(messages=messages, model=model_name, temperature=temperature)

        try:
            data = json.loads(raw)
        except Exception as exc:  # noqa: BLE001
            raise WorkflowExecutionError(f"意图识别模型返回非 JSON 格式: {raw}") from exc

        intent_id = data.get("intent_id")
        intent_name = data.get("intent_name")
        reason = data.get("reason")

        if not intent_id or not intent_name:
            raise WorkflowExecutionError(f"意图识别结果缺少必要字段: {data}")

        result = {
            "intent_id": intent_id,
            "intent_name": intent_name,
            "intent_reason": reason,
        }
        # 同时写入简化字段，方便后续节点使用
        self.context["intent"] = intent_name
        return result

    def _execute_llm_node(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        LLM 节点：
        - 使用系统提示词 + 用户提示词模板 + 当前上下文 JSON 调用大模型
        - 要求模型严格返回 JSON: {answer, thoughts}
        """
        model_name = config.get("model") or "doubao-seed-1-6-251015"
        system_prompt = (
            config.get("systemPrompt")
            or "你是一个对话型 AI 助手，请根据上下文给出有帮助的回答。"
        )
        prompt_tpl = config.get("prompt")
        if not prompt_tpl:
            raise WorkflowExecutionError("LLM 节点未配置 prompt")

        temperature = float(config.get("temperature") or 0.7)

        context_json = json.dumps(self.context, ensure_ascii=False, indent=2)
        user_prompt = (
            f"{prompt_tpl}\n\n"
            "下面是当前工作流上下文（JSON 格式），你可以参考其中的信息进行回答：\n"
            f"{context_json}\n\n"
            "请严格按照如下 JSON 结构返回结果：\n"
            "{\n"
            '  "answer": "最终的自然语言回答",\n'
            '  "thoughts": "可选的思考过程说明"\n'
            "}\n"
            "注意：一定只返回 JSON，不要有任何额外解释。"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        llm_service = get_llm_service("volcano")
        raw = llm_service.chat(messages=messages, model=model_name, temperature=temperature)

        try:
            data = json.loads(raw)
        except Exception as exc:  # noqa: BLE001
            raise WorkflowExecutionError(f"LLM 节点返回非 JSON 格式: {raw}") from exc

        answer = data.get("answer")
        if not isinstance(answer, str) or not answer.strip():
            raise WorkflowExecutionError(f"LLM 节点返回的 answer 非法: {data}")

        # 将 answer / thoughts 等字段合并回上下文
        result = {
            "answer": answer,
            "thoughts": data.get("thoughts"),
        }
        return result

    def _execute_http_node(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        HTTP请求节点：
        - 调用外部HTTP API
        - 支持变量替换（url、headers、body）
        """
        url = config.get("url", "")
        method = config.get("method", "GET").upper()
        headers = config.get("headers", {})
        body = config.get("body")
        timeout = config.get("timeout", 10)
        retry_count = config.get("retryCount", 0)
        validate_ssl = config.get("validateSSL", True)
        follow_redirect = config.get("followRedirect", True)
        
        if not url:
            raise WorkflowExecutionError("HTTP节点必须配置URL")
        
        # 对URL进行变量替换
        url = self._replace_variables(url)
        
        # 替换请求头中的变量
        processed_headers = {}
        for key, value in headers.items():
            if isinstance(value, str):
                processed_headers[key] = self._replace_variables(value)
            else:
                processed_headers[key] = value
        
        # 替换请求体中的变量
        processed_body = None
        if body:
            if isinstance(body, str):
                processed_body = self._replace_variables(body)
                # 尝试解析为JSON
                try:
                    processed_body = json.loads(processed_body)
                except json.JSONDecodeError:
                    # 如果不是JSON，保持原样
                    pass
            elif isinstance(body, dict):
                # 如果是字典，递归替换其中的字符串值
                processed_body = self._replace_dict_variables(body)
            else:
                processed_body = body
        
        # 发送HTTP请求（支持重试）
        last_error = None
        for attempt in range(retry_count + 1):
            try:
                # 准备请求参数
                request_kwargs = {
                    "method": method,
                    "url": url,
                    "headers": processed_headers,
                    "timeout": timeout,
                    "allow_redirects": follow_redirect,
                    "verify": validate_ssl,
                }
                
                # 根据方法设置body
                if method in ("POST", "PUT", "PATCH"):
                    if isinstance(processed_body, dict):
                        request_kwargs["json"] = processed_body
                    elif isinstance(processed_body, str):
                        request_kwargs["data"] = processed_body
                    else:
                        request_kwargs["data"] = processed_body
                
                response = requests.request(**request_kwargs)
                
                # 尝试解析响应为JSON
                try:
                    response_body = response.json()
                except (ValueError, json.JSONDecodeError):
                    response_body = response.text
                
                # 构造输出结果
                output = {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response_body,
                    "data": response_body,  # 别名，方便引用
                    "status": response.status_code,  # 别名
                    "success": 200 <= response.status_code < 300,  # 成功标志
                    "url": url,  # 实际请求的URL（经过变量替换后）
                    "method": method,  # 请求方法
                }
                
                logger.info(
                    "HTTP节点执行成功，状态码: %s, 尝试次数: %s/%s",
                    response.status_code,
                    attempt + 1,
                    retry_count + 1,
                )
                return output
                
            except requests.exceptions.Timeout:
                last_error = TimeoutError(f"HTTP请求超时（{timeout}秒）")
                if attempt < retry_count:
                    logger.warning(
                        "HTTP请求超时，正在重试 (%s/%s)", attempt + 1, retry_count
                    )
                    import time
                    time.sleep(1)  # 重试前等待1秒
                else:
                    raise last_error
            except Exception as e:
                last_error = e
                if attempt < retry_count:
                    logger.warning(
                        "HTTP请求失败: %s，正在重试 (%s/%s)", str(e), attempt + 1, retry_count
                    )
                    import time
                    time.sleep(1)  # 重试前等待1秒
                else:
                    logger.error(
                        "HTTP节点执行失败（已重试%s次）: %s", retry_count, str(e), exc_info=True
                    )
                    raise
        
        # 如果所有重试都失败，抛出最后一个错误
        if last_error:
            raise last_error
        
        raise WorkflowExecutionError("HTTP节点执行失败")
    
    def _replace_dict_variables(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """递归替换字典中的变量"""
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self._replace_variables(value)
            elif isinstance(value, dict):
                result[key] = self._replace_dict_variables(value)
            elif isinstance(value, list):
                result[key] = [
                    self._replace_variables(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                result[key] = value
        return result
    
    def _execute_knowledge_node(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        知识库检索节点：
        - 调用外部知识库API进行检索
        - 支持变量替换（query）
        """
        knowledge_base_id = config.get("knowledge_base_id") or config.get("knowledgeBaseId")
        query = config.get("query", "")
        top_k = config.get("top_k") or config.get("topK", 5)
        user_id = config.get("user_id") or config.get("userId", 1)  # 默认用户ID为1
        
        if not knowledge_base_id:
            raise WorkflowExecutionError("知识库检索节点必须配置知识库ID")
        
        if not query:
            raise WorkflowExecutionError("知识库检索节点必须配置查询文本")
        
        # 对查询文本进行变量替换
        query = self._replace_variables(str(query))
        
        # 知识库API URL（从环境变量读取，如果没有则使用默认值）
        kb_api_base = os.getenv("KB_API_BASE", "https://kenbers.cyou/kb")
        query_url = f"{kb_api_base}/query"
        
        # 构建请求体
        request_body = {
            "user_id": user_id,
            "knowledge_base_id": int(knowledge_base_id),
            "query": query,
            "top_k": int(top_k),
        }
        
        try:
            # 发送请求
            response = requests.post(
                query_url,
                json=request_body,
                timeout=30,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            
            # 解析响应
            response_data = response.json()
            
            # 处理不同的响应格式
            results = []
            if isinstance(response_data, dict):
                # 格式1: { documents: [...], metadatas: [...], scores: [...] }
                if "documents" in response_data:
                    documents = response_data.get("documents", [])
                    metadatas = response_data.get("metadatas", [])
                    scores = response_data.get("scores", [])
                    results = [
                        {
                            "id": str(metadatas[i].get("doc_id", i)) if i < len(metadatas) else str(i),
                            "content": doc,
                            "metadata": metadatas[i] if i < len(metadatas) else {},
                            "score": scores[i] if i < len(scores) else None,
                        }
                        for i, doc in enumerate(documents)
                    ]
                # 格式2: { data: [...] }
                elif "data" in response_data:
                    results = response_data["data"]
                    if not isinstance(results, list):
                        results = []
                # 格式3: 直接是结果字典
                elif isinstance(response_data, dict) and "results" in response_data:
                    results = response_data["results"]
            elif isinstance(response_data, list):
                # 格式4: 直接是数组
                results = response_data
            
            # 构造输出结果
            output = {
                "results": results,
                "total": len(results),
                "kb_id": knowledge_base_id,
                "query": query,  # 经过变量替换后的查询文本
            }
            
            # 如果有结果，添加便捷访问字段
            if results:
                output["top_result"] = results[0]  # 最相似的结果
                output["top_content"] = results[0].get("content", "") if isinstance(results[0], dict) else str(results[0])  # 最相似的内容
                if isinstance(results[0], dict) and "score" in results[0]:
                    output["top_similarity"] = results[0]["score"]  # 最高相似度
                
                # 合并所有内容，用于LLM节点
                contents = []
                for r in results:
                    if isinstance(r, dict):
                        content = r.get("content", "")
                        metadata = r.get("metadata", {})
                        title = metadata.get("title") or metadata.get("document_title") or "未知来源"
                        contents.append(f"【来源：{title}】\n{content}")
                    else:
                        contents.append(str(r))
                output["combined_content"] = "\n\n---\n\n".join(contents)
            
            logger.info("知识库检索完成，找到 %s 个结果", len(results))
            return output
            
        except requests.exceptions.RequestException as e:
            logger.error("知识库检索节点执行失败: %s", str(e), exc_info=True)
            raise WorkflowExecutionError(f"知识库检索失败: {str(e)}")
        except Exception as e:
            logger.error("知识库检索节点执行异常: %s", str(e), exc_info=True)
            raise WorkflowExecutionError(f"知识库检索异常: {str(e)}")
    
    def _execute_plugin_node(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        插件节点：
        - 调用已注册的插件操作
        - 支持变量替换（参数）
        """
        plugin_id = config.get("plugin_id") or config.get("pluginId")
        operation_id = config.get("operation_id") or config.get("operationId")
        params = config.get("params") or config.get("arguments") or {}
        
        if not plugin_id:
            raise WorkflowExecutionError("插件节点必须配置插件ID")
        
        if not operation_id:
            raise WorkflowExecutionError("插件节点必须配置操作ID（operationId）")
        
        # 查询插件
        try:
            plugin = Plugin.objects.get(id=plugin_id, deleted=False)
        except Plugin.DoesNotExist:
            raise WorkflowExecutionError(f"插件不存在: {plugin_id}")
        
        # 检查插件状态
        if plugin.status != "enabled":
            raise WorkflowExecutionError(f"插件未启用: {plugin.name}")
        
        # 对参数进行变量替换
        processed_params = self._replace_dict_variables(params)
        
        # 调用插件操作
        plugin_service = PluginService()
        result = plugin_service.call_plugin_operation(plugin, operation_id, processed_params)
        
        if not result.get("success"):
            error_msg = result.get("error", "未知错误")
            logger.error("插件节点执行失败: %s", error_msg)
            raise WorkflowExecutionError(f"插件调用失败: {error_msg}")
        
        # 构造输出结果
        output = {
            "success": True,
            "data": result.get("data"),
            "status_code": result.get("status_code"),
            "operation_id": operation_id,
            "plugin_id": plugin_id,
            "plugin_name": plugin.name,
        }
        
        logger.info(
            "插件节点执行成功，插件: %s, 操作: %s, 状态码: %s",
            plugin.name,
            operation_id,
            result.get("status_code"),
        )
        return output
    
    def _execute_end_node(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        结束节点：
        - 优先使用 outputContent 配置（支持变量替换）
        - 如果 outputContent 存在，执行变量替换后返回
        - 否则默认返回上下文中的 answer 字段
        - 若不存在，则返回完整上下文（用于调试）。
        """
        output_content = config.get("outputContent") or config.get("output_content")
        
        # 优先使用 outputContent (这是前端直接编辑的字段)
        if output_content:
            # 执行变量替换
            final_content = self._replace_variables(str(output_content))
            logger.info("结束节点输出(自定义): %s", final_content)
            
            # 尝试判断是否是JSON格式，如果是则解析，否则返回字符串
            try:
                if (final_content.startswith("{") and final_content.endswith("}")) or \
                   (final_content.startswith("[") and final_content.endswith("]")):
                    return json.loads(final_content)
            except json.JSONDecodeError:
                pass
                
            return {"output": final_content}
        
        # 默认逻辑：优先返回 answer 字段
        if "answer" in self.context:
            return {"answer": self.context.get("answer")}
        
        # 如果没有answer，返回完整上下文（用于调试）
        logger.info("结束节点输出(默认): %s", self.context)
        return dict(self.context)


