"""
知识库模型定义
"""
from django.db import models


class KnowledgeBase(models.Model):
    """知识库模型"""
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=100, verbose_name='知识库名称')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    embedding_model = models.CharField(
        max_length=100,
        default='text-embedding-ada-002',
        verbose_name='嵌入模型'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    deleted = models.BooleanField(default=False, verbose_name='逻辑删除')
    
    class Meta:
        db_table = 'knowledge_base'
        verbose_name = '知识库'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.name


class Document(models.Model):
    """文档模型"""
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    knowledge_base = models.ForeignKey(
        KnowledgeBase,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='知识库'
    )
    filename = models.CharField(max_length=255, verbose_name='文件名')
    file_path = models.CharField(max_length=500, verbose_name='文件路径')
    file_type = models.CharField(max_length=50, verbose_name='文件类型')
    file_size = models.BigIntegerField(verbose_name='文件大小（字节）')
    content = models.TextField(blank=True, null=True, verbose_name='文档内容')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='处理状态'
    )
    error_message = models.TextField(blank=True, null=True, verbose_name='错误信息')
    chunk_count = models.IntegerField(default=0, verbose_name='分块数量')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    processed_at = models.DateTimeField(blank=True, null=True, verbose_name='处理时间')
    
    class Meta:
        db_table = 'document'
        verbose_name = '文档'
        verbose_name_plural = verbose_name
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['knowledge_base', 'status']),
            models.Index(fields=['uploaded_at']),
        ]
    
    def __str__(self):
        return self.filename


class DocumentChunk(models.Model):
    """文档分块模型"""
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='chunks',
        verbose_name='文档'
    )
    content = models.TextField(verbose_name='分块内容')
    chunk_index = models.IntegerField(verbose_name='分块索引')
    embedding = models.JSONField(blank=True, null=True, verbose_name='向量嵌入')
    metadata = models.JSONField(default=dict, verbose_name='元数据')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'document_chunk'
        verbose_name = '文档分块'
        verbose_name_plural = verbose_name
        ordering = ['document', 'chunk_index']
        indexes = [
            models.Index(fields=['document', 'chunk_index']),
        ]
    
    def __str__(self):
        return f'{self.document.filename} - Chunk {self.chunk_index}'
