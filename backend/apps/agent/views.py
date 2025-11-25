"""
智能体视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

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
        """测试智能体"""
        agent = self.get_object()
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_message = serializer.validated_data['message']
        
        # TODO: 调用LLM服务生成回复
        # 这里先返回模拟数据
        assistant_message = f"这是对 '{user_message}' 的测试回复"
        
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
        agent = self.get_object()
        
        # 验证智能体是否已发布
        if agent.status != 'published':
            return ApiResponse.error(message='智能体未发布，无法对话')
        
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_message = serializer.validated_data['message']
        
        # TODO: 调用LLM服务生成回复
        # TODO: 集成知识库检索
        # TODO: 执行工作流
        # TODO: 调用插件
        assistant_message = f"这是对 '{user_message}' 的回复"
        
        # 保存对话记录
        conversation = Conversation.objects.create(
            agent=agent,
            user_message=user_message,
            assistant_message=assistant_message,
            context=serializer.validated_data.get('context', {})
        )
        
        conv_serializer = ConversationSerializer(conversation)
        return ApiResponse.success(data=conv_serializer.data, message='对话成功')
