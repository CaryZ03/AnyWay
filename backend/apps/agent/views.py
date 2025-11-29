"""
智能体视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import os

from .models import Agent, Conversation
from .serializers import (
    AgentSerializer, AgentListSerializer,
    ConversationSerializer, ChatRequestSerializer
)
from utils.response import ApiResponse


class AgentViewSet(viewsets.ModelViewSet):
    """
    智能体视图集
    
    提供智能体的CRUD操作
    """
    queryset = Agent.objects.filter(deleted=False)
    serializer_class = AgentSerializer
    
    def get_serializer_class(self):
        """根据action选择序列化器"""
        if self.action == 'list':
            return AgentListSerializer
        return AgentSerializer
    
    @swagger_auto_schema(
        operation_summary='获取智能体列表',
        operation_description='获取所有未删除的智能体列表',
        responses={200: AgentListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """获取智能体列表"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(data=serializer.data, message='获取智能体列表成功')
    
    @swagger_auto_schema(
        operation_summary='创建智能体',
        operation_description='创建新的智能体',
        request_body=AgentSerializer,
        responses={201: AgentSerializer()}
    )
    def create(self, request, *args, **kwargs):
        """创建智能体"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ApiResponse.created(data=serializer.data, message='智能体创建成功')
    
    @swagger_auto_schema(
        operation_summary='获取智能体详情',
        operation_description='根据ID获取智能体详细信息',
        responses={200: AgentSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        """获取智能体详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.success(data=serializer.data, message='获取智能体详情成功')
    
    @swagger_auto_schema(
        operation_summary='更新智能体',
        operation_description='更新智能体信息',
        request_body=AgentSerializer,
        responses={200: AgentSerializer()}
    )
    def update(self, request, *args, **kwargs):
        """更新智能体"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ApiResponse.success(data=serializer.data, message='智能体更新成功')
    
    @swagger_auto_schema(
        operation_summary='删除智能体',
        operation_description='逻辑删除智能体',
        responses={200: '删除成功'}
    )
    def destroy(self, request, *args, **kwargs):
        """删除智能体（逻辑删除）"""
        instance = self.get_object()
        instance.deleted = True
        instance.save()
        return ApiResponse.success(message='智能体删除成功')
    
    @swagger_auto_schema(
        operation_summary='发布智能体',
        operation_description='将智能体状态从草稿改为已发布',
        responses={200: AgentSerializer()}
    )
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """发布智能体"""
        agent = self.get_object()
        
        # 验证配置是否完整
        if not agent.system_prompt:
            return ApiResponse.error(message='系统提示词不能为空')
        
        agent.status = 'published'
        agent.save()
        
        serializer = self.get_serializer(agent)
        return ApiResponse.success(data=serializer.data, message='智能体发布成功')
    
    @swagger_auto_schema(
        operation_summary='测试智能体',
        operation_description='发送测试消息给智能体',
        request_body=ChatRequestSerializer,
        responses={200: openapi.Response('测试成功', ConversationSerializer())}
    )
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """测试智能体（不需要发布即可测试）"""
        from apps.llm.services import get_llm_service
        import logging
        
        logger = logging.getLogger(__name__)
        agent = self.get_object()
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_message = serializer.validated_data['message']
        
        try:
            # 构建消息历史
            messages = []
            
            # 添加系统提示词
            if agent.system_prompt:
                messages.append({
                    'role': 'system',
                    'content': agent.system_prompt
                })
            
            # 添加用户消息
            messages.append({
                'role': 'user',
                'content': user_message
            })
            
            # 获取模型配置
            model_config = agent.model_config or {}
            model = model_config.get('model', 'doubao-seed-1-6-251015')
            temperature = model_config.get('temperature', 0.7)
            if model in ('gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo'):
                model = os.getenv('ARK_DEFAULT_MODEL', 'doubao-seed-1-6-251015')
            
            # 调用LLM服务生成回复
            llm_service = get_llm_service('volcano')
            assistant_message = llm_service.chat(
                messages=messages,
                model=model,
                temperature=temperature
            )
            
        except Exception as e:
            logger.error(f'测试LLM调用失败: {str(e)}')
            assistant_message = f"测试失败: {str(e)}"
        
        # 保存对话记录
        conversation = Conversation.objects.create(
            agent=agent,
            user_message=user_message,
            assistant_message=assistant_message,
            context=serializer.validated_data.get('context', {})
        )
        
        conv_serializer = ConversationSerializer(conversation)
        return ApiResponse.success(data=conv_serializer.data, message='测试成功')
    
    @swagger_auto_schema(
        operation_summary='与智能体对话',
        operation_description='与已发布的智能体进行对话',
        request_body=ChatRequestSerializer,
        responses={200: openapi.Response('对话成功', ConversationSerializer())}
    )
    @action(detail=True, methods=['post'])
    def chat(self, request, pk=None):
        """与智能体对话"""
        from apps.llm.services import get_llm_service
        import logging
        
        logger = logging.getLogger(__name__)
        agent = self.get_object()
        
        # 验证智能体是否已发布
        if agent.status != 'published':
            return ApiResponse.error(message='智能体未发布，无法对话')
        
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_message = serializer.validated_data['message']
        
        try:
            # 构建消息历史
            messages = []
            
            # 添加系统提示词
            if agent.system_prompt:
                messages.append({
                    'role': 'system',
                    'content': agent.system_prompt
                })

            # 从 Conversation 表中加载历史上下文
            past_convs = Conversation.objects.filter(agent=agent).order_by("created_at")
            for conv in past_convs:
                # 用户消息
                messages.append({"role": "user", "content": conv.user_message})
                # 助手消息
                messages.append({"role": "assistant", "content": conv.assistant_message})

            # 添加用户消息
            messages.append({
                'role': 'user',
                'content': user_message
            })
            
            # 获取模型配置
            model_config = agent.model_config or {}
            model = model_config.get('model', 'doubao-seed-1-6-251015')
            temperature = model_config.get('temperature', 0.7)
            if model in ('gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo'):
                model = os.getenv('ARK_DEFAULT_MODEL', 'doubao-seed-1-6-251015')
            
            logger.info(f'智能体 {agent.name} 开始对话，model={model}')
            
            # 调用LLM服务生成回复
            llm_service = get_llm_service('volcano')
            assistant_message = llm_service.chat(
                messages=messages,
                model=model,
                temperature=temperature
            )
            
            logger.info(f'LLM回复成功，长度: {len(assistant_message)}')
            
        except Exception as e:
            logger.error(f'LLM调用失败: {str(e)}', exc_info=True)
            assistant_message = f"抱歉，发生了错误: {str(e)}"
        
        # 保存对话记录
        conversation = Conversation.objects.create(
            agent=agent,
            user_message=user_message,
            assistant_message=assistant_message,
            context=serializer.validated_data.get('context', {})
        )
        
        conv_serializer = ConversationSerializer(conversation)
        return ApiResponse.success(data=conv_serializer.data, message='对话成功')

    @swagger_auto_schema(
        operation_summary='为智能体添加插件',
        operation_description='将一个或多个插件ID添加到智能体的 plugin_ids 列表中',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['plugin_ids'],
            properties={
                'plugin_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_INTEGER),
                    description='要添加的插件ID列表，也可以传单个整数'
                )
            }
        ),
        responses={200: AgentSerializer()}
    )
    @action(detail=True, methods=['post'])
    def add_plugins(self, request, pk=None):
        """给智能体添加一个或多个插件"""
        agent = self.get_object()
        plugin_ids = request.data.get('plugin_ids')

        if plugin_ids is None:
            return ApiResponse.error(message='plugin_ids 必填')

        # 如果前端传的是单个整数，转换为列表
        if isinstance(plugin_ids, int):
            plugin_ids = [plugin_ids]
        elif not isinstance(plugin_ids, list):
            return ApiResponse.error(message='plugin_ids 必须是整数或整数列表')

        # 初始化 plugin_ids
        current_ids = agent.plugin_ids or []

        # 去重并添加
        for pid in plugin_ids:
            if pid not in current_ids:
                current_ids.append(pid)

        agent.plugin_ids = current_ids
        agent.save()

        serializer = self.get_serializer(agent)
        return ApiResponse.success(data=serializer.data, message='插件添加成功')

    @swagger_auto_schema(
        operation_summary='从智能体删除插件',
        operation_description='将一个或多个插件ID从智能体的 plugin_ids 列表中移除',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['plugin_ids'],
            properties={
                'plugin_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_INTEGER),
                    description='要删除的插件ID列表，也可以传单个整数'
                )
            }
        ),
        responses={200: AgentSerializer()}
    )
    @action(detail=True, methods=['post'])
    def remove_plugins(self, request, pk=None):
        """从智能体删除一个或多个插件"""
        agent = self.get_object()
        plugin_ids = request.data.get('plugin_ids')

        if plugin_ids is None:
            return ApiResponse.error(message='plugin_ids 必填')

        # 如果前端传的是单个整数，转换为列表
        if isinstance(plugin_ids, int):
            plugin_ids = [plugin_ids]
        elif not isinstance(plugin_ids, list):
            return ApiResponse.error(message='plugin_ids 必须是整数或整数列表')

        # 当前插件列表
        current_ids = agent.plugin_ids or []

        # 移除指定ID
        agent.plugin_ids = [pid for pid in current_ids if pid not in plugin_ids]
        agent.save()

        serializer = self.get_serializer(agent)
        return ApiResponse.success(data=serializer.data, message='插件删除成功')
