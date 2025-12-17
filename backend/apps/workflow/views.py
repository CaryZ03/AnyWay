"""
工作流视图集
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from utils.response import ApiResponse

from .models import Workflow, WorkflowExecution
from .serializers import (
    WorkflowSerializer,
    WorkflowExecutionSerializer,
    WorkflowExecuteRequestSerializer,
)
from .services import WorkflowEngine, WorkflowExecutionError


class WorkflowViewSet(viewsets.ModelViewSet):
    """
    工作流视图集

    提供工作流的 CRUD 与执行能力。
    """

    queryset = Workflow.objects.filter(deleted=False)
    serializer_class = WorkflowSerializer

    @swagger_auto_schema(
        operation_summary="获取工作流列表",
        operation_description="获取所有未删除的工作流列表",
        responses={200: WorkflowSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(data=serializer.data, message="获取工作流列表成功")

    @swagger_auto_schema(
        operation_summary="创建工作流",
        operation_description="创建新的工作流",
        request_body=WorkflowSerializer,
        responses={201: WorkflowSerializer()},
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ApiResponse.created(data=serializer.data, message="工作流创建成功")

    @swagger_auto_schema(
        operation_summary="获取工作流详情",
        operation_description="根据 ID 获取工作流详细信息",
        responses={200: WorkflowSerializer()},
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.success(data=serializer.data, message="获取工作流详情成功")

    @swagger_auto_schema(
        operation_summary="更新工作流",
        operation_description="更新工作流信息",
        request_body=WorkflowSerializer,
        responses={200: WorkflowSerializer()},
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ApiResponse.success(data=serializer.data, message="工作流更新成功")

    @swagger_auto_schema(
        operation_summary="删除工作流",
        operation_description="逻辑删除工作流",
        responses={200: "删除成功"},
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted = True
        instance.save(update_fields=["deleted"])
        return ApiResponse.success(message="工作流删除成功")

    @swagger_auto_schema(
        operation_summary="执行工作流",
        operation_description="执行指定工作流（主要用于调试和联调）",
        request_body=WorkflowExecuteRequestSerializer,
        responses={
            200: openapi.Response("执行成功", WorkflowExecutionSerializer()),
            500: "执行失败",
        },
    )
    @action(detail=True, methods=["post"])
    def execute(self, request, pk=None):
        workflow = self.get_object()
        req_serializer = WorkflowExecuteRequestSerializer(data=request.data)
        req_serializer.is_valid(raise_exception=True)
        input_data = req_serializer.validated_data["input_data"]

        execution = WorkflowExecution.objects.create(
            workflow=workflow,
            input_data=input_data,
            status="pending",
        )

        engine = WorkflowEngine()
        try:
            engine.execute(workflow, input_data, execution)
        except WorkflowExecutionError as exc:
            # 此时 execution 已由引擎更新为 failed 状态
            exec_serializer = WorkflowExecutionSerializer(execution)
            return ApiResponse.server_error(
                message=f"工作流执行失败: {str(exc)}",  # 前端会展示 message
            )

        exec_serializer = WorkflowExecutionSerializer(execution)
        return ApiResponse.success(
            data=exec_serializer.data,
            message="工作流执行成功",
        )


