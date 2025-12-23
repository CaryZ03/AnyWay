from django.test import override_settings
from rest_framework.test import APITestCase


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
class HealthAndSwaggerTests(APITestCase):
    def test_health_endpoint(self):
        """Health check should return 200 and status ok."""
        resp = self.client.get('/health/')
        assert resp.status_code == 200
        assert resp.json().get('status') == 'ok'

    def test_swagger_ui_accessible(self):
        """Swagger UI returns HTML; just ensure 200 OK."""
        resp = self.client.get('/swagger/')
        assert resp.status_code == 200
