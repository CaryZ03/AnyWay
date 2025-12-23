import json
from unittest.mock import MagicMock, patch

import pytest

from apps.workflow.services import WorkflowEngine, WorkflowExecutionError

pytestmark = pytest.mark.django_db


def test_execute_llm_node_success(monkeypatch):
    engine = WorkflowEngine()
    engine.context = {"user_input": "hello"}
    cfg = {"prompt": "Answer", "systemPrompt": "sys", "model": "demo"}

    class DummyLLM:
        def chat(self, *args, **kwargs):
            return json.dumps({"answer": "ok", "thoughts": "t"})

    monkeypatch.setattr("apps.workflow.services.get_llm_service", lambda provider: DummyLLM())
    result = engine._execute_llm_node(cfg)
    assert result["answer"] == "ok"


def test_execute_llm_node_non_json_raises(monkeypatch):
    engine = WorkflowEngine()
    engine.context = {"user_input": "hello"}
    cfg = {"prompt": "Answer"}

    class DummyLLM:
        def chat(self, *args, **kwargs):
            return "not-json"

    monkeypatch.setattr("apps.workflow.services.get_llm_service", lambda provider: DummyLLM())
    with pytest.raises(WorkflowExecutionError):
        engine._execute_llm_node(cfg)


def test_execute_http_node_replaces_and_returns(monkeypatch):
    engine = WorkflowEngine()
    engine.context = {"input": {"id": 123}}
    cfg = {
        "url": "https://api.example.com/items/{input.id}",
        "method": "GET",
        "headers": {"X-Test": "{input.id}"},
    }

    fake_resp = MagicMock()
    fake_resp.json.return_value = {"ok": True}
    fake_resp.text = ""
    fake_resp.status_code = 200
    fake_resp.headers = {"h": "v"}

    monkeypatch.setattr("apps.workflow.services.requests.request", lambda **kwargs: fake_resp)
    result = engine._execute_http_node(cfg)
    assert result["success"] is True
    assert result["body"] == {"ok": True}
    assert "items/123" in result["url"]


def test_execute_http_node_missing_url_raises():
    engine = WorkflowEngine()
    with pytest.raises(WorkflowExecutionError):
        engine._execute_http_node({"method": "GET"})


def test_execute_http_node_retries_on_timeout(monkeypatch):
    engine = WorkflowEngine()
    engine.context = {}
    cfg = {
        "url": "https://api.example.com/r",
        "method": "GET",
        "retryCount": 1,
        "timeout": 1,
    }

    fake_resp = MagicMock()
    fake_resp.json.return_value = {"ok": True}
    fake_resp.text = ""
    fake_resp.status_code = 200
    fake_resp.headers = {}

    def side_effect(**kwargs):
        if side_effect.calls == 0:
            side_effect.calls += 1
            raise Exception("timeout")
        return fake_resp

    side_effect.calls = 0
    monkeypatch.setattr("apps.workflow.services.requests.request", side_effect)

    result = engine._execute_http_node(cfg)
    assert result["success"] is True
    assert side_effect.calls == 1


def test_execute_knowledge_node_success(monkeypatch):
    engine = WorkflowEngine()
    engine.context = {"input": {"q": "hello"}}
    cfg = {"knowledge_base_id": 1, "query": "{input.q}", "top_k": 2}

    fake_resp = MagicMock()
    fake_resp.json.return_value = {"documents": ["d1"], "metadatas": [{"doc_id": 1}], "scores": [0.9]}
    fake_resp.raise_for_status.return_value = None

    monkeypatch.setattr("apps.workflow.services.requests.post", lambda *args, **kwargs: fake_resp)
    result = engine._execute_knowledge_node(cfg)
    assert result["results"][0]["content"] == "d1"


def test_execute_knowledge_node_missing_id_raises():
    engine = WorkflowEngine()
    with pytest.raises(WorkflowExecutionError):
        engine._execute_knowledge_node({"query": "hi"})


def test_execute_start_node_populates_user_input():
    engine = WorkflowEngine()
    engine.context = {"message": "hello"}
    result = engine._execute_start_node({})
    assert result["user_input"] == "hello"
    assert engine.context["user_input"] == "hello"


def test_execute_intent_node_success(monkeypatch):
    engine = WorkflowEngine()
    engine.context = {"user_input": "book a flight"}
    cfg = {
        "intents": [
            {"id": "book", "name": "Book", "description": ""},
            {"id": "other", "name": "Other", "description": ""},
        ]
    }

    class DummyLLM:
        def chat(self, *args, **kwargs):
            return json.dumps({"intent_id": "book", "intent_name": "Book", "reason": "match"})

    monkeypatch.setattr("apps.workflow.services.get_llm_service", lambda provider: DummyLLM())
    result = engine._execute_intent_node(cfg)
    assert result["intent_id"] == "book"
    assert engine.context["intent"] == "Book"


def test_execute_intent_node_missing_intents_raises():
    engine = WorkflowEngine()
    engine.context = {"user_input": "hi"}
    with pytest.raises(WorkflowExecutionError):
        engine._execute_intent_node({"intents": []})


def test_execute_intent_node_no_user_input_raises():
    engine = WorkflowEngine()
    with pytest.raises(WorkflowExecutionError):
        engine._execute_intent_node({"intents": [{"id": "a", "name": "A"}]})
