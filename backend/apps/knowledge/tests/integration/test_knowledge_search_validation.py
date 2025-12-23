import pytest
from django.test import override_settings
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_search_requires_query_and_top_k_bounds():
    client = APIClient()
    kb_resp = client.post("/api/v1/knowledge/", {"name": "KB", "description": "d"}, format="json")
    assert kb_resp.status_code == 201
    kb_id = kb_resp.json().get("data", {}).get("id")

    # 缺少 query 应返回 400
    resp_missing = client.post(f"/api/v1/knowledge/{kb_id}/search/", {"top_k": 5}, format="json")
    assert resp_missing.status_code == 400

    # top_k 过大应返回 400
    resp_topk = client.post(
        f"/api/v1/knowledge/{kb_id}/search/",
        {"query": "hi", "top_k": 50},
        format="json",
    )
    assert resp_topk.status_code == 400

