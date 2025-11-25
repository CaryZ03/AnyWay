"""
知识库序列化器
"""
from rest_framework import serializers
from .models import KnowledgeBase, Document, DocumentChunk


class KnowledgeBaseSerializer(serializers.ModelSerializer):
    """知识库序列化器"""
    document_count = serializers.SerializerMethodField()
    
    class Meta:
        model = KnowledgeBase
        fields = [
            'id', 'name', 'description', 'embedding_model',
            'document_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_document_count(self, obj):
        """获取文档数量"""
        return obj.documents.count()


class DocumentSerializer(serializers.ModelSerializer):
    """文档序列化器"""
    
    class Meta:
        model = Document
        fields = [
            'id', 'knowledge_base', 'filename', 'file_type',
            'file_size', 'status', 'error_message', 'chunk_count',
            'uploaded_at', 'processed_at'
        ]
        read_only_fields = [
            'id', 'file_size', 'status', 'error_message',
            'chunk_count', 'uploaded_at', 'processed_at'
        ]


class DocumentUploadSerializer(serializers.Serializer):
    """文档上传序列化器"""
    file = serializers.FileField(required=True, help_text='文档文件（TXT或Markdown）')
    
    def validate_file(self, value):
        """验证文件类型"""
        allowed_types = ['.txt', '.md', '.markdown']
        file_ext = value.name.lower().split('.')[-1]
        
        if f'.{file_ext}' not in allowed_types:
            raise serializers.ValidationError(
                f'不支持的文件类型。仅支持: {", ".join(allowed_types)}'
            )
        
        # 验证文件大小（最大10MB）
        max_size = 10 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError('文件大小不能超过10MB')
        
        return value


class DocumentChunkSerializer(serializers.ModelSerializer):
    """文档分块序列化器"""
    
    class Meta:
        model = DocumentChunk
        fields = ['id', 'document', 'content', 'chunk_index', 'metadata', 'created_at']
        read_only_fields = ['id', 'created_at']


class SearchRequestSerializer(serializers.Serializer):
    """知识库搜索请求序列化器"""
    query = serializers.CharField(required=True, help_text='搜索查询')
    top_k = serializers.IntegerField(default=5, min_value=1, max_value=20, help_text='返回结果数量')
