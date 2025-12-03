"""
工作流执行引擎

目前支持的节点类型：
- start  ：开始节点，直接透传输入；
- intent ：意图识别节点，调用大模型做分类，要求严格 JSON 输出；
- llm    ：大模型节点，根据上下文生成最终回答，要求严格 JSON 输出；
- end    ：结束节点，返回上下文中的最终 answer。
"""
from datetime import datetime
import json
import logging
from typing import Any, Dict

from apps.llm.services import get_llm_service

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """工作流执行引擎"""
    
    def execute(self, workflow, input_data, execution):
        """
        执行工作流
        
        Args:
            workflow: 工作流对象
            input_data: 输入数据
            execution: 执行记录对象
        
        Returns:
            执行结果
        """
        logger.info(f'开始执行工作流: {workflow.name}')
        
        # 更新执行状态
        execution.status = 'running'
        execution.started_at = datetime.now()
        execution.save()
        
        try:
            # 获取工作流定义
            definition = workflow.definition
            nodes = definition.get('nodes', [])
            edges = definition.get('edges', [])
            
            # 构建节点依赖图
            node_map = {node['id']: node for node in nodes}
            node_status = {}
            
            # 按拓扑顺序执行节点
            # TODO: 实现完整的DAG执行逻辑
            output_data = self._execute_nodes(node_map, edges, input_data, node_status)
            
            # 更新执行记录
            execution.status = 'completed'
            execution.output_data = output_data
            execution.node_status = node_status
            execution.completed_at = datetime.now()
            execution.save()
            
            logger.info(f'工作流执行完成: {workflow.name}')
            return output_data
            
        except Exception as e:
            logger.error(f'工作流执行失败: {workflow.name}, 错误: {str(e)}')
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.completed_at = datetime.now()
            execution.save()
            raise
    
    def _execute_nodes(self, node_map, edges, input_data, node_status):
        """
        执行节点
        
        Args:
            node_map: 节点映射
            edges: 边列表
            input_data: 输入数据
            node_status: 节点状态记录
        
        Returns:
            输出数据
        """
        # 简化版本：顺序执行所有节点
        # TODO: 实现完整的拓扑排序和并行执行
        
        current_data = input_data
        
        for node_id, node in node_map.items():
            node_type = node.get('type', 'unknown')
            node_config = node.get('config', {})
            
            logger.info(f'执行节点: {node_id}, 类型: {node_type}')
            
            try:
                # 根据节点类型执行不同的逻辑
                result = self._execute_node(node_type, node_config, current_data)
                node_status[node_id] = {
                    'status': 'completed',
                    'output': result
                }
                current_data = result
                
            except Exception as e:
                logger.error(f'节点执行失败: {node_id}, 错误: {str(e)}')
                node_status[node_id] = {
                    'status': 'failed',
                    'error': str(e)
                }
                raise
        
        return current_data
    
    def _execute_node(self, node_type: str, config: Dict[str, Any], input_data: Dict[str, Any]):
        """
        执行单个节点
        
        Args:
            node_type: 节点类型
            config: 节点配置
            input_data: 输入数据
        
        Returns:
            节点输出（会与原始 input_data 合并）
        """
        # 开始/结束节点：简单透传
        if node_type in ('start', 'end'):
            return input_data

        # 意图识别节点
        if node_type == 'intent':
            return self._execute_intent_node(config, input_data)

        # 大模型节点
        if node_type == 'llm':
            return self._execute_llm_node(config, input_data)

        # 未识别类型，做透传
        logger.warning(f'未知的节点类型: {node_type}，将直接透传输入')
        return input_data

    def _execute_intent_node(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行意图识别节点

        要求大模型严格返回 JSON：
        {
            "intent_id": "xxx",
            "intent_name": "xxx",
            "reason": "简要说明"
        }
        """
        user_input = input_data.get('user_input') or input_data.get('message') or ''
        intents = config.get('intents') or []
        temperature = config.get('temperature', 0.2)
        model = config.get('model', 'doubao-seed-1-6-251015')

        if not user_input:
            raise ValueError('意图识别节点需要 user_input 字段')

        if not intents:
            raise ValueError('意图识别节点未配置 intents 列表')

        # 构造系统提示词和用户提示词
        intents_text = json.dumps(intents, ensure_ascii=False, indent=2)
        system_prompt = (
            "你是一个意图分类助手。请根据用户的自然语言输入，从给定的意图列表中选择最合适的一个意图。\n"
            "必须严格按照下面的 JSON 结构输出，不能包含任何多余文字或注释：\n"
            '{\n'
            '  "intent_id": "意图ID",\n'
            '  "intent_name": "意图名称",\n'
            '  "reason": "简要说明你为何选择该意图"\n'
            '}\n'
        )
        user_prompt = (
            f"意图列表（JSON）：\n{intents_text}\n\n"
            f"用户输入：\n{user_input}\n\n"
            "请只返回 JSON，不要输出任何解释。"
        )

        llm = get_llm_service('volcano')
        reply = llm.chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=model,
            temperature=temperature,
        )

        try:
            intent_result = json.loads(reply)
        except Exception as exc:
            logger.error(f'解析意图识别结果失败，原始回复: {reply}')
            raise ValueError(f'意图识别节点期望严格 JSON，但解析失败: {exc}')

        merged = dict(input_data)
        merged['intent'] = intent_result
        return merged

    def _execute_llm_node(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行大模型节点

        要求大模型严格返回 JSON：
        {
            "answer": "最终回答",
            "thoughts": "可选的思考过程"
        }
        """
        model = config.get('model', 'doubao-seed-1-6-251015')
        temperature = config.get('temperature', 0.7)
        max_tokens = config.get('maxTokens', 2000)
        system_prompt = config.get(
            'systemPrompt',
            '你是一个对话型 AI 助手，请根据给定上下文为用户生成最终回答。',
        )
        user_prompt_template = config.get(
            'prompt',
            '根据下面的工作流上下文，为用户生成最终回答。',
        )

        context_json = json.dumps(input_data, ensure_ascii=False, indent=2)
        user_prompt = (
            f"{user_prompt_template}\n\n"
            f"工作流上下文 JSON：\n{context_json}\n\n"
            "请严格按照下面的 JSON 结构输出，不能包含任何多余文字或注释：\n"
            '{\n'
            '  "answer": "最终的自然语言回答",\n'
            '  "thoughts": "可选的思考过程说明"\n'
            '}\n'
            "只返回 JSON。"
        )

        llm = get_llm_service('volcano')
        reply = llm.chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        try:
            result = json.loads(reply)
        except Exception as exc:
            logger.error(f'解析 LLM 节点结果失败，原始回复: {reply}')
            raise ValueError(f'LLM 节点期望严格 JSON，但解析失败: {exc}')

        merged = dict(input_data)
        merged.update(result)
        return merged
