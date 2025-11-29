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


class PluginListSerializer(serializers.ModelSerializer):
    """插件列表序列化器"""
    
    class Meta:
        model = Plugin
        fields = ['id', 'name', 'description', 'status', 'created_at', 'updated_at']


class PluginCreateUpdateSerializer(serializers.ModelSerializer):
    """专门用于 create/update 的序列化器，前端直接传 OpenAPI JSON"""

    openapi_spec = serializers.JSONField()
    status = serializers.CharField(required=False, default='enabled')

    class Meta:
        model = Plugin
        fields = ['openapi_spec', 'status']

    def validate_openapi_spec(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError('OpenAPI规范必须是JSON对象')
        for field in ['openapi', 'info', 'servers', 'paths']:
            if field not in value:
                raise serializers.ValidationError(f'OpenAPI规范缺少必需字段: {field}')
        return value

    def create(self, validated_data):
        openapi_spec = validated_data.pop('openapi_spec')
        status = validated_data.pop('status', 'enabled')
        auth_config = openapi_spec.get('auth_config', {})

        name = openapi_spec['info']['title']
        description = openapi_spec['info']['description']
        base_url = openapi_spec['servers'][0]['url']

        return Plugin.objects.create(
            name=name,
            description=description,
            base_url=base_url,
            openapi_spec=openapi_spec,
            auth_config=auth_config,
            status=status,
            **validated_data
        )

    def update(self, instance, validated_data):
        openapi_spec = validated_data.get('openapi_spec', instance.openapi_spec)
        status = validated_data.get('status', instance.status)
        auth_config = openapi_spec.get('auth_config', instance.auth_config)

        instance.openapi_spec = openapi_spec
        instance.name = openapi_spec['info']['title']
        instance.description = openapi_spec['info']['description']
        instance.base_url = openapi_spec['servers'][0]['url']
        instance.auth_config = auth_config
        instance.status = status
        instance.save()
        return instance
