from app.graph.runner import run_research
from app.models import SearchResult


class FakeSearchTool:
    def search(self, query: str, max_results: int = 3) -> list[SearchResult]:
        return [
            SearchResult(
                title="Agent observability source",
                url="https://example.com/agent-observability",
                content="Agent observability should capture tool calls, latency, errors and evaluation traces.",
            )
        ]


class FakePipelineLLM:
    def __init__(self) -> None:
        self.calls = 0

    def generate(self, prompt: str) -> str:
        self.calls += 1
        return (
            "# Deep Research 报告：研究 Agent 可观测性\n\n"
            "## 执行摘要\nLLM Pipeline Writer 已接入，结论基于证据[S1]。\n\n"
            "## 直接答案\n应记录工具调用、延迟、错误和评估轨迹[S1]。\n\n"
            "## 关键判断\n- 可观测性需要覆盖运行日志和评估链路[S1]。\n\n"
            "## 风险与反方观点\n- 数据采集需要注意脱敏和权限控制[S1]。\n\n"
            "## 落地路线\n1. 先记录 run log。\n2. 再接评估看板。\n\n"
            "## 引用来源\n- [S1] [Agent observability source](https://example.com/agent-observability)：tool calls, latency, errors"
        )


def test_run_research_generates_chinese_brief_tasks_evidence_and_report() -> None:
    result = run_research(
        "研究 LangGraph、AutoGen、CrewAI 哪个更适合企业级多 Agent 系统",
        use_mock_search=True,
    )

    assert result.brief.language == "zh"
    assert "企业级多 Agent 系统" in result.brief.objective
    assert len(result.plan) >= 3
    assert len(result.evidence) >= len(result.plan)
    assert result.report.title.startswith("#")
    assert "引用" in result.report.markdown
    assert result.visual_graph["nodes"]
    assert result.visual_graph["links"]


def test_run_research_marks_opposing_evidence_when_mock_results_include_risk() -> None:
    result = run_research("分析 LangGraph 的优势和风险", use_mock_search=True)

    stances = {item.stance for item in result.evidence}

    assert "support" in stances
    assert "oppose" in stances


def test_run_research_uses_llm_writer_in_live_mode_with_injected_tools() -> None:
    llm = FakePipelineLLM()

    result = run_research(
        "研究 Agent 可观测性",
        use_mock_search=False,
        search_tool=FakeSearchTool(),
        llm=llm,
    )

    assert llm.calls == 1
    assert "LLM Pipeline Writer 已接入" in result.report.markdown
    assert "[S1]" in result.report.markdown
