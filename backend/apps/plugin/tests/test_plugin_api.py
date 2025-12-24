import tempfile
import shutil
from django.test import override_settings
from rest_framework.test import APITestCase

from apps.plugin.models import Plugin


VALID_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "Weather API", "description": "desc"},
    "servers": [{"url": "https://api.example.com"}],
    "paths": {},
}

TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'], MEDIA_ROOT=TEST_MEDIA_ROOT)
class PluginApiTests(APITestCase):
    @classmethod
    def tearDownClass(cls):
        try:
            shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)
        finally:
            super().tearDownClass()

    def test_register_plugin_success(self):
        # 注册插件成功路径
        resp = self.client.post('/api/v1/plugins/', {"openapi_spec": VALID_SPEC}, format='json')
        assert resp.status_code == 201
        body = resp.json()
        assert body.get('success') is True
        assert Plugin.objects.filter(name='Weather API', base_url='https://api.example.com', deleted=False).exists()

    def test_register_plugin_missing_required_field(self):
        # 缺少 openapi/paths 等字段的校验
        bad_spec = {
            "info": {"title": "Bad"},
            "servers": [{"url": "https://api.example.com"}],
            # missing openapi and paths
        }
        resp = self.client.post('/api/v1/plugins/', {"openapi_spec": bad_spec}, format='json')
        assert resp.status_code == 400
        body = resp.json()
        assert body.get('success') is False
        assert 'openapi' in body.get('message', '') or 'paths' in body.get('message', '')

    def test_register_plugin_rejects_missing_paths(self):
        # paths 缺失应 400
        bad_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Bad", "description": "d"},
            "servers": [{"url": "https://api.example.com"}],
            # 缺少 paths
        }
        resp = self.client.post('/api/v1/plugins/', {"openapi_spec": bad_spec}, format='json')
        assert resp.status_code == 400
        body = resp.json()
        assert body.get('success') is False
        assert 'paths' in body.get('message', '')

    def test_register_plugin_rejects_missing_server_url(self):
        # servers[0].url 缺失应 400
        bad_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Bad", "description": "d"},
            "servers": [{}],
            "paths": {},
        }
        resp = self.client.post('/api/v1/plugins/', {"openapi_spec": bad_spec}, format='json')
        assert resp.status_code == 400
        body = resp.json()
        assert body.get('success') is False
        assert 'servers' in body.get('message', '')

    def test_list_plugins_and_retrieve(self):
        # 列表与详情
        plugin = Plugin.objects.create(
            name='Demo',
            description='d',
            openapi_spec=VALID_SPEC,
            base_url='https://api.example.com',
            auth_config={},
            status='enabled'
        )
        list_resp = self.client.get('/api/v1/plugins/')
        assert list_resp.status_code == 200
        data = list_resp.json().get('data')
        assert any(item['id'] == plugin.id for item in data)

        retrieve_resp = self.client.get(f'/api/v1/plugins/{plugin.id}/')
        assert retrieve_resp.status_code == 200
        assert retrieve_resp.json().get('data', {}).get('id') == plugin.id

    def test_update_plugin(self):
        # 更新 openapi spec 并同步 name
        plugin = Plugin.objects.create(
            name='Demo',
            description='d',
            openapi_spec=VALID_SPEC,
            base_url='https://api.example.com',
            auth_config={},
            status='enabled'
        )
        new_spec = {**VALID_SPEC, "info": {"title": "NewTitle"}}
        resp = self.client.put(f'/api/v1/plugins/{plugin.id}/', {"openapi_spec": new_spec}, format='json')
        assert resp.status_code == 200
        plugin.refresh_from_db()
        assert plugin.name == 'NewTitle'

    def test_enable_disable(self):
        # 启用/停用切换
        plugin = Plugin.objects.create(
            name='Demo',
            description='d',
            openapi_spec=VALID_SPEC,
            base_url='https://api.example.com',
            auth_config={},
            status='disabled'
        )
        enable_resp = self.client.post(f'/api/v1/plugins/{plugin.id}/enable/')
        assert enable_resp.status_code == 200
        plugin.refresh_from_db()
        assert plugin.status == 'enabled'

        disable_resp = self.client.post(f'/api/v1/plugins/{plugin.id}/disable/')
        assert disable_resp.status_code == 200
        plugin.refresh_from_db()
        assert plugin.status == 'disabled'

    def test_soft_delete(self):
        # 逻辑删除后列表不再包含
        plugin = Plugin.objects.create(
            name='Demo',
            description='d',
            openapi_spec=VALID_SPEC,
            base_url='https://api.example.com',
            auth_config={},
            status='enabled'
        )
        del_resp = self.client.delete(f'/api/v1/plugins/{plugin.id}/')
        assert del_resp.status_code == 200
        plugin.refresh_from_db()
        assert plugin.deleted is True
        list_resp = self.client.get('/api/v1/plugins/')
        data = list_resp.json().get('data')
        assert all(item['id'] != plugin.id for item in data)
