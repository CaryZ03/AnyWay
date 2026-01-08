"""
插件视图
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
import logging

from .models import Plugin
from .serializers import PluginSerializer, PluginListSerializer, PluginCreateUpdateSerializer
from utils.response import ApiResponse

logger = logging.getLogger(__name__)


class PluginViewSet(viewsets.ModelViewSet):
    """
    插件视图集
    
    提供插件的CRUD操作
    """
    queryset = Plugin.objects.filter(deleted=False)
    serializer_class = PluginSerializer
    
    def get_serializer_class(self):
        """根据action选择序列化器"""
        if self.action == 'list':
            return PluginListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PluginCreateUpdateSerializer
        return PluginSerializer
    
    @swagger_auto_schema(
        operation_summary='获取插件列表',
        operation_description='获取所有未删除的插件列表',
        responses={200: PluginListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """获取插件列表"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(data=serializer.data, message='获取插件列表成功')
    
    @swagger_auto_schema(
        operation_summary='注册插件',
        operation_description='注册新的插件',
        request_body=PluginCreateUpdateSerializer,
        responses={201: PluginSerializer()}
    )
    def create(self, request, *args, **kwargs):
        """注册插件"""
        logger.info(f'创建插件请求，接收到的数据: {request.data}')
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f'序列化器验证失败: {serializer.errors}')
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            logger.info(f'插件创建成功: {instance.id}')
            # 使用 PluginSerializer 返回完整数据
            response_serializer = PluginSerializer(instance)
            return ApiResponse.created(data=response_serializer.data, message='插件注册成功')
        except Exception as e:
            logger.error(f'创建插件时发生异常: {str(e)}', exc_info=True)
            raise
    
    @swagger_auto_schema(
        operation_summary='获取插件详情',
        operation_description='根据ID获取插件详细信息',
        responses={200: PluginSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        """获取插件详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.success(data=serializer.data, message='获取插件详情成功')
    
    @swagger_auto_schema(
        operation_summary='更新插件',
        operation_description='更新插件信息',
        request_body=PluginCreateUpdateSerializer,
        responses={200: PluginSerializer()}
    )
    def update(self, request, *args, **kwargs):
        """更新插件"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()
        # 使用 PluginSerializer 返回完整数据
        response_serializer = PluginSerializer(updated_instance)
        return ApiResponse.success(data=response_serializer.data, message='插件更新成功')
    
    @swagger_auto_schema(
        operation_summary='删除插件',
        operation_description='逻辑删除插件',
        responses={200: '删除成功'}
    )
    def destroy(self, request, *args, **kwargs):
        """删除插件（逻辑删除）"""
        instance = self.get_object()
        instance.deleted = True
        instance.save()
        return ApiResponse.success(message='插件删除成功')
    
    @swagger_auto_schema(
        operation_summary='启用插件',
        operation_description='启用指定的插件',
        responses={200: PluginSerializer()}
    )
    @action(detail=True, methods=['post'])
    def enable(self, request, pk=None):
        """启用插件"""
        plugin = self.get_object()
        plugin.status = 'enabled'
        plugin.save()
        
        serializer = self.get_serializer(plugin)
        return ApiResponse.success(data=serializer.data, message='插件已启用')
    
    @swagger_auto_schema(
        operation_summary='禁用插件',
        operation_description='禁用指定的插件',
        responses={200: PluginSerializer()}
    )
    @action(detail=True, methods=['post'])
    def disable(self, request, pk=None):
        """禁用插件"""
        plugin = self.get_object()
        plugin.status = 'disabled'
        plugin.save()
        
        serializer = self.get_serializer(plugin)
        return ApiResponse.success(data=serializer.data, message='插件已禁用')
