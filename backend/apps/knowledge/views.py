"""
知识库视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.files.storage import default_storage
import os

from .models import KnowledgeBase, Document
from .serializers import (
    KnowledgeBaseSerializer, DocumentSerializer,
    DocumentUploadSerializer, SearchRequestSerializer
)
from .tasks import process_document
from utils.response import ApiResponse


class KnowledgeBaseViewSet(viewsets.ModelViewSet):
    """
    知识库视图集
    
    提供知识库的CRUD操作
    """
    queryset = KnowledgeBase.objects.filter(deleted=False)
    serializer_class = KnowledgeBaseSerializer
    
    @swagger_auto_schema(
        operation_summary='获取知识库列表',
        operation_description='获取所有未删除的知识库列表',
        responses={200: KnowledgeBaseSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """获取知识库列表"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(data=serializer.data, message='获取知识库列表成功')
    
    @swagger_auto_schema(
        operation_summary='创建知识库',
        operation_description='创建新的知识库',
        request_body=KnowledgeBaseSerializer,
        responses={201: KnowledgeBaseSerializer()}
    )
    def create(self, request, *args, **kwargs):
        """创建知识库"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ApiResponse.created(data=serializer.data, message='知识库创建成功')
    
    @swagger_auto_schema(
        operation_summary='获取知识库详情',
        operation_description='根据ID获取知识库详细信息',
        responses={200: KnowledgeBaseSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        """获取知识库详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.success(data=serializer.data, message='获取知识库详情成功')
    
    @swagger_auto_schema(
        operation_summary='更新知识库',
        operation_description='更新知识库信息',
        request_body=KnowledgeBaseSerializer,
        responses={200: KnowledgeBaseSerializer()}
    )
    def update(self, request, *args, **kwargs):
        """更新知识库"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ApiResponse.success(data=serializer.data, message='知识库更新成功')
    
    @swagger_auto_schema(
        operation_summary='删除知识库',
        operation_description='逻辑删除知识库',
        responses={200: '删除成功'}
    )
    def destroy(self, request, *args, **kwargs):
        """删除知识库（逻辑删除）"""
        instance = self.get_object()
        instance.deleted = True
        instance.save()
        return ApiResponse.success(message='知识库删除成功')
    
    @swagger_auto_schema(
        operation_summary='上传文档',
        operation_description='上传文档到知识库',
        request_body=DocumentUploadSerializer,
        responses={201: DocumentSerializer()}
    )
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload(self, request, pk=None):
        """上传文档"""
        knowledge_base = self.get_object()
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        uploaded_file = serializer.validated_data['file']
        
        # 保存文件
        file_path = f'knowledge_base/{pk}/{uploaded_file.name}'
        saved_path = default_storage.save(file_path, uploaded_file)
        
        # 创建文档记录
        document = Document.objects.create(
            knowledge_base=knowledge_base,
            filename=uploaded_file.name,
            file_path=saved_path,
            file_type=uploaded_file.name.split('.')[-1],
            file_size=uploaded_file.size,
            status='pending'
        )
        
        # 异步处理文档
        # TODO: 使用Celery异步任务
        # process_document.delay(document.id)
        
        doc_serializer = DocumentSerializer(document)
        return ApiResponse.created(data=doc_serializer.data, message='文档上传成功，正在处理中')
    
    @swagger_auto_schema(
        operation_summary='获取文档列表',
        operation_description='获取知识库中的所有文档',
        responses={200: DocumentSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """获取文档列表"""
        knowledge_base = self.get_object()
        documents = knowledge_base.documents.all()
        serializer = DocumentSerializer(documents, many=True)
        return ApiResponse.success(data=serializer.data, message='获取文档列表成功')
    
    @swagger_auto_schema(
        operation_summary='搜索知识库',
        operation_description='在知识库中搜索相关内容',
        request_body=SearchRequestSerializer,
        responses={200: openapi.Response('搜索成功', DocumentSerializer(many=True))}
    )
    @action(detail=True, methods=['post'])
    def search(self, request, pk=None):
        """搜索知识库"""
        knowledge_base = self.get_object()
        serializer = SearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        query = serializer.validated_data['query']
        top_k = serializer.validated_data['top_k']
        
        # TODO: 实现向量搜索
        # 1. 将查询转换为向量
        # 2. 在向量数据库中搜索相似文档块
        # 3. 返回最相关的结果
        
        results = []
        return ApiResponse.success(data=results, message='搜索完成')
