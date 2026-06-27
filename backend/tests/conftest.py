import pytest


@pytest.fixture(autouse=True)
def isolate_external_provider_env(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("MODEL_NAME", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    monkeypatch.setenv("RESEARCH_HISTORY_DB", str(tmp_path / "test-history.sqlite3"))
