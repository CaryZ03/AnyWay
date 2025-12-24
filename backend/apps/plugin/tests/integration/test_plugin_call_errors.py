import pytest
from django.test import override_settings
from rest_framework.test import APIClient
from unittest.mock import patch
from requests.exceptions import RequestException

pytestmark = pytest.mark.django_db


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_plugin_call_http_error():
    # 插件调用 HTTP 异常时应返回失败
    client = APIClient()
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Demo", "description": "d"},
        "servers": [{"url": "https://api.example.com"}],
        "paths": {"/hello": {"get": {"operationId": "helloOp"}}},
    }
    reg_resp = client.post("/api/v1/plugins/", {"openapi_spec": spec, "status": "enabled"}, format="json")
    plugin_id = reg_resp.json().get("data", {}).get("id")
    with patch("requests.get", side_effect=RequestException("bad http")):
        call_resp = client.post(
            f"/api/v1/plugins/{plugin_id}/call/",
            {"operation_id": "helloOp", "parameters": {}},
            format="json",
        )
    assert call_resp.status_code in (500, 200)
    body = call_resp.json()
    if call_resp.status_code == 200:
        assert body.get("data", {}).get("success") is False or "错误" in body.get("message", "")
    else:
        assert body.get("success") is False
