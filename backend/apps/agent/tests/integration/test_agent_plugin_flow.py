import os
from unittest.mock import MagicMock, patch
from django.test import override_settings

import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

VALID_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "Hello API"},
    "servers": [{"url": "https://api.example.com"}],
    "paths": {
        "/hello": {
            "get": {
                "operationId": "helloOp",
                "description": "Say hello",
                "parameters": []
            }
        }
    }
}


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_agent_chat_with_plugin_toolchain(tmp_path):
    client = APIClient()

    # 创建插件
    plugin_resp = client.post(
        "/api/v1/plugins/",
        {"openapi_spec": VALID_SPEC, "status": "enabled"},
        format="json",
    )
    assert plugin_resp.status_code == 201
    plugin_id = plugin_resp.json().get("data", {}).get("id")

    # 创建 Agent
    agent_resp = client.post(
        "/api/v1/agents/",
        {"name": "A1", "system_prompt": "You are helpful"},
        format="json",
    )
    assert agent_resp.status_code == 201
    agent_id = agent_resp.json().get("data", {}).get("id")

    # 绑定插件
    bind_resp = client.post(
        f"/api/v1/agents/{agent_id}/add_plugins/",
        {"plugin_ids": [plugin_id]},
        format="json",
    )
    assert bind_resp.status_code == 200

    # 构造 LLM 与插件 HTTP 的假响应
    first = MagicMock()
    first.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "first",
                    "tool_calls": [
                        {"function": {"name": "helloOp", "arguments": "{}"}}
                    ],
                }
            }
        ]
    }
    first.raise_for_status.return_value = None

    second = MagicMock()
    second.json.return_value = {"choices": [{"message": {"content": "final"}}]}
    second.raise_for_status.return_value = None

    fake_plugin_resp = MagicMock()
    fake_plugin_resp.json.return_value = {"msg": "hi"}
    fake_plugin_resp.text = ""
    fake_plugin_resp.status_code = 200
    fake_plugin_resp.raise_for_status.return_value = None

    with patch.dict(os.environ, {"ARK_API_KEY": "test-key", "ARK_API_BASE": "http://fake"}, clear=False):
        with patch("requests.Session.post", side_effect=[first, second]) as llm_post, \
             patch("requests.get", return_value=fake_plugin_resp) as plugin_get:
            chat_resp = client.post(
                f"/api/v1/agents/{agent_id}/chat/",
                {"message": "hi"},
                format="json",
            )
    assert chat_resp.status_code == 200
    assistant = chat_resp.json().get("data", {}).get("assistant_message")
    assert assistant == "final"
    assert llm_post.call_count == 2
    assert plugin_get.called
