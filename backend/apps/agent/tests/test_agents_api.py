from django.test import override_settings
from rest_framework.test import APITestCase
from unittest.mock import patch
from typing import Any

from apps.agent.models import Agent, Conversation


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
class AgentEndpointTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """Prepare a base agent for most tests."""
        cls.agent = Agent.objects.create(
            name='Agent A',
            description='desc',
            system_prompt='You are helpful.',
            model_config={'provider': 'volcano', 'model': 'demo-model'},
            workflow_id=None,
            knowledge_base_ids=[],
            plugin_ids=[],
        )

    def test_create_agent_success(self):
        resp = self.client.post('/api/v1/agents/', {
            'name': 'Test Agent',
            'system_prompt': 'hello',
        }, format='json')
        assert resp.status_code == 201
        body = resp.json()
        assert body.get('success') is True
        assert body.get('data', {}).get('name') == 'Test Agent'

    def test_publish_requires_system_prompt(self):
        agent = Agent.objects.create(
            name='NoPrompt',
            description='desc',
            system_prompt='',
            model_config={'provider': 'volcano'},
            knowledge_base_ids=[],
            plugin_ids=[],
        )
        resp = self.client.post(f'/api/v1/agents/{agent.id}/publish/')
        assert resp.status_code == 400
        body = resp.json()
        assert body.get('success') is False
        assert body.get('message') == '系统提示词不能为空'

    def test_publish_success(self):
        resp = self.client.post(f'/api/v1/agents/{self.agent.id}/publish/')
        assert resp.status_code == 200
        self.agent.refresh_from_db()
        assert self.agent.status == 'published'

    def test_soft_delete_excludes_from_list(self):
        agent = Agent.objects.create(
            name='ToDelete',
            description='desc',
            system_prompt='prompt',
            model_config={},
            knowledge_base_ids=[],
            plugin_ids=[],
        )
        delete_resp = self.client.delete(f'/api/v1/agents/{agent.id}/')
        assert delete_resp.status_code == 200
        list_resp = self.client.get('/api/v1/agents/')
        assert list_resp.status_code == 200
        data = list_resp.json().get('data')
        assert all(item['id'] != agent.id for item in data)
        assert Agent.objects.filter(deleted=False).count() == 1

    def test_chat_saves_conversation_and_returns_reply(self):
        class DummyLLM:
            def chat(self, messages: Any = None, model: str = '', temperature: float = 0.0, **kwargs: Any):
                return 'mock reply'

        with patch('apps.llm.services.get_llm_service', return_value=DummyLLM()):
            resp = self.client.post(
                f'/api/v1/agents/{self.agent.id}/chat/',
                {'message': 'hi'},
                format='json'
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get('success') is True
        assert body.get('data', {}).get('assistant_message') == 'mock reply'
        assert Conversation.objects.count() == 1

    def test_test_endpoint_uses_llm_and_persists_history(self):
        class DummyLLM:
            def chat(self, messages: Any = None, model: str = '', temperature: float = 0.0, **kwargs: Any):
                return 'test reply'

        with patch('apps.llm.services.get_llm_service', return_value=DummyLLM()):
            resp = self.client.post(
                f'/api/v1/agents/{self.agent.id}/test/',
                {'message': 'ping'},
                format='json'
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get('data', {}).get('assistant_message') == 'test reply'
        assert Conversation.objects.count() == 1

    def test_list_agents(self):
        resp = self.client.get('/api/v1/agents/')
        assert resp.status_code == 200
        body = resp.json()
        assert body.get('success') is True
        assert isinstance(body.get('data'), list)
