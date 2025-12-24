import pytest
from django.test import override_settings
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_knowledge_search_handles_missing_kb():
    # 不存在的知识库检索应返回 404/4xx
    client = APIClient()
    resp = client.post(
        "/api/v1/knowledge/999/search/",
        {"query": "hi", "top_k": 3},
        format="json",
    )
    # 应返回 404 或 4xx 错误
    assert resp.status_code in (404, 400)
