"""
知识库后台管理
"""
from django.contrib import admin
from .models import KnowledgeBase, Document, DocumentChunk


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'embedding_model', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'filename', 'knowledge_base', 'status', 'chunk_count', 'uploaded_at']
    list_filter = ['status', 'uploaded_at']
    search_fields = ['filename']
    readonly_fields = ['uploaded_at', 'processed_at']


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ['id', 'document', 'chunk_index', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
