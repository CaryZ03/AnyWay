from unittest.mock import MagicMock

from apps.llm.services import OpenAIService


def test_openai_embedding_client_error_returns_message(monkeypatch):
    svc = OpenAIService(api_key="k")
    fake_client = MagicMock()
    fake_client.embeddings.create.side_effect = Exception("bad")
    monkeypatch.setattr("apps.llm.services.OpenAI", MagicMock(return_value=fake_client))
    result = svc.embedding("hi")
    assert "错误" in result or "bad" in result

