from fastapi.testclient import TestClient

from app.main import app


def test_research_endpoint_includes_matrix_timeline_and_export_markdown() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/research",
        json={"query": "研究 LangGraph 的优势和风险", "use_mock_search": True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["opposition_matrix"]
    assert payload["timeline"]
    assert payload["exports"]["markdown"].startswith("# Deep Research 报告")


def test_export_markdown_endpoint_returns_markdown_text() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/export/markdown",
        json={"query": "研究 LangGraph 的优势和风险", "use_mock_search": True},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/markdown")
    assert "# Deep Research 报告" in response.text


def test_research_events_endpoint_streams_steps_and_final_payload() -> None:
    client = TestClient(app)

    with client.stream(
        "POST",
        "/api/research/events",
        json={"query": "研究 LangGraph 的优势和风险", "use_mock_search": True},
    ) as response:
        lines = [line for line in response.iter_lines() if line]

    assert response.status_code == 200
    assert any('"event": "step"' in line for line in lines)
    assert any('"event": "final"' in line for line in lines)


def test_research_events_endpoint_streams_error_when_live_search_is_not_configured(monkeypatch) -> None:
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    client = TestClient(app)

    with client.stream(
        "POST",
        "/api/research/events",
        json={"query": "研究 LangGraph 的优势和风险", "use_mock_search": False},
    ) as response:
        lines = [line for line in response.iter_lines() if line]

    assert response.status_code == 200
    assert any('"event": "error"' in line for line in lines)
    assert any("TAVILY_API_KEY" in line for line in lines)
