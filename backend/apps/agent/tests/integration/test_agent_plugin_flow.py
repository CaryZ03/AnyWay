import os
from unittest.mock import MagicMock, patch

import pytest
from django.test import override_settings
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

VALID_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "P1", "description": "d"},
    "servers": [{"url": "https://api.example.com"}],
    "paths": {
        "/hello": {
            "get": {"operationId": "helloOp"}
        }
    }
}


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_agent_chat_with_plugin_toolchain(tmp_path):
    # 集成链路：注册插件->创建绑定智能体->对话产生 tool_call -> 插件 HTTP -> 二次 LLM
    client = APIClient()

    # 创建插件
    plugin_resp = client.post(
        "/api/v1/plugins/",
        {"openapi_spec": VALID_SPEC, "status": "enabled", "name": "P1"},
        format="json",
    )
    assert plugin_resp.status_code == 201
    plugin_id = plugin_resp.json().get("data", {}).get("id")

    # 创建智能体并绑定插件
    agent_resp = client.post(
        "/api/v1/agents/",
        {
            "name": "A1",
            "system_prompt": "You are helpful",
            "model_config": {"provider": "volcano", "model": "demo"},
            "plugin_ids": [plugin_id],
        },
        format="json",
    )
    assert agent_resp.status_code == 201
    agent_id = agent_resp.json().get("data", {}).get("id")

    # LLM 第一次返回 tool_calls，第二次返回最终内容
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

    # 插件 HTTP mock
    fake_plugin_resp = MagicMock()
    fake_plugin_resp.json.return_value = {"msg": "hi"}
    fake_plugin_resp.text = ""
    fake_plugin_resp.status_code = 200
    fake_plugin_resp.raise_for_status.return_value = None

    with patch.dict(os.environ, {"ARK_API_KEY": "k", "ARK_API_BASE": "http://fake"}, clear=False):
        with patch("requests.Session.post", side_effect=[first, second]) as llm_post, \
             patch("requests.get", return_value=fake_plugin_resp) as plugin_get:
            chat_resp = client.post(
                f"/api/v1/agents/{agent_id}/chat/",
                {"message": "hi"},
                format="json",
            )

    assert chat_resp.status_code == 200
    data = chat_resp.json().get("data", {})
    assert data.get("assistant_message") == "final"
    assert llm_post.call_count == 2
    assert plugin_get.called
