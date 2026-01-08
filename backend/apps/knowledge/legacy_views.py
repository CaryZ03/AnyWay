"""
兼容 Postman 文档的知识库接口

这些接口保持了 /kb/* 的路径形式，方便前端直接对接，
内部复用现有的模型与序列化器，避免破坏已有 /api/v1/knowledge/ 路由。
"""
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser

from .models import KnowledgeBase, Document
from .serializers import (
    KnowledgeBaseSerializer,
    DocumentSerializer,
    DocumentUploadSerializer,
    SearchRequestSerializer,
)
from utils.response import ApiResponse


@api_view(["GET"])
def list_knowledge_bases(request):
    """GET /kb/list?user_id=1"""
    queryset = KnowledgeBase.objects.filter(deleted=False)
    serializer = KnowledgeBaseSerializer(queryset, many=True)
    return ApiResponse.success(data=serializer.data, message="获取知识库列表成功")


@api_view(["POST"])
def create_knowledge_base(request):
    """POST /kb/create"""
    serializer = KnowledgeBaseSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return ApiResponse.created(data=serializer.data, message="知识库创建成功")


@api_view(["GET"])
def get_documents(request):
    """GET /kb/documents?user_id=1&knowledge_base_id=1"""
    kb_id = request.query_params.get("knowledge_base_id") or request.query_params.get(
        "knowledge_base"
    )
    if not kb_id:
        return ApiResponse.error(message="缺少参数 knowledge_base_id")

    knowledge_base = get_object_or_404(
        KnowledgeBase, pk=kb_id, deleted=False
    )
    documents = knowledge_base.documents.all()
    serializer = DocumentSerializer(documents, many=True)
    return ApiResponse.success(data=serializer.data, message="获取文档列表成功")


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def upload_document(request):
    """POST /kb/upload"""
    kb_id = request.data.get("knowledge_base_id") or request.data.get("knowledge_base")
    if not kb_id:
        return ApiResponse.error(message="缺少参数 knowledge_base_id")

    knowledge_base = get_object_or_404(
        KnowledgeBase, pk=kb_id, deleted=False
    )

    upload_serializer = DocumentUploadSerializer(data=request.data)
    upload_serializer.is_valid(raise_exception=True)

    uploaded_file = upload_serializer.validated_data["file"]
    file_path = f"knowledge_base/{knowledge_base.id}/{uploaded_file.name}"
    saved_path = default_storage.save(file_path, uploaded_file)

    document = Document.objects.create(
        knowledge_base=knowledge_base,
        filename=uploaded_file.name,
        file_path=saved_path,
        file_type=uploaded_file.name.split(".")[-1],
        file_size=uploaded_file.size,
        status="pending",
    )

    doc_serializer = DocumentSerializer(document)
    return ApiResponse.created(
        data=doc_serializer.data, message="文档上传成功，正在处理中"
    )


@api_view(["DELETE"])
def delete_knowledge_base(request):
    """DELETE /kb/delete?user_id=1&knowledge_base_id=1"""
    kb_id = request.query_params.get("knowledge_base_id") or request.query_params.get(
        "knowledge_base"
    )
    if not kb_id:
        return ApiResponse.error(message="缺少参数 knowledge_base_id")

    knowledge_base = get_object_or_404(
        KnowledgeBase, pk=kb_id, deleted=False
    )
    knowledge_base.deleted = True
    knowledge_base.save()
    return ApiResponse.success(message="知识库删除成功")


@api_view(["DELETE"])
def delete_document(request, doc_id: int):
    """DELETE /kb/document/<doc_id>?user_id=1"""
    document = get_object_or_404(Document, pk=doc_id)
    document.delete()
    return ApiResponse.success(message="文档删除成功")


@api_view(["POST"])
def query_knowledge_base(request):
    """POST /kb/query"""
    serializer = SearchRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # TODO: 接入向量检索，这里先返回空结果保持接口兼容
    return ApiResponse.success(data=[], message="查询完成")
