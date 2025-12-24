import pytest
from unittest.mock import patch
from django.test import override_settings
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_workflow_execute_basic_success():
    # 基础执行路径，Engine.execute 被 mock，返回 completed
    client = APIClient()
    definition = {
        "nodes": [
            {"id": "start", "type": "start"},
            {"id": "end", "type": "end"},
        ],
        "edges": [
            {"source": "start", "target": "end"},
        ],
    }
    wf_resp = client.post(
        "/api/v1/workflows/",
        {"name": "Flow", "description": "d", "definition": definition, "status": "active"},
        format="json",
    )
    assert wf_resp.status_code == 201
    wf_id = wf_resp.json().get("data", {}).get("id")

    def fake_execute(workflow, input_data, execution):
        execution.status = "completed"
        execution.output_data = {"answer": "ok"}
        execution.save(update_fields=["status", "output_data"])
        return execution.output_data

    with patch("apps.workflow.views.WorkflowEngine.execute", side_effect=fake_execute):
        exec_resp = client.post(
            f"/api/v1/workflows/{wf_id}/execute/",
            {"input_data": {"user_input": "hi"}},
            format="json",
        )
    assert exec_resp.status_code == 200
    data = exec_resp.json().get("data", {})
    assert data.get("status") == "completed"

