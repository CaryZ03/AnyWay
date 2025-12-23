from unittest.mock import patch

import pytest
from django.test import override_settings
from rest_framework.test import APIClient

from apps.workflow.models import WorkflowExecution

pytestmark = pytest.mark.django_db

VALID_DEF = {
    "nodes": [
        {"id": "start", "type": "start"},
        {"id": "end", "type": "end"},
    ],
    "edges": [
        {"source": "start", "target": "end"},
    ],
}


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_workflow_execute_flow():
    client = APIClient()

    create_resp = client.post(
        "/api/v1/workflows/",
        {"name": "wf", "description": "d", "definition": VALID_DEF, "status": "draft"},
        format="json",
    )
    assert create_resp.status_code == 201
    wf_id = create_resp.json()["data"]["id"]

    def fake_execute(workflow, input_data, execution):
        execution.status = "completed"
        execution.output_data = {"answer": "ok"}
        execution.node_status = {"start": {"status": "success"}, "end": {"status": "success"}}
        execution.save(update_fields=["status", "output_data", "node_status"])
        return execution.output_data

    with patch("apps.workflow.views.WorkflowEngine.execute", side_effect=fake_execute):
        exec_resp = client.post(
            f"/api/v1/workflows/{wf_id}/execute/",
            {"input_data": {"user_input": "hi"}},
            format="json",
        )
    assert exec_resp.status_code == 200
    body = exec_resp.json()
    assert body.get("data", {}).get("status") == "completed"
    assert WorkflowExecution.objects.filter(workflow_id=wf_id).count() == 1

