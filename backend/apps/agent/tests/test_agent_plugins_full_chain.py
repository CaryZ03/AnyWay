import json
import os
from unittest.mock import patch, MagicMock

from django.test import override_settings
from rest_framework.test import APITestCase

from apps.agent.models import Agent, Conversation
from apps.plugin.models import Plugin

VALID_SPEC = {
    "openapi": "3.0.0",
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
class AgentPluginChatTests(APITestCase):
    def setUp(self):
        Conversation.objects.all().delete()
        Agent.objects.all().delete()
        Plugin.objects.all().delete()
        self.plugin = Plugin.objects.create(
            name='P1', description='d', openapi_spec=VALID_SPEC,
            base_url='https://api.example.com', auth_config={}, status='enabled'
        )
        self.agent = Agent.objects.create(
            name='A1', description='d', system_prompt='You are helpful',
            model_config={'provider': 'volcano', 'model': 'demo'},
            plugin_ids=[self.plugin.id],
            knowledge_base_ids=[],
        )

    def test_chat_uses_plugin_tools(self):
        # first LLM call returns tool_call, second returns final message
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

        # plugin HTTP call returns JSON
        fake_plugin_resp = MagicMock()
        fake_plugin_resp.json.return_value = {"msg": "hi"}
        fake_plugin_resp.text = ""
        fake_plugin_resp.status_code = 200
        fake_plugin_resp.raise_for_status.return_value = None

        with patch.dict(os.environ, {"ARK_API_KEY": "test-key", "ARK_API_BASE": "http://fake"}, clear=False):
            with patch('requests.Session.post', side_effect=[first, second]) as llm_post, \
                 patch('requests.get', return_value=fake_plugin_resp) as plugin_get:
                resp = self.client.post(
                    f'/api/v1/agents/{self.agent.id}/chat/',
                    {'message': 'hi'},
                    format='json'
                )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get('data', {}).get('assistant_message') == 'final'
        assert llm_post.call_count == 2
        assert plugin_get.called
        assert Conversation.objects.count() == 1
