import os

from app.tools.search import TavilySearchTool


def test_tavily_tool_requires_api_key_for_live_search(monkeypatch) -> None:
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    tool = TavilySearchTool()

    assert tool.is_configured is False


def test_tavily_tool_uses_environment_api_key(monkeypatch) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    tool = TavilySearchTool()

    assert tool.is_configured is True
    assert os.environ["TAVILY_API_KEY"] == "test-key"
