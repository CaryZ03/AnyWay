import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import serializers

from apps.knowledge.serializers import (
    DocumentUploadSerializer,
    KnowledgeBaseSerializer,
    SearchRequestSerializer,
)
from apps.knowledge.models import KnowledgeBase, Document


pytestmark = pytest.mark.django_db(strict=True)


def test_document_upload_serializer_rejects_bad_extension():
    upload = SimpleUploadedFile("file.pdf", b"bad", content_type="application/pdf")
    serializer = DocumentUploadSerializer(data={"file": upload})
    with pytest.raises(serializers.ValidationError):
        serializer.is_valid(raise_exception=True)


def test_document_upload_serializer_rejects_too_large():
    big_content = b"a" * (10 * 1024 * 1024 + 1)  # just over 10MB
    upload = SimpleUploadedFile("file.txt", big_content, content_type="text/plain")
    serializer = DocumentUploadSerializer(data={"file": upload})
    with pytest.raises(serializers.ValidationError):
        serializer.is_valid(raise_exception=True)


def test_knowledge_base_serializer_document_count():
    kb = KnowledgeBase.objects.create(name="KB")
    Document.objects.create(
        knowledge_base=kb,
        filename="a.txt",
        file_path="/tmp/a.txt",
        file_type="txt",
        file_size=10,
        status="pending",
    )
    data = KnowledgeBaseSerializer(kb).data
    assert data["document_count"] == 1


def test_search_request_serializer_top_k_bounds():
    serializer = SearchRequestSerializer(data={"query": "hi", "top_k": 30})
    assert serializer.is_valid() is False
    serializer = SearchRequestSerializer(data={"query": "hi", "top_k": 5})
    assert serializer.is_valid() is True
