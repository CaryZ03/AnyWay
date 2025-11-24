"""
工作流视图
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Workflow, WorkflowExecution
from .serializers import (
    WorkflowSerializer, WorkflowListSerializer,
    WorkflowExecutionSerializer, WorkflowExecuteRequestSerializer
)
from .services import WorkflowEngine
from utils.response import ApiResponse


class WorkflowViewSet(viewsets.ModelViewSet):
    """
    工作流视图集
    
    提供工作流的CRUD操作和执行功能
    """
    queryset = Workflow.objects.filter(deleted=False)
    serializer_class = WorkflowSerializer
    
    def get_serializer_class(self):
        """根据action选择序列化器"""
        if self.action == 'list':
            return WorkflowListSerializer
        return WorkflowSerializer
    
    @swagger_auto_schema(
        operation_summary='获取工作流列表',
        operation_description='获取所有未删除的工作流列表',
        responses={200: WorkflowListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """获取工作流列表"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(data=serializer.data, message='获取工作流列表成功')
    
    @swagger_auto_schema(
        operation_summary='创建工作流',
        operation_description='创建新的工作流',
        request_body=WorkflowSerializer,
        responses={201: WorkflowSerializer()}
    )
    def create(self, request, *args, **kwargs):
        """创建工作流"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ApiResponse.created(data=serializer.data, message='工作流创建成功')
    
    @swagger_auto_schema(
        operation_summary='获取工作流详情',
        operation_description='根据ID获取工作流详细信息',
        responses={200: WorkflowSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        """获取工作流详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.success(data=serializer.data, message='获取工作流详情成功')
    
    @swagger_auto_schema(
        operation_summary='更新工作流',
        operation_description='更新工作流信息',
        request_body=WorkflowSerializer,
        responses={200: WorkflowSerializer()}
    )
    def update(self, request, *args, **kwargs):
        """更新工作流"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ApiResponse.success(data=serializer.data, message='工作流更新成功')
    
    @swagger_auto_schema(
        operation_summary='删除工作流',
        operation_description='逻辑删除工作流',
        responses={200: '删除成功'}
    )
    def destroy(self, request, *args, **kwargs):
        """删除工作流（逻辑删除）"""
        instance = self.get_object()
        instance.deleted = True
        instance.save()
        return ApiResponse.success(message='工作流删除成功')
    
    @swagger_auto_schema(
        operation_summary='执行工作流',
        operation_description='执行指定的工作流',
        request_body=WorkflowExecuteRequestSerializer,
        responses={200: openapi.Response('执行成功', WorkflowExecutionSerializer())}
    )
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """执行工作流"""
        workflow = self.get_object()
        serializer = WorkflowExecuteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        input_data = serializer.validated_data['input_data']
        
        # 创建执行记录
        execution = WorkflowExecution.objects.create(
            workflow=workflow,
            input_data=input_data,
            status='pending'
        )
        
        # 异步执行工作流
        # TODO: 使用Celery异步任务
        engine = WorkflowEngine()
        try:
            result = engine.execute(workflow, input_data, execution)
            exec_serializer = WorkflowExecutionSerializer(execution)
            return ApiResponse.success(data=exec_serializer.data, message='工作流执行成功')
        except Exception as e:
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.save()
            return ApiResponse.error(message=f'工作流执行失败: {str(e)}')
    
    @swagger_auto_schema(
        operation_summary='获取执行历史',
        operation_description='获取工作流的执行历史记录',
        responses={200: WorkflowExecutionSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def executions(self, request, pk=None):
        """获取执行历史"""
        workflow = self.get_object()
        executions = workflow.executions.all()
        serializer = WorkflowExecutionSerializer(executions, many=True)
        return ApiResponse.success(data=serializer.data, message='获取执行历史成功')
