import pytest
from django.test import override_settings
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

VALID_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "Hello API"},
    "servers": [{"url": "https://api.example.com"}],
    "paths": {
        "/hello": {
            "get": {"operationId": "helloOp", "description": "Say hello"}
        }
    },
}


@override_settings(ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"])
def test_plugin_crud_enable_disable_flow():
    client = APIClient()

    # 注册插件
    create_resp = client.post("/api/v1/plugins/", {"openapi_spec": VALID_SPEC}, format="json")
    assert create_resp.status_code == 201
    plugin_id = create_resp.json().get("data", {}).get("id")

    # 列表/详情
    list_resp = client.get("/api/v1/plugins/")
    assert list_resp.status_code == 200
    assert any(p["id"] == plugin_id for p in list_resp.json().get("data", []))

    detail_resp = client.get(f"/api/v1/plugins/{plugin_id}/")
    assert detail_resp.status_code == 200

    # 禁用 → 启用
    disable_resp = client.post(f"/api/v1/plugins/{plugin_id}/disable/")
    assert disable_resp.status_code == 200
    enable_resp = client.post(f"/api/v1/plugins/{plugin_id}/enable/")
    assert enable_resp.status_code == 200

    # 逻辑删除后列表不再返回
    del_resp = client.delete(f"/api/v1/plugins/{plugin_id}/")
    assert del_resp.status_code == 200
    list_after = client.get("/api/v1/plugins/")
    assert all(p["id"] != plugin_id for p in list_after.json().get("data", []))

