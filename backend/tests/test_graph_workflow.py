from app.graph.langgraph_workflow import build_research_graph


def test_langgraph_workflow_runs_end_to_end_with_mock_search() -> None:
    graph = build_research_graph(use_mock_search=True)

    result = graph.invoke(
        {
            "user_query": "研究中文 Deep Research Agent 的架构亮点",
            "use_mock_search": True,
        }
    )

    assert result["brief"].language == "zh"
    assert result["plan"]
    assert result["evidence"]
    assert result["report"].markdown.startswith("# Deep Research 报告")
    assert result["visual_graph"]["nodes"]
    assert result["opposition_matrix"]
    assert result["timeline"]
