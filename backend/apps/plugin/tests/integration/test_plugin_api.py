import pytest
from django.test import override_settings
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock

pytestmark = pytest.mark.django_db


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_plugin_register_and_call():
    # 插件注册后调用 /call/ 端点（HTTP mock）
    client = APIClient()
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Demo", "description": "d"},
        "servers": [{"url": "https://api.example.com"}],
        "paths": {
            "/hello": {
                "get": {
                    "operationId": "helloOp"
                }
            }
        }
    }

    reg_resp = client.post("/api/v1/plugins/", {"openapi_spec": spec, "status": "enabled", "name": "Demo"}, format="json")
    assert reg_resp.status_code == 201
    plugin_id = reg_resp.json().get("data", {}).get("id")

    fake_resp = MagicMock()
    fake_resp.json.return_value = {"msg": "ok"}
    fake_resp.text = ""
    fake_resp.status_code = 200
    fake_resp.raise_for_status.return_value = None

    with patch('requests.get', return_value=fake_resp):
        call_resp = client.post(
            f"/api/v1/plugins/{plugin_id}/call/",
            {"operation_id": "helloOp", "parameters": {}},
            format="json"
        )
    assert call_resp.status_code == 200
    data = call_resp.json().get("data", {})
    assert data.get("data") == {"msg": "ok"}
    assert data.get("success") is True

