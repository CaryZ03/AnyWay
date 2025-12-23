from unittest.mock import MagicMock

from apps.llm.services import OpenAIService


def test_openai_embedding_client_error_returns_message(monkeypatch):
    svc = OpenAIService(api_key="k")
    fake_client = MagicMock()
    fake_client.embeddings.create.side_effect = Exception("bad")
    monkeypatch.setattr(svc, "client", fake_client, raising=False)
    result = svc.embedding("hi")
    # service falls back to default vector on error
    assert isinstance(result, list)
    assert len(result) == 1536
