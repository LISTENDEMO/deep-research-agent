from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.researcher import extract_evidence
from app.agents.scope import generate_brief
from app.agents.supervisor import plan_research
from app.agents.writer import write_report
from app.analysis import build_opposition_matrix, build_timeline
from app.evaluation import evaluate_research_quality
from app.graph.visualization import build_visual_graph
from app.llm import ChineseLLM, build_llm
from app.models import Evidence, ResearchBrief, ResearchReport, ResearchTask
from app.tools.search import MockSearchTool, SearchTool, TavilySearchTool


class ResearchGraphState(TypedDict, total=False):
    user_query: str
    use_mock_search: bool
    brief: ResearchBrief
    plan: list[ResearchTask]
    evidence: list[Evidence]
    report: ResearchReport
    visual_graph: dict[str, Any]
    opposition_matrix: list[Any]
    timeline: list[Any]
    exports: dict[str, str]
    quality_metrics: dict[str, float | int]


def build_research_graph(
    *,
    use_mock_search: bool = False,
    search_tool: SearchTool | None = None,
    llm: ChineseLLM | None = None,
):
    resolved_llm = llm or build_llm()

    def scope_node(state: ResearchGraphState) -> ResearchGraphState:
        return {"brief": generate_brief(state["user_query"])}

    def plan_node(state: ResearchGraphState) -> ResearchGraphState:
        return {"plan": plan_research(state["brief"])}

    def research_node(state: ResearchGraphState) -> ResearchGraphState:
        should_mock = state.get("use_mock_search", use_mock_search)
        tool = search_tool or (MockSearchTool() if should_mock else TavilySearchTool())
        evidence: list[Evidence] = []
        for task in state["plan"]:
            results = tool.search(task.query, max_results=3)
            evidence.extend(extract_evidence(task, results))
        return {"evidence": evidence}

    def verify_node(state: ResearchGraphState) -> ResearchGraphState:
        matrix = build_opposition_matrix(state["evidence"])
        return {
            "opposition_matrix": matrix,
            "timeline": build_timeline(state["brief"], state["plan"], state["evidence"]),
            "quality_metrics": evaluate_research_quality(state["evidence"], matrix),
        }

    def write_node(state: ResearchGraphState) -> ResearchGraphState:
        should_mock = state.get("use_mock_search", use_mock_search)
        report = write_report(
            state["brief"],
            state["plan"],
            state["evidence"],
            llm=None if should_mock else resolved_llm,
        )
        return {"report": report, "exports": {"markdown": report.markdown}}

    def visualize_node(state: ResearchGraphState) -> ResearchGraphState:
        return {
            "visual_graph": build_visual_graph(
                state["brief"],
                state["plan"],
                state["evidence"],
            )
        }

    builder = StateGraph(ResearchGraphState)
    builder.add_node("scope", scope_node)
    builder.add_node("plan", plan_node)
    builder.add_node("research", research_node)
    builder.add_node("verify", verify_node)
    builder.add_node("write", write_node)
    builder.add_node("visualize", visualize_node)
    builder.add_edge(START, "scope")
    builder.add_edge("scope", "plan")
    builder.add_edge("plan", "research")
    builder.add_edge("research", "verify")
    builder.add_edge("verify", "write")
    builder.add_edge("write", "visualize")
    builder.add_edge("visualize", END)
    return builder.compile()
