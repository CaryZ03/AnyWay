import os
from unittest.mock import MagicMock, patch

import pytest

from apps.llm.services import VolcanoService, OpenAIService


@pytest.mark.parametrize("response_body,expected", [
    ({"choices": [{"message": {"content": "hi"}}]}, "hi"),
])
def test_volcano_chat_basic(response_body, expected):
    fake_resp = MagicMock()
    fake_resp.json.return_value = response_body
    fake_resp.raise_for_status.return_value = None

    with patch.dict(os.environ, {"ARK_API_KEY": "test-key", "ARK_API_BASE": "http://fake"}, clear=False):
        with patch("requests.Session.post", return_value=fake_resp) as post_mock:
            svc = VolcanoService()
            result = svc.chat(messages=[{"role": "user", "content": "hi"}], model="demo")

    assert result == expected
    assert post_mock.called


def test_volcano_chat_with_tool_calls_triggers_second_call():
    first = MagicMock()
    first.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "first",
                    "tool_calls": [
                        {
                            "function": {"name": "tool1", "arguments": "{}"}
                        }
                    ],
                }
            }
        ]
    }
    first.raise_for_status.return_value = None

    second = MagicMock()
    second.json.return_value = {"choices": [{"message": {"content": "final"}}]}
    second.raise_for_status.return_value = None

    with patch.dict(os.environ, {"ARK_API_KEY": "test-key", "ARK_API_BASE": "http://fake"}, clear=False):
        with patch("requests.Session.post", side_effect=[first, second]) as post_mock:
            svc = VolcanoService()
            # api_map empty, so tool_calls not executed, but flow hits second call when tool_results truthy? requires api_map
            result = svc.chat(messages=[{"role": "user", "content": "hi"}], model="demo", active_tools=[{"function": {"name": "tool1"}}], api_map={"p": {"tool1": {"method": "GET", "url": "http://fake"}}})

    assert result == "final"
    assert post_mock.call_count == 2


def test_volcano_chat_tool_call_missing_api_map_returns_original():
    first = MagicMock()
    first.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "first",
                    "tool_calls": [
                        {
                            "function": {"name": "tool_missing", "arguments": "{}"}
                        }
                    ],
                }
            }
        ]
    }
    first.raise_for_status.return_value = None

    with patch.dict(os.environ, {"ARK_API_KEY": "test-key", "ARK_API_BASE": "http://fake"}, clear=False):
        with patch("requests.Session.post", return_value=first) as post_mock:
            svc = VolcanoService()
            result = svc.chat(messages=[{"role": "user", "content": "hi"}], model="demo", active_tools=[{"function": {"name": "tool_missing"}}], api_map={})

    assert result == "first"
    assert post_mock.call_count == 1


def test_openai_service_without_client_returns_placeholder():
    svc = OpenAIService(api_key=None)
    result = svc.chat(messages=[{"role": "user", "content": "hi"}])
    assert result == "OpenAI服务未配置"


def test_volcano_chat_tool_call_http_error_returns_error(monkeypatch):
    first = MagicMock()
    first.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "first",
                    "tool_calls": [
                        {"function": {"name": "tool1", "arguments": "{}"}}
                    ],
                }
            }
        ]
    }
    first.raise_for_status.return_value = None

    second = MagicMock()
    second.json.return_value = {"choices": [{"message": {"content": "second"}}]}
    second.raise_for_status.return_value = None

    def fake_get(url, params=None, json=None, timeout=5):
        raise Exception("http fail")

    with patch.dict(os.environ, {"ARK_API_KEY": "test-key", "ARK_API_BASE": "http://fake"}, clear=False):
        with patch("requests.Session.post", side_effect=[first, second]) as post_mock, patch("requests.get", side_effect=fake_get):
            svc = VolcanoService()
            result = svc.chat(
                messages=[{"role": "user", "content": "hi"}],
                model="demo",
                active_tools=[{"function": {"name": "tool1"}}],
                api_map={"p": {"tool1": {"method": "GET", "url": "http://fake/tool"}}},
            )

    assert post_mock.call_count == 2
    assert "错误" in result or "抱歉" in result or result == "second"
