"""
智能体模型定义
"""
from django.db import models
from django.contrib.auth.models import User


class Agent(models.Model):
    """智能体模型"""
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=100, verbose_name='智能体名称')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    system_prompt = models.TextField(blank=True, null=True, verbose_name='系统提示词')
    user_prompt_template = models.TextField(blank=True, null=True, verbose_name='用户提示词模板')
    model_config = models.JSONField(default=dict, verbose_name='模型配置')
    workflow_id = models.BigIntegerField(blank=True, null=True, verbose_name='关联工作流ID')
    knowledge_base_ids = models.JSONField(default=list, verbose_name='关联知识库ID列表')
    plugin_ids = models.JSONField(default=list, verbose_name='关联插件ID列表')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='状态'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    deleted = models.BooleanField(default=False, verbose_name='逻辑删除')
    
    class Meta:
        db_table = 'agent'
        verbose_name = '智能体'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.name


class Conversation(models.Model):
    """对话记录模型"""
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='conversations',
        verbose_name='智能体'
    )
    user_message = models.TextField(verbose_name='用户消息')
    assistant_message = models.TextField(verbose_name='助手回复')
    context = models.JSONField(default=dict, verbose_name='上下文信息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'conversation'
        verbose_name = '对话记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agent', 'created_at']),
        ]
    
    def __str__(self):
        return f'{self.agent.name} - {self.created_at}'
