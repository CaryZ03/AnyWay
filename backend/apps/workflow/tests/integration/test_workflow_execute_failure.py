import pytest
from django.test import override_settings
from rest_framework.test import APIClient
from unittest.mock import patch

from apps.workflow.services import WorkflowExecutionError

pytestmark = pytest.mark.django_db

VALID_DEF = {
    "nodes": [{"id": "start", "type": "start"}, {"id": "end", "type": "end"}],
    "edges": [{"source": "start", "target": "end"}],
}


@override_settings(ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"])
def test_workflow_execute_failure_returns_500():
    client = APIClient()
    create_resp = client.post(
        "/api/v1/workflows/",
        {"name": "wf", "definition": VALID_DEF, "status": "draft"},
        format="json",
    )
    assert create_resp.status_code == 201
    wf_id = create_resp.json()["data"]["id"]

    with patch("apps.workflow.views.WorkflowEngine.execute", side_effect=WorkflowExecutionError("boom")):
        exec_resp = client.post(
            f"/api/v1/workflows/{wf_id}/execute/",
            {"input_data": {"user_input": "hi"}},
            format="json",
        )
    assert exec_resp.status_code == 500
    body = exec_resp.json()
    assert body.get("success") is False
    assert "失败" in body.get("message", "")

