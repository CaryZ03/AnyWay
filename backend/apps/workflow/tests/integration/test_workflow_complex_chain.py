import pytest
from unittest.mock import MagicMock, patch
from django.test import override_settings
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_workflow_intent_http_knowledge_chain():
    # 覆盖 intent -> http -> knowledge -> end 的链路，全部外部调用 mock
    client = APIClient()

    definition = {
        "nodes": [
            {"id": "start", "type": "start"},
            {"id": "intent", "type": "intent", "config": {"intents": [{"id": "route", "name": "Route"}]}},
            {"id": "http1", "type": "http", "config": {"url": "https://api.example.com/ok", "method": "GET"}},
            {"id": "kb", "type": "knowledge", "config": {"knowledge_base_id": 1, "query": "hello", "top_k": 1}},
            {"id": "end", "type": "end"},
        ],
        "edges": [
            {"source": "start", "target": "intent"},
            {"source": "intent", "target": "http1"},
            {"source": "http1", "target": "kb"},
            {"source": "kb", "target": "end"},
        ],
    }

    wf_resp = client.post(
        "/api/v1/workflows/",
        {"name": "Flow", "description": "d", "definition": definition, "status": "active"},
        format="json",
    )
    assert wf_resp.status_code == 201
    wf_id = wf_resp.json().get("data", {}).get("id")

    class DummyLLM:
        def chat(self, *args, **kwargs):
            return '{"intent_id": "route", "intent_name": "Route"}'

    fake_http_resp = MagicMock()
    fake_http_resp.json.return_value = {"ok": True}
    fake_http_resp.text = ""
    fake_http_resp.status_code = 200
    fake_http_resp.headers = {}

    fake_kb_resp = MagicMock()
    fake_kb_resp.json.return_value = {"documents": ["d1"], "metadatas": [{}], "scores": [0.8]}
    fake_kb_resp.raise_for_status.return_value = None

    with patch("apps.workflow.services.get_llm_service", lambda provider=None: DummyLLM()), \
         patch("requests.request", return_value=fake_http_resp), \
         patch("requests.post", return_value=fake_kb_resp):
        exec_resp = client.post(
            f"/api/v1/workflows/{wf_id}/execute/",
            {"input_data": {"user_input": "hi"}},
            format="json",
        )
    assert exec_resp.status_code == 200
    data = exec_resp.json().get("data", {})
    assert data.get("status") == "completed"
