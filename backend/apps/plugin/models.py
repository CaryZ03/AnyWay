"""
插件模型定义
"""
from django.db import models


class Plugin(models.Model):
    """插件模型"""
    
    STATUS_CHOICES = [
        ('enabled', '启用'),
        ('disabled', '禁用'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=100, verbose_name='插件名称')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    openapi_spec = models.JSONField(verbose_name='OpenAPI规范')
    base_url = models.CharField(max_length=500, verbose_name='基础URL')
    auth_config = models.JSONField(default=dict, verbose_name='认证配置')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='enabled',
        verbose_name='状态'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    deleted = models.BooleanField(default=False, verbose_name='逻辑删除')
    
    class Meta:
        db_table = 'plugin'
        verbose_name = '插件'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.name
