"""
工作流模型定义
"""
from django.db import models


class Workflow(models.Model):
    """工作流模型"""
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('active', '激活'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=100, verbose_name='工作流名称')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    definition = models.JSONField(default=dict, verbose_name='工作流定义（节点和连线）')
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
        db_table = 'workflow'
        verbose_name = '工作流'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.name


class WorkflowExecution(models.Model):
    """工作流执行记录"""
    
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('running', '运行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='executions',
        verbose_name='工作流'
    )
    input_data = models.JSONField(default=dict, verbose_name='输入数据')
    output_data = models.JSONField(default=dict, verbose_name='输出数据')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='执行状态'
    )
    node_status = models.JSONField(default=dict, verbose_name='节点执行状态')
    error_message = models.TextField(blank=True, null=True, verbose_name='错误信息')
    started_at = models.DateTimeField(blank=True, null=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='完成时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'workflow_execution'
        verbose_name = '工作流执行记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workflow', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'{self.workflow.name} - {self.status}'
