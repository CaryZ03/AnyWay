"""
工作流序列化器
"""
from rest_framework import serializers
from .models import Workflow, WorkflowExecution


class WorkflowSerializer(serializers.ModelSerializer):
    """工作流序列化器"""
    
    class Meta:
        model = Workflow
        fields = [
            'id', 'name', 'description', 'definition',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        """验证名称不能为空"""
        if not value or not value.strip():
            raise serializers.ValidationError('工作流名称不能为空')
        return value
    
    def validate_definition(self, value):
        """验证工作流定义格式"""
        if not isinstance(value, dict):
            raise serializers.ValidationError('工作流定义必须是JSON对象')
        
        # 验证必需字段
        if 'nodes' not in value or 'edges' not in value:
            raise serializers.ValidationError('工作流定义必须包含nodes和edges字段')
        
        # TODO: 添加DAG验证（有向无环图）
        
        return value


class WorkflowListSerializer(serializers.ModelSerializer):
    """工作流列表序列化器"""
    
    class Meta:
        model = Workflow
        fields = ['id', 'name', 'description', 'status', 'created_at', 'updated_at']


class WorkflowExecutionSerializer(serializers.ModelSerializer):
    """工作流执行记录序列化器"""
    
    class Meta:
        model = WorkflowExecution
        fields = [
            'id', 'workflow', 'input_data', 'output_data',
            'status', 'node_status', 'error_message',
            'started_at', 'completed_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'output_data', 'status', 'node_status',
            'error_message', 'started_at', 'completed_at', 'created_at'
        ]


class WorkflowExecuteRequestSerializer(serializers.Serializer):
    """工作流执行请求序列化器"""
    input_data = serializers.JSONField(required=True, help_text='输入数据')
