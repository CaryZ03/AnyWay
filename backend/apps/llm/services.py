"""
LLM服务集成
"""
import os
from typing import List, Dict, Optional
import logging
import requests

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
        火山引擎聊天接口（兼容 OpenAI Chat Completions）
        """
        if not self.api_key:
            return "抱歉，AI服务尚未配置，请设置 ARK_API_KEY。"
        
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        payload = {
            'model': model,
            'messages': messages,
            'temperature': kwargs.get('temperature', 0.7),
        }
        reasoning_effort = kwargs.get('reasoning_effort')
        if reasoning_effort:
            payload['reasoning_effort'] = reasoning_effort
        
        try:
            logger.info(f'调用火山引擎API: model={model}, messages_count={len(messages)}')
            response = self.session.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            choices = data.get('choices') or []
            if not choices:
                logger.error(f'火山引擎返回内容异常: {data}')
                return "抱歉，我暂时无法回复，你可以稍后再试。"
            message = choices[0].get('message') or {}
            reply = message.get('content')
            if reply:
                logger.info(f'火山引擎API调用成功，回复长度: {len(reply)}')
                return reply
            logger.warning(f'火山引擎未返回content: {data}')
            return "抱歉，我没有生成回复。"
        except requests.HTTPError as http_err:
            error_text = http_err.response.text if http_err.response else str(http_err)
            logger.error(f'火山引擎HTTP错误: {error_text}')
            return f"抱歉，AI服务返回错误：{error_text}"
        except Exception as e:
            logger.error(f'火山引擎API调用失败: {str(e)}', exc_info=True)
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
