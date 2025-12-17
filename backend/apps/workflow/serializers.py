"""
Workflow 相关序列化器
"""
from rest_framework import serializers

from .models import Workflow, WorkflowExecution
from .services import WorkflowValidator, WorkflowExecutionError


class WorkflowSerializer(serializers.ModelSerializer):
    """工作流序列化器，兼容前端 BackendWorkflow 类型。"""

    class Meta:
        model = Workflow
        fields = [
            "id",
            "name",
            "description",
            "definition",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value: str) -> str:
        if not value or not value.strip():
            raise serializers.ValidationError("工作流名称不能为空")
        return value

    def validate_definition(self, value):
        """
        校验工作流定义格式，并调用 WorkflowValidator 做 DAG 验证。
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("definition 必须是对象（JSON）")

        nodes = value.get("nodes")
        edges = value.get("edges")
        if not isinstance(nodes, list) or not isinstance(edges, list):
            raise serializers.ValidationError(
                "definition 必须包含列表类型的 nodes 和 edges 字段"
            )

        # 进一步进行 DAG 合法性校验（开始节点 / 结束节点 / 无环等）
        try:
            WorkflowValidator.assert_valid(value)
        except WorkflowExecutionError as exc:  # pragma: no cover - 简单错误转发
            raise serializers.ValidationError(str(exc)) from exc

        return value


class WorkflowExecutionSerializer(serializers.ModelSerializer):
    """工作流执行记录序列化器，对应前端 WorkflowExecutionResponse。"""

    class Meta:
        model = WorkflowExecution
        fields = [
            "id",
            "workflow",
            "input_data",
            "output_data",
            "status",
            "node_status",
            "error_message",
            "started_at",
            "completed_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "workflow",
            "status",
            "node_status",
            "error_message",
            "started_at",
            "completed_at",
            "created_at",
        ]


class WorkflowExecuteRequestSerializer(serializers.Serializer):
    """执行工作流的请求体，兼容前端 WorkflowExecuteRequest。"""

    input_data = serializers.JSONField(required=True, help_text="工作流输入数据")


