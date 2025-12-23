from apps.llm.services import OpenAIService


def test_openai_embedding_returns_default_when_unconfigured():
    svc = OpenAIService(api_key=None)
    emb = svc.embedding("hello")
    # fallback returns list of 1536 values 0.1 per implementation
    assert isinstance(emb, list)
    assert len(emb) == 1536
    assert all(abs(x - 0.1) < 1e-6 for x in emb)

