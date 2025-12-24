from django.test import TestCase, override_settings
import yaml


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
class HealthSwaggerTests(TestCase):
    # 健康检查应 200 且返回状态 ok
    def test_health_endpoint(self):
        resp = self.client.get('/health/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('status'), 'ok')

    # swagger UI 可访问，包含 swagger-ui 容器
    def test_swagger_endpoint(self):
        resp = self.client.get('/swagger/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'id="swagger-ui"', resp.content)

    # redoc UI 可访问，包含 redoc 占位
    def test_redoc_endpoint(self):
        resp = self.client.get('/redoc/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'redoc-placeholder', resp.content)

    # swagger.json/schema 可返回 200，支持 json 或 yaml
    def test_swagger_json_endpoint(self):
        resp = self.client.get('/swagger.json')
        self.assertEqual(resp.status_code, 200)
        ctype = resp.get('Content-Type', '')
        if 'json' in ctype:
            data = resp.json()
        else:
            data = yaml.safe_load(resp.content.decode())
        self.assertEqual(data.get('info', {}).get('title'), 'AI Agent Platform API')
        # openapi 或 swagger 版本字段存在即可
        self.assertTrue(data.get('swagger') or data.get('openapi'))


@override_settings(ALLOWED_HOSTS=['badhost'])
class HealthSwaggerDisallowedHostTests(TestCase):
    # 在不允许的 Host 下应返回 400/DisallowedHost
    def test_health_disallowed_host(self):
        resp = self.client.get('/health/', HTTP_HOST='evil.com')
        self.assertIn(resp.status_code, (400, 403, 500))

    def test_swagger_disallowed_host(self):
        resp = self.client.get('/swagger/', HTTP_HOST='evil.com')
        self.assertIn(resp.status_code, (400, 403, 500))
