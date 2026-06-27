from fastapi.testclient import TestClient

from app.main import app


def test_research_endpoint_returns_report_and_visual_graph() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/research",
        json={"query": "研究 LangGraph 企业级 Agent 落地", "use_mock_search": True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["brief"]["language"] == "zh"
    assert payload["report"]["markdown"].startswith("# Deep Research 报告")
    assert payload["visual_graph"]["nodes"]


def test_config_status_endpoint_masks_secret_values(monkeypatch) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "secret-tavily")
    monkeypatch.setenv("OPENAI_API_KEY", "secret-openai")
    client = TestClient(app)

    response = client.get("/api/config/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload == {"tavily_configured": True, "llm_configured": True}
    assert "secret" not in response.text
