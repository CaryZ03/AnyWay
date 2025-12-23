import json
from unittest.mock import MagicMock, patch

import pytest
from django.test import override_settings
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

COMPLEX_DEF = {
    "nodes": [
        {"id": "start", "type": "start"},
        {"id": "intent", "type": "intent", "config": {"intents": [{"id": "a", "name": "A"}]}},
        {"id": "http", "type": "http", "config": {"url": "https://api.example.com/data", "method": "GET"}},
        {"id": "kb", "type": "knowledge", "config": {"knowledge_base_id": 1, "query": "{intent.intent_name}"}},
        {"id": "end", "type": "end"},
    ],
    "edges": [
        {"source": "start", "target": "intent"},
        {"source": "intent", "target": "http"},
        {"source": "http", "target": "kb"},
        {"source": "kb", "target": "end"},
    ],
}


@override_settings(ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"])
def test_workflow_complex_flow_executes_with_mocks():
    client = APIClient()

    # 创建 workflow
    create_resp = client.post(
        "/api/v1/workflows/",
        {"name": "wf", "definition": COMPLEX_DEF, "status": "draft"},
        format="json",
    )
    assert create_resp.status_code == 201
    wf_id = create_resp.json()["data"]["id"]

    # Dummy LLM for intent node
    class DummyLLM:
        def chat(self, *args, **kwargs):
            return json.dumps({"intent_id": "a", "intent_name": "A", "reason": "match"})

    fake_http_resp = MagicMock()
    fake_http_resp.json.return_value = {"ok": True}
    fake_http_resp.text = ""
    fake_http_resp.status_code = 200
    fake_http_resp.headers = {}

    fake_kb_resp = MagicMock()
    fake_kb_resp.json.return_value = {
        "documents": ["doc"],
        "metadatas": [{"doc_id": 10}],
        "scores": [0.9],
    }
    fake_kb_resp.raise_for_status.return_value = None

    with patch("apps.workflow.services.get_llm_service", lambda provider: DummyLLM()), \
         patch("apps.workflow.services.requests.request", return_value=fake_http_resp), \
         patch("apps.workflow.services.requests.post", return_value=fake_kb_resp):
        exec_resp = client.post(
            f"/api/v1/workflows/{wf_id}/execute/",
            {"input_data": {"user_input": "hi"}},
            format="json",
        )

    assert exec_resp.status_code == 200
    body = exec_resp.json()
    assert body.get("data", {}).get("status") in ("completed", "running")
    assert body.get("data", {}).get("node_status") is not None
    assert body.get("success") is True

