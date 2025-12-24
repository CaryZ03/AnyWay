import pytest
from unittest.mock import patch
from django.test import override_settings
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_workflow_http_node_failure_returns_5xx():
    # HTTP 节点异常时，执行接口应返回 5xx
    client = APIClient()
    definition = {
        "nodes": [
            {"id": "start", "type": "start"},
            {"id": "http1", "type": "http"},
            {"id": "end", "type": "end"},
        ],
        "edges": [
            {"source": "start", "target": "http1"},
            {"source": "http1", "target": "end"},
        ],
    }
    wf_resp = client.post(
        "/api/v1/workflows/",
        {"name": "Flow", "description": "d", "definition": definition, "status": "active"},
        format="json",
    )
    wf_id = wf_resp.json().get("data", {}).get("id")

    with patch("requests.request", side_effect=Exception("http fail")):
        exec_resp = client.post(
            f"/api/v1/workflows/{wf_id}/execute/",
            {"input_data": {"user_input": "hi"}},
            format="json",
        )
    assert exec_resp.status_code >= 500

