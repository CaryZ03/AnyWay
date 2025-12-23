from unittest.mock import MagicMock, patch

import pytest
from django.test import override_settings
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


VALID_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "Hello API"},
    "servers": [{"url": "https://api.example.com"}],
    "paths": {
        "/hello/{name}": {
            "get": {
                "operationId": "helloOp",
                "parameters": [
                    {"in": "path", "name": "name", "schema": {"type": "string"}, "required": True}
                ],
                "description": "Say hello",
            }
        }
    },
}


@override_settings(ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"])
def test_plugin_operation_call_integration():
    client = APIClient()

    create_resp = client.post("/api/v1/plugins/", {"openapi_spec": VALID_SPEC}, format="json")
    assert create_resp.status_code == 201
    plugin_id = create_resp.json().get("data", {}).get("id")

    fake_resp = MagicMock()
    fake_resp.json.return_value = {"msg": "hi bob"}
    fake_resp.text = ""
    fake_resp.status_code = 200
    fake_resp.raise_for_status.return_value = None

    with patch("requests.get", return_value=fake_resp) as mock_get:
        resp = client.post(
            f"/api/v1/plugins/{plugin_id}/call/",
            {"operation_id": "helloOp", "params": {"name": "bob"}},
            format="json",
        )
    assert resp.status_code == 200
    data = resp.json().get("data", {})
    assert data.get("data", {}).get("msg") == "hi bob"
    assert mock_get.called
