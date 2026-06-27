from app.graph.langgraph_workflow import build_research_graph
from app.llm import ChineseLLM
from app.models import ResearchResult
from app.tools.search import SearchTool


def run_research(
    user_query: str,
    *,
    use_mock_search: bool = False,
    search_tool: SearchTool | None = None,
    llm: ChineseLLM | None = None,
) -> ResearchResult:
    graph = build_research_graph(
        use_mock_search=use_mock_search,
        search_tool=search_tool,
        llm=llm,
    )
    state = graph.invoke(
        {
            "user_query": user_query,
            "use_mock_search": use_mock_search,
        }
    )
    return ResearchResult(
        brief=state["brief"],
        plan=state["plan"],
        evidence=state["evidence"],
        report=state["report"],
        visual_graph=state["visual_graph"],
        opposition_matrix=state["opposition_matrix"],
        timeline=state["timeline"],
        exports=state["exports"],
        quality_metrics=state["quality_metrics"],
    )
