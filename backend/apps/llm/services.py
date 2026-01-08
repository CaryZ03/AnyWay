"""
LLM服务集成
"""
import os
from typing import List, Dict, Optional
import logging
import requests
import json

logger = logging.getLogger(__name__)


class LLMService:
    """LLM服务基类"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url
    
    def chat(self, messages: List[Dict], model: str = 'gpt-3.5-turbo', **kwargs):
        """
        聊天接口
        
        Args:
            messages: 消息列表
            model: 模型名称
            **kwargs: 其他参数
        
        Returns:
            模型回复
        """
        raise NotImplementedError
    
    def embedding(self, text: str, model: str = 'text-embedding-ada-002'):
        """
        生成文本嵌入
        
        Args:
            text: 文本内容
            model: 嵌入模型名称
        
        Returns:
            嵌入向量
        """
        raise NotImplementedError


class VolcanoService(LLMService):
    """火山引擎（豆包）服务"""
    
    def __init__(self, api_key: Optional[str] = None):
        base_url = os.getenv('ARK_API_BASE', 'https://ark.cn-beijing.volces.com/api/v3')
        api_key = api_key or os.getenv('ARK_API_KEY')
        super().__init__(api_key, base_url)
        
        if not self.api_key:
            logger.warning('未配置 ARK_API_KEY，火山引擎服务不可用')
        
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            })

    def chat(self, messages: List[Dict], model: str = 'doubao-seed-1-6-251015', **kwargs):
        """
        火山引擎聊天接口（兼容 OpenAI Chat Completions），支持插件
        """
        if not self.api_key:
            return "抱歉，AI服务尚未配置，请设置 ARK_API_KEY。"

        tools = kwargs.pop("active_tools", [])
        api_map = kwargs.pop("api_map", {})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
        }

        try:
            logger.info(f"调用火山引擎API: model={model}, messages_count={len(messages)}")
            logger.debug(f"Payload: {json.dumps({**payload, 'tools': tools}, ensure_ascii=False, indent=2)}")
            logger.debug(f"工具生成结果：{json.dumps(tools, ensure_ascii=False, indent=2)}")
            logger.debug(f"工具API生成结果：{json.dumps(api_map, ensure_ascii=False, indent=2)}")

            # 第一次调用 LLM
            response = self.session.post(
                f"{self.base_url.rstrip('/')}/chat/completions",
                json={**payload, "tools": tools},
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            logger.debug(f"LLM返回原始数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            message = data.get("choices", [{}])[0].get("message", {})

            # 处理 tool_calls
            tool_calls = message.get("tool_calls") or []
            tool_results = []
            if tool_calls and api_map:
                logger.info(f"发现 {len(tool_calls)} 个工具调用")
                for idx, tool_call in enumerate(tool_calls, 1):
                    tool_name = tool_call["function"]["name"]
                    tool_args = json.loads(tool_call["function"]["arguments"])
                    logger.info(f"工具调用 {idx}: {tool_name} 参数: {tool_args}")

                    # 在 api_map 中找到对应的插件接口
                    plugin_api = None
                    for p_map in api_map.values():
                        if tool_name in p_map:
                            plugin_api = p_map[tool_name]
                            break

                    if plugin_api:
                        method = plugin_api["method"]
                        url = plugin_api["url"]
                        logger.info(f"准备调用插件API: {tool_name} -> {url}, 方法: {method}")

                        try:
                            if method.upper() == "GET":
                                result = requests.get(url, params=tool_args, timeout=5).json()
                            else:
                                result = requests.post(url, json=tool_args, timeout=5).json()
                            logger.info(f"插件API返回结果: {json.dumps(result, ensure_ascii=False)}")
                        except Exception as e:
                            result = {"error": str(e)}
                            logger.error(f"插件调用失败: {tool_name}, 错误: {str(e)}")

                        # 收集工具结果用于第二次调用 LLM
                        tool_results.append(f"{tool_name} 返回: {json.dumps(result, ensure_ascii=False)}")
                    else:
                        logger.warning(f"未找到插件API映射: {tool_name}")

            # 第二次调用 LLM，传入工具结果作为 assistant 消息，而不是 role=tool
            if tool_results:
                messages_for_second_call = messages + [{
                    "role": "assistant",
                    "content": "\n".join(tool_results)
                }]
                payload2 = {
                    "model": model,
                    "messages": messages_for_second_call,
                    "temperature": kwargs.get("temperature", 0.7),
                }
                logger.debug(f"第二次调用火山引擎 payload: {json.dumps(payload2, ensure_ascii=False, indent=2)}")

                response = self.session.post(
                    f"{self.base_url.rstrip('/')}/chat/completions",
                    json=payload2,
                    timeout=60
                )
                response.raise_for_status()
                data = response.json()
                logger.debug(f"第二次 LLM 返回原始数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
                message = data.get("choices", [{}])[0].get("message", {})

            return message.get("content", "")

        except Exception as e:
            logger.error(f"火山引擎API调用失败: {str(e)}", exc_info=True)
            return f"抱歉，发生了错误: {str(e)}"


class OpenAIService(LLMService):
    """OpenAI服务（保留用于兼容）"""
    
    def __init__(self, api_key: str = None):
        base_url = None
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        super().__init__(api_key, base_url)
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except Exception as e:
            logger.error(f'OpenAI客户端初始化失败: {str(e)}')
            self.client = None
    
    def chat(self, messages: List[Dict], model: str = 'gpt-3.5-turbo', **kwargs):
        """
        OpenAI聊天接口
        """
        if not self.client:
            return "OpenAI服务未配置"
            
        try:

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f'OpenAI API调用失败: {str(e)}')
            return f"抱歉，发生了错误: {str(e)}"
    
    def embedding(self, text: str, model: str = 'text-embedding-ada-002'):
        """
        生成文本嵌入
        """
        if not self.client:
            return [0.1] * 1536
            
        try:
            response = self.client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f'OpenAI Embedding API调用失败: {str(e)}')
            return [0.1] * 1536


def get_llm_service(provider: str = 'volcano') -> LLMService:
    """
    获取LLM服务实例
    
    Args:
        provider: 服务提供商，支持 'volcano' (火山引擎) 或 'openai'
    
    Returns:
        LLM服务实例
    """
    if provider == 'volcano':
        return VolcanoService()
    elif provider == 'openai':
        return OpenAIService()
    else:
        logger.warning(f'未知的LLM提供商: {provider}，使用默认的火山引擎服务')
        return VolcanoService()


# 为了向后兼容，保留原有函数
def get_llm_service_legacy() -> LLMService:
    """
    获取LLM服务实例
    
    Args:
        provider: 服务提供商
    
    Returns:
        LLM服务实例
    """
    if provider == 'openai':
        return OpenAIService()
    else:
        raise ValueError(f'不支持的LLM提供商: {provider}')
