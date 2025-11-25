"""
插件序列化器
"""
from rest_framework import serializers
from .models import Plugin


class PluginSerializer(serializers.ModelSerializer):
    """插件序列化器"""
    
    class Meta:
        model = Plugin
        fields = [
            'id', 'name', 'description', 'openapi_spec',
            'base_url', 'auth_config', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_openapi_spec(self, value):
        """验证OpenAPI规范格式"""
        if not isinstance(value, dict):
            raise serializers.ValidationError('OpenAPI规范必须是JSON对象')
        
        # 验证必需字段
        required_fields = ['openapi', 'info', 'paths']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f'OpenAPI规范缺少必需字段: {field}')
        
        return value


class PluginListSerializer(serializers.ModelSerializer):
    """插件列表序列化器"""
    
    class Meta:
        model = Plugin
        fields = ['id', 'name', 'description', 'status', 'created_at', 'updated_at']
