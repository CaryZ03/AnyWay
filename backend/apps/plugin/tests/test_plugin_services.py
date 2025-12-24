from unittest.mock import MagicMock, patch

from requests.exceptions import RequestException

from apps.plugin.models import Plugin
from apps.plugin.services import PluginService, build_api_map


def make_plugin(status='enabled', spec=None):
    return Plugin(id=1, name='P1', description='d', openapi_spec=spec or {}, base_url='https://api.example.com', auth_config={}, status=status)


def test_parse_openapi_to_functions_filters_disabled():
    # 过滤禁用插件
    disabled = make_plugin(status='disabled', spec={'paths': {}, 'servers': []})
    funcs = PluginService.parse_openapi_to_functions([disabled])
    assert funcs == []


def test_parse_openapi_to_functions_basic():
    # 基本 openapi 解析为工具函数
    spec = {
        'paths': {
            '/weather': {
                'get': {
                    'operationId': 'getWeather',
                    'summary': 'Get weather',
                    'parameters': [
                        {'in': 'query', 'name': 'city', 'schema': {'type': 'string'}, 'required': True}
                    ]
                }
            }
        },
        'servers': [{'url': 'https://api.example.com'}]
    }
    plugin = make_plugin(spec=spec)
    funcs = PluginService.parse_openapi_to_functions([plugin])
    assert len(funcs) == 1
    fn = funcs[0]
    assert fn['name'] == 'getWeather'
    assert fn['parameters']['required'] == ['city']
    assert fn['metadata']['path'] == '/weather'


def test_build_api_map():
    # 构建 operationId -> url/method 映射
    spec = {
        'servers': [{'url': 'https://api.example.com'}],
        'paths': {
            '/hello': {
                'get': {'operationId': 'helloOp'}
            }
        }
    }
    api_map = build_api_map(spec)
    assert api_map['helloOp']['url'] == 'https://api.example.com/hello'
    assert api_map['helloOp']['method'] == 'GET'


def test_call_function_success_json():
    # call_function 成功返回 JSON
    spec = {
        'paths': {
            '/hello': {
                'get': {
                    'operationId': 'helloOp',
                    'parameters': []
                }
            }
        },
        'servers': [{'url': 'https://api.example.com'}]
    }
    plugin = make_plugin(spec=spec)
    funcs = PluginService.parse_openapi_to_functions([plugin])

    fake_resp = MagicMock()
    fake_resp.json.return_value = {'msg': 'ok'}
    fake_resp.text = ''
    fake_resp.status_code = 200
    fake_resp.raise_for_status.return_value = None

    with patch('requests.get', return_value=fake_resp):
        result = PluginService.call_function('helloOp', {}, funcs)
    assert result['success'] is True
    assert result['data'] == {'msg': 'ok'}


def test_call_function_not_found():
    # 未找到 operationId 的兜底
    result = PluginService.call_function('missing', {}, [])
    assert '不存在' in result['error']


def test_format_function_result_handles_error_and_dict():
    # 格式化错误/成功返回
    assert PluginService.format_function_result({'success': False, 'error': 'boom'}) == '调用失败: boom'
    text = PluginService.format_function_result({'success': True, 'data': {'a': 1}})
    assert '"a": 1' in text


def test_call_plugin_operation_success():
    # 通过 plugin 实例执行 operationId 成功
    spec = {
        'servers': [{'url': 'https://api.example.com'}],
        'paths': {
            '/hello/{name}': {
                'get': {
                    'operationId': 'helloOp'
                }
            }
        }
    }
    plugin = make_plugin(spec=spec)
    fake_resp = MagicMock()
    fake_resp.json.return_value = {'hi': 'bob'}
    fake_resp.text = ''
    fake_resp.status_code = 200
    fake_resp.raise_for_status.return_value = None

    with patch('requests.get', return_value=fake_resp):
        result = PluginService.call_plugin_operation(plugin, 'helloOp', {'name': 'bob', 'q': 1})
    assert result['success'] is True
    assert result['data'] == {'hi': 'bob'}
    assert 'helloOp' in result['operation_id']


def test_call_plugin_operation_missing():
    # operationId 不存在的兜底
    plugin = make_plugin(spec={'paths': {}, 'servers': []})
    result = PluginService.call_plugin_operation(plugin, 'missing', {})
    assert '不存在' in result['error']


def test_call_function_http_error():
    # HTTP 调用异常兜底
    spec = {
        'paths': {'/hello': {'get': {'operationId': 'helloOp'}}},
        'servers': [{'url': 'https://api.example.com'}]
    }
    plugin = make_plugin(spec=spec)
    funcs = PluginService.parse_openapi_to_functions([plugin])

    with patch('requests.get', side_effect=RequestException('boom')):
        result = PluginService.call_function('helloOp', {}, funcs)
    assert result['success'] is False
    assert 'boom' in result['error']


def test_call_plugin_operation_propagates_http_error():
    # call_plugin_operation 返回 HTTP 异常应带 error 消息
    plugin = make_plugin(spec={
        'servers': [{'url': 'https://api.example.com'}],
        'paths': {
            '/hello': {
                'get': {'operationId': 'helloOp'}
            }
        }
    })
    with patch('requests.get', side_effect=RequestException('bad http')):
        result = PluginService.call_plugin_operation(plugin, 'helloOp', {'name': 'bob'})
    assert result['success'] is False
    assert 'bad http' in result.get('error', '')
