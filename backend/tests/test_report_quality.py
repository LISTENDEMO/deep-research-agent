from app.agents.writer import write_report
from app.models import Evidence, ResearchBrief, ResearchTask


class FakeWriterLLM:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls: list[str] = []

    def generate(self, prompt: str) -> str:
        self.calls.append(prompt)
        return self.response


def test_writer_synthesizes_evidence_into_actionable_sections() -> None:
    brief = ResearchBrief(
        original_query="研究 LangGraph、AutoGen、CrewAI 哪个更适合企业级多 Agent 系统",
        objective="比较三个框架并给出企业落地建议。",
    )
    plan = [
        ResearchTask(
            id="task-1",
            title="技术架构与工作流能力",
            query="",
            rationale="比较状态管理、恢复能力和编排方式。",
        ),
        ResearchTask(
            id="task-2",
            title="风险、限制与反方观点",
            query="",
            rationale="识别学习曲线、成本和稳定性风险。",
        ),
    ]
    evidence = [
        Evidence(
            id="e1",
            task_id="task-1",
            claim="LangGraph 更适合有状态、多步骤、可恢复的 Agent 工作流。",
            source_title="LangGraph docs",
            source_url="https://example.com/langgraph",
            quote="stateful workflows and durable execution",
            stance="support",
            confidence=0.86,
            topic="技术架构与工作流能力",
        ),
        Evidence(
            id="e2",
            task_id="task-2",
            claim="企业落地复杂 Agent 时需要关注学习曲线、监控和工具调用稳定性。",
            source_title="Agent risk memo",
            source_url="https://example.com/risk",
            quote="learning curve and operational risk",
            stance="oppose",
            confidence=0.78,
            topic="风险、限制与反方观点",
        ),
    ]

    report = write_report(brief, plan, evidence)

    assert "## 关键判断" in report.markdown
    assert "## 观点对立与风险" in report.markdown
    assert "## 详细执行方案" in report.markdown
    assert "## 验收标准" in report.markdown
    assert "## 落地路线" in report.markdown
    assert "## 引用来源" in report.markdown
    assert "[S1]" in report.markdown
    assert "可执行优先级" in report.markdown


def test_writer_adds_framework_selection_matrix_for_langgraph_autogen_crewai() -> None:
    brief = ResearchBrief(
        original_query="研究 LangGraph、AutoGen、CrewAI 哪个更适合企业级多 Agent 系统",
        objective="给出企业级多 Agent 框架选型建议。",
    )
    plan = [
        ResearchTask(id="task-1", title="技术架构与工作流能力", query="", rationale=""),
    ]
    evidence = [
        Evidence(
            id="e1",
            task_id="task-1",
            claim="LangGraph 支持有状态图、检查点和可恢复工作流。",
            source_title="LangGraph",
            source_url="https://example.com/langgraph",
            quote="stateful graph workflows",
            stance="support",
            confidence=0.86,
            topic="技术架构与工作流能力",
        )
    ]

    report = write_report(brief, plan, evidence)

    assert "## 框架选型矩阵" in report.markdown
    assert "| LangGraph |" in report.markdown
    assert "| AutoGen |" in report.markdown
    assert "| CrewAI |" in report.markdown
    assert "企业级复杂流程优先选 LangGraph" in report.markdown


def test_writer_answers_rag_recall_with_actionable_priority_table() -> None:
    brief = ResearchBrief(
        original_query="RAG怎么提高召回率",
        objective="给出提高 RAG 召回率的有效方案。",
    )
    plan = [
        ResearchTask(id="task-1", title="查询改写与召回扩展", query="", rationale="研究 query rewrite、multi-query 和 HyDE。"),
        ResearchTask(id="task-2", title="分块、索引与数据覆盖", query="", rationale="研究 chunking、metadata 和 hybrid retrieval。"),
    ]
    evidence = [
        Evidence(
            id="e1",
            task_id="task-1",
            claim="Multi-query 和 query rewrite 能扩展用户问题表达，降低语义失配导致的漏召回。",
            source_title="RAG recall guide",
            source_url="https://example.com/rag-recall",
            quote="query expansion improves recall by covering more formulations",
            stance="support",
            confidence=0.82,
            topic="查询改写与召回扩展",
        ),
        Evidence(
            id="e2",
            task_id="task-2",
            claim="分块过粗或过细都会影响相关片段召回，应该结合文档结构和评估集调参。",
            source_title="Chunking guide",
            source_url="https://example.com/chunking",
            quote="chunk size affects retrieval recall and precision",
            stance="support",
            confidence=0.82,
            topic="分块、索引与数据覆盖",
        ),
    ]

    report = write_report(brief, plan, evidence)

    assert "## 直接答案：RAG 提高召回率优先做什么" in report.markdown
    assert "Recall@k" in report.markdown
    assert "Query rewrite" in report.markdown
    assert "hybrid search" in report.markdown
    assert "## 详细执行方案" in report.markdown
    assert "## 30 天落地计划" in report.markdown
    assert "Agent 框架" not in report.markdown


def test_writer_answers_enterprise_rag_trust_without_noisy_claims() -> None:
    brief = ResearchBrief(
        original_query="企业知识库 RAG 如何降低幻觉并保证可追溯？",
        objective="给出企业知识库 RAG 降低幻觉和保证可追溯的工程方案。",
    )
    plan = [
        ResearchTask(id="task-1", title="核心机制", query="", rationale="研究 grounded generation 和 citation。"),
        ResearchTask(id="task-2", title="评估指标", query="", rationale="研究 faithfulness、citation coverage 和审计日志。"),
    ]
    evidence = [
        Evidence(
            id="e1",
            task_id="task-1",
            claim="人人都是产品经理 搜索 APP 起点课堂会员权益 职业体系课特权 线下行业大会特权",
            source_title="Noisy content farm",
            source_url="https://example.com/noisy",
            quote="irrelevant membership text",
            stance="support",
            confidence=0.91,
            topic="核心机制",
        ),
        Evidence(
            id="e2",
            task_id="task-2",
            claim="企业 RAG 应记录 query、retrieved_chunk_ids、score、answer 和 citation map 以支持审计回放。",
            source_title="RAG audit guide",
            source_url="https://example.com/rag-audit",
            quote="trace every answer to chunks and source documents",
            stance="support",
            confidence=0.82,
            topic="评估指标",
        ),
    ]

    report = write_report(brief, plan, evidence)

    assert "## 直接答案：企业知识库 RAG 如何降低幻觉并保证可追溯" in report.markdown
    assert "先检索、再校验、后生成、可回放" in report.markdown
    assert "citation_map" in report.markdown
    assert "unsupported_claims" in report.markdown
    assert "人人都是产品经理" not in report.markdown.split("## 研究目标")[0]


def test_writer_uses_llm_when_valid_markdown_is_returned() -> None:
    brief = ResearchBrief(
        original_query="研究 AI Agent 可观测性",
        objective="给出可观测性建设建议。",
    )
    plan = [ResearchTask(id="task-1", title="指标体系", query="", rationale="研究日志、指标和链路追踪。")]
    evidence = [
        Evidence(
            id="e1",
            task_id="task-1",
            claim="Agent 可观测性需要记录工具调用、输入输出、延迟和错误。",
            source_title="Observability guide",
            source_url="https://example.com/observability",
            quote="trace tool calls, latency and errors",
            stance="support",
            confidence=0.84,
            topic="指标体系",
        )
    ]
    llm = FakeWriterLLM(
        "# Deep Research 报告：研究 AI Agent 可观测性\n\n"
        "## 执行摘要\n这是 LLM Writer 生成标记，核心结论来自证据[S1]。\n\n"
        "## 直接答案\n应该记录工具调用、输入输出、延迟和错误[S1]。\n\n"
        "## 关键判断\n- 可观测性建设要覆盖 trace、metrics 和错误回放[S1]。\n\n"
        "## 风险与反方观点\n- 如果日志缺少脱敏，会带来安全风险[S1]。\n\n"
        "## 落地路线\n1. 先采集 run log。\n2. 再建设评估集。\n\n"
        "## 引用来源\n- [S1] [Observability guide](https://example.com/observability)：trace tool calls, latency and errors"
    )

    report = write_report(brief, plan, evidence, llm=llm)

    assert llm.calls
    assert "LLM Writer 生成标记" in report.markdown
    assert "[S1]" in report.markdown


def test_writer_falls_back_when_llm_markdown_is_invalid() -> None:
    brief = ResearchBrief(
        original_query="研究 AI Agent 可观测性",
        objective="给出可观测性建设建议。",
    )
    plan = [ResearchTask(id="task-1", title="指标体系", query="", rationale="研究日志、指标和链路追踪。")]
    evidence = [
        Evidence(
            id="e1",
            task_id="task-1",
            claim="Agent 可观测性需要记录工具调用、输入输出、延迟和错误。",
            source_title="Observability guide",
            source_url="https://example.com/observability",
            quote="trace tool calls, latency and errors",
            stance="support",
            confidence=0.84,
            topic="指标体系",
        )
    ]
    llm = FakeWriterLLM("一句没有结构、没有引用的短回答。")

    report = write_report(brief, plan, evidence, llm=llm)

    assert llm.calls
    assert "一句没有结构" not in report.markdown
    assert "## 关键判断" in report.markdown
