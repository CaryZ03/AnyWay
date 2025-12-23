import shutil
import tempfile

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_knowledge_document_flow():
    client = APIClient()
    tmpdir = tempfile.mkdtemp()
    try:
        # 创建知识库
        kb_resp = client.post("/api/v1/knowledge/", {"name": "KB", "description": "d"}, format="json")
        assert kb_resp.status_code == 201
        kb_id = kb_resp.json().get("data", {}).get("id")

        # 上传文档
        upload = SimpleUploadedFile("note.txt", b"hello world", content_type="text/plain")
        up_resp = client.post(f"/api/v1/knowledge/{kb_id}/upload/", {"file": upload}, format="multipart")
        assert up_resp.status_code == 201
        doc_id = up_resp.json().get("data", {}).get("id")

        # 列表文档
        list_resp = client.get(f"/api/v1/knowledge/{kb_id}/documents/")
        assert list_resp.status_code == 200
        docs = list_resp.json().get("data")
        assert any(d["id"] == doc_id for d in docs)

        # 搜索（占位，当前返回空列表）
        search_resp = client.post(
            f"/api/v1/knowledge/{kb_id}/search/",
            {"query": "hello", "top_k": 3},
            format="json",
        )
        assert search_resp.status_code == 200
        assert search_resp.json().get("data") in ([], None)

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

