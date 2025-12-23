from unittest.mock import patch
from django.test import override_settings
from rest_framework.test import APITestCase

from apps.workflow.models import Workflow, WorkflowExecution
from apps.workflow.services import WorkflowExecutionError

VALID_DEFINITION = {
    "nodes": [
        {"id": "start", "type": "start"},
        {"id": "end", "type": "end"},
    ],
    "edges": [
        {"id": "e1", "source": "start", "target": "end"},
    ],
}


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
class WorkflowApiTests(APITestCase):
    def setUp(self):
        self.workflow = Workflow.objects.create(
            name='Flow1',
            description='desc',
            definition=VALID_DEFINITION,
            status='draft'
        )

    def test_create_workflow(self):
        resp = self.client.post('/api/v1/workflows/', {
            'name': 'Flow2',
            'description': 'd',
            'definition': VALID_DEFINITION,
            'status': 'active'
        }, format='json')
        assert resp.status_code == 201
        body = resp.json()
        assert body.get('success') is True
        assert Workflow.objects.filter(name='Flow2', deleted=False).exists()

    def test_list_and_retrieve(self):
        list_resp = self.client.get('/api/v1/workflows/')
        assert list_resp.status_code == 200
        data = list_resp.json().get('data')
        assert any(item['id'] == self.workflow.id for item in data)

        get_resp = self.client.get(f'/api/v1/workflows/{self.workflow.id}/')
        assert get_resp.status_code == 200
        assert get_resp.json().get('data', {}).get('id') == self.workflow.id

    def test_update_and_delete(self):
        update_resp = self.client.put(f'/api/v1/workflows/{self.workflow.id}/', {
            'name': 'Flow1-upd',
            'definition': VALID_DEFINITION,
            'status': 'active'
        }, format='json')
        assert update_resp.status_code == 200
        self.workflow.refresh_from_db()
        assert self.workflow.name == 'Flow1-upd'
        assert self.workflow.status == 'active'

        del_resp = self.client.delete(f'/api/v1/workflows/{self.workflow.id}/')
        assert del_resp.status_code == 200
        self.workflow.refresh_from_db()
        assert self.workflow.deleted is True
        list_resp = self.client.get('/api/v1/workflows/')
        assert all(item['id'] != self.workflow.id for item in list_resp.json().get('data'))

    def test_execute_success(self):
        def fake_execute(workflow, input_data, execution):
            execution.status = 'completed'
            execution.output_data = {'answer': 'ok'}
            execution.save(update_fields=['status', 'output_data'])
            return execution.output_data

        with patch('apps.workflow.views.WorkflowEngine.execute', side_effect=fake_execute):
            resp = self.client.post(
                f'/api/v1/workflows/{self.workflow.id}/execute/',
                {'input_data': {'user_input': 'hi'}},
                format='json'
            )
        assert resp.status_code == 200
        body = resp.json()
        exec_data = body.get('data', {})
        assert exec_data.get('status') == 'completed'
        assert WorkflowExecution.objects.filter(workflow=self.workflow).count() == 1

    def test_execute_failure(self):
        with patch('apps.workflow.views.WorkflowEngine.execute', side_effect=WorkflowExecutionError('boom')):
            resp = self.client.post(
                f'/api/v1/workflows/{self.workflow.id}/execute/',
                {'input_data': {'user_input': 'hi'}},
                format='json'
            )
        assert resp.status_code == 500
        body = resp.json()
        assert body.get('success') is False
        assert '失败' in body.get('message', '')
