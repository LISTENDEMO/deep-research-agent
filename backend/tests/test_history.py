from dataclasses import asdict

from fastapi.testclient import TestClient

from app.history_store import HistoryStore
from app.main import app
from app.models import ResearchResult


def test_history_store_saves_lists_loads_and_deletes_research_result(tmp_path) -> None:
    result = _sample_result()
    store = HistoryStore(tmp_path / "history.sqlite3")

    report_id = store.save_result(result)

    reports = store.list_reports()
    assert reports[0]["id"] == report_id
    assert reports[0]["query"] == "研究 Agent 历史功能"
    assert reports[0]["source_count"] == 1

    loaded = store.get_report(report_id)
    assert loaded is not None
    assert loaded["payload"]["report"]["markdown"].startswith("# Deep Research 报告")
    assert loaded["payload"]["evidence"][0]["source_url"] == "https://example.com/history"

    assert store.delete_report(report_id) is True
    assert store.get_report(report_id) is None


def test_research_api_persists_history_and_exposes_detail_endpoints(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("RESEARCH_HISTORY_DB", str(tmp_path / "api-history.sqlite3"))
    client = TestClient(app)

    response = client.post(
        "/api/research",
        json={"query": "研究 LangGraph 历史功能", "use_mock_search": True},
    )

    assert response.status_code == 200
    payload = response.json()
    report_id = payload["report_id"]

    list_response = client.get("/api/reports")
    assert list_response.status_code == 200
    reports = list_response.json()["reports"]
    assert reports[0]["id"] == report_id
    assert reports[0]["query"] == "研究 LangGraph 历史功能"

    detail_response = client.get(f"/api/reports/{report_id}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["id"] == report_id
    assert detail["payload"]["report"]["markdown"].startswith("# Deep Research 报告")
    assert detail["payload"]["evidence"]

    delete_response = client.delete(f"/api/reports/{report_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"deleted": True}
    assert client.get(f"/api/reports/{report_id}").status_code == 404


def _sample_result() -> ResearchResult:
    return ResearchResult(
        brief={
            "original_query": "研究 Agent 历史功能",
            "objective": "验证历史保存。",
            "language": "zh",
            "scope": [],
            "deliverables": [],
            "success_criteria": [],
        },
        plan=[
            {
                "id": "task-1",
                "title": "历史保存",
                "query": "history",
                "rationale": "验证保存。",
            }
        ],
        evidence=[
            {
                "id": "e1",
                "task_id": "task-1",
                "claim": "历史需要保存证据。",
                "source_title": "History source",
                "source_url": "https://example.com/history",
                "quote": "history stores evidence",
                "stance": "support",
                "confidence": 0.8,
                "topic": "历史保存",
            }
        ],
        report={
            "title": "# Deep Research 报告：研究 Agent 历史功能",
            "markdown": "# Deep Research 报告：研究 Agent 历史功能\n\n## 引用来源\n- [S1] source",
        },
        visual_graph={"nodes": [], "links": []},
        opposition_matrix=[],
        timeline=[],
        exports={"markdown": "# Deep Research 报告：研究 Agent 历史功能"},
        quality_metrics={
            "citation_coverage": 1,
            "source_count": 1,
            "opposition_balance": 0,
            "hallucination_risk": 0.1,
        },
    )
