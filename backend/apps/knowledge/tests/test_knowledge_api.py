import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase

from apps.knowledge.models import KnowledgeBase, Document

TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'], MEDIA_ROOT=TEST_MEDIA_ROOT)
class KnowledgeApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.kb = KnowledgeBase.objects.create(name='KB1', description='desc')

    @classmethod
    def tearDownClass(cls):
        try:
            shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)
        finally:
            super().tearDownClass()

    def test_list_knowledge_bases_empty_or_existing(self):
        resp = self.client.get('/api/v1/knowledge/')
        assert resp.status_code == 200
        data = resp.json().get('data')
        assert isinstance(data, list)
        assert any(item['id'] == self.kb.id for item in data)

    def test_create_knowledge_base(self):
        resp = self.client.post('/api/v1/knowledge/', {'name': 'KB2', 'description': 'd'}, format='json')
        assert resp.status_code == 201
        body = resp.json()
        assert body.get('success') is True
        assert KnowledgeBase.objects.filter(name='KB2', deleted=False).exists()

    def test_retrieve_and_delete(self):
        resp = self.client.get(f'/api/v1/knowledge/{self.kb.id}/')
        assert resp.status_code == 200
        assert resp.json().get('data', {}).get('id') == self.kb.id

        del_resp = self.client.delete(f'/api/v1/knowledge/{self.kb.id}/')
        assert del_resp.status_code == 200
        self.kb.refresh_from_db()
        assert self.kb.deleted is True

    def test_upload_document_and_list(self):
        content = b'hello world'
        upload = SimpleUploadedFile('note.txt', content, content_type='text/plain')
        resp = self.client.post(
            f'/api/v1/knowledge/{self.kb.id}/upload/',
            {'file': upload},
            format='multipart'
        )
        assert resp.status_code == 201
        body = resp.json()
        doc_id = body.get('data', {}).get('id')
        assert Document.objects.filter(id=doc_id, knowledge_base=self.kb).exists()

        list_resp = self.client.get(f'/api/v1/knowledge/{self.kb.id}/documents/')
        assert list_resp.status_code == 200
        docs = list_resp.json().get('data')
        assert any(d['id'] == doc_id for d in docs)

    def test_search_returns_empty_list(self):
        resp = self.client.post(
            f'/api/v1/knowledge/{self.kb.id}/search/',
            {'query': 'test', 'top_k': 3},
            format='json'
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get('success') is True
        assert body.get('data') == []
