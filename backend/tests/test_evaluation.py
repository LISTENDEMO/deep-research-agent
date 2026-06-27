from app.evaluation import evaluate_research_quality
from app.graph.runner import run_research


def test_evaluate_research_quality_reports_citation_and_risk_metrics() -> None:
    result = run_research("研究 LangGraph 的优势和风险", use_mock_search=True)

    metrics = evaluate_research_quality(result.evidence, result.opposition_matrix)

    assert metrics["citation_coverage"] == 1.0
    assert metrics["source_count"] >= 2
    assert 0 <= metrics["hallucination_risk"] <= 1
