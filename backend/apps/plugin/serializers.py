"""
插件序列化器
"""
from rest_framework import serializers
from .models import Plugin
import logging

logger = logging.getLogger(__name__)


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


class PluginCreateUpdateSerializer(serializers.Serializer):
    """专门用于 create/update 的序列化器，前端直接传 OpenAPI JSON
    使用 Serializer 而不是 ModelSerializer，避免自动验证模型字段
    """

    openapi_spec = serializers.JSONField()
    status = serializers.CharField(required=False, default='enabled')
    
    def to_internal_value(self, data):
        """
        重写此方法，只提取我们需要的字段，忽略其他字段
        这样可以避免前端意外发送 name、base_url 等字段时触发验证错误
        """
        # 只提取 openapi_spec 和 status 字段
        internal_value = {}
        if 'openapi_spec' in data:
            internal_value['openapi_spec'] = data['openapi_spec']
        if 'status' in data:
            internal_value['status'] = data['status']
        # 忽略其他字段（如 name、base_url、description 等）
        # 这些字段会在 create/update 方法中从 openapi_spec 中提取
        return super().to_internal_value(internal_value)

    def validate_openapi_spec(self, value):
        logger.info(f'验证 OpenAPI 规范，接收到的数据: {value}')
        
        if not isinstance(value, dict):
            logger.warning('OpenAPI规范不是JSON对象')
            raise serializers.ValidationError('OpenAPI规范必须是JSON对象')
        
        # 检查必需字段
        for field in ['openapi', 'info', 'servers', 'paths']:
            if field not in value:
                logger.warning(f'OpenAPI规范缺少必需字段: {field}')
                raise serializers.ValidationError(f'OpenAPI规范缺少必需字段: {field}')
        
        # 检查 info 字段
        info = value.get('info', {})
        if not isinstance(info, dict):
            logger.warning('OpenAPI规范中的info字段不是对象')
            raise serializers.ValidationError('OpenAPI规范中的info字段必须是对象')
        
        # 检查 info.title（必需）
        if 'title' not in info or not info.get('title'):
            logger.warning(f'OpenAPI规范中的info.title字段为空，info: {info}')
            raise serializers.ValidationError('OpenAPI规范中的info.title字段不能为空')
        
        # 检查 servers 字段
        servers = value.get('servers', [])
        if not isinstance(servers, list) or len(servers) == 0:
            logger.warning(f'OpenAPI规范中的servers字段无效，servers: {servers}')
            raise serializers.ValidationError('OpenAPI规范中的servers字段必须是非空数组')
        
        # 检查 servers[0].url（必需）
        first_server = servers[0]
        if not isinstance(first_server, dict):
            logger.warning(f'OpenAPI规范中的servers[0]不是对象，servers[0]: {first_server}')
            raise serializers.ValidationError('OpenAPI规范中的servers[0]必须是对象')
        
        if 'url' not in first_server or not first_server.get('url'):
            logger.warning(f'OpenAPI规范中的servers[0].url字段为空，servers[0]: {first_server}')
            raise serializers.ValidationError('OpenAPI规范中的servers[0].url字段不能为空')
        
        logger.info('OpenAPI 规范验证通过')
        return value

    def create(self, validated_data):
        openapi_spec = validated_data.pop('openapi_spec')
        status = validated_data.pop('status', 'enabled')
        auth_config = openapi_spec.get('auth_config', {})

        # 安全地提取字段，使用 .get() 方法并提供默认值
        info = openapi_spec.get('info', {})
        name = info.get('title', '')
        description = info.get('description', '') or ''
        
        servers = openapi_spec.get('servers', [])
        if servers and len(servers) > 0:
            base_url = servers[0].get('url', '')
        else:
            base_url = ''

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

        # 安全地提取字段，使用 .get() 方法并提供默认值
        info = openapi_spec.get('info', {})
        name = info.get('title', instance.name)
        description = info.get('description', '') or ''
        
        servers = openapi_spec.get('servers', [])
        if servers and len(servers) > 0:
            base_url = servers[0].get('url', instance.base_url)
        else:
            base_url = instance.base_url

        instance.openapi_spec = openapi_spec
        instance.name = name
        instance.description = description
        instance.base_url = base_url
        instance.auth_config = auth_config
        instance.status = status
        instance.save()
        return instance
