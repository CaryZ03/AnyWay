"""
智能体序列化器
"""
from rest_framework import serializers
from .models import Agent, Conversation


class AgentSerializer(serializers.ModelSerializer):
    """智能体序列化器"""
    
    class Meta:
        model = Agent
        fields = [
            'id', 'name', 'description', 'system_prompt',
            'user_prompt_template', 'model_config', 'workflow_id',
            'knowledge_base_ids', 'plugin_ids', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        """验证名称不能为空"""
        if not value or not value.strip():
            raise serializers.ValidationError('智能体名称不能为空')
        return value


class AgentListSerializer(serializers.ModelSerializer):
    """智能体列表序列化器（简化版）"""
    
    class Meta:
        model = Agent
        fields = ['id', 'name', 'description', 'status', 'created_at', 'updated_at']


class ConversationSerializer(serializers.ModelSerializer):
    """对话记录序列化器"""
    
    class Meta:
        model = Conversation
        fields = ['id', 'agent', 'user_message', 'assistant_message', 'context', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChatRequestSerializer(serializers.Serializer):
    """对话请求序列化器"""
    message = serializers.CharField(required=True, help_text='用户消息')
    context = serializers.JSONField(required=False, default=dict, help_text='上下文信息')
    
    class Meta:
        ref_name = 'AgentChatRequest'
