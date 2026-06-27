from app.models import ResearchBrief, ResearchTask


def plan_research(brief: ResearchBrief) -> list[ResearchTask]:
    if _is_framework_selection_query(brief.original_query):
        topics = [
            ("architecture", "技术架构与工作流能力", "LangGraph AutoGen CrewAI comparison enterprise agent orchestration stateful workflow"),
            ("ecosystem", "生态成熟度与工具集成", "LangGraph AutoGen CrewAI ecosystem documentation production integration"),
            ("risk", "风险、限制与反方观点", "LangGraph AutoGen CrewAI limitations learning curve production risks"),
            ("recommendation", "落地建议与选型结论", "LangGraph vs AutoGen vs CrewAI enterprise use cases recommendation"),
        ]
    elif _is_rag_trust_query(brief.original_query):
        topics = [
            ("governance", "知识治理与权限元数据", "enterprise RAG knowledge governance metadata ACL document version source traceability"),
            ("retrieval", "受控检索与证据选择", "enterprise RAG hallucination mitigation hybrid retrieval metadata filter rerank grounded context"),
            ("citation", "引用映射与生成后校验", "RAG citation mapping faithfulness groundedness unsupported claims verification"),
            ("audit", "审计日志与评估指标", "RAG audit log traceability citation coverage faithfulness evaluation replay"),
        ]
    elif _is_rag_recall_query(brief.original_query):
        topics = [
            ("query", "查询改写与召回扩展", "RAG improve recall query rewriting multi query HyDE query expansion"),
            ("index", "分块、索引与数据覆盖", "RAG recall chunking indexing metadata hybrid sparse dense retrieval"),
            ("retrieval", "混合检索、重排与候选池", "RAG recall hybrid search reranking candidate pool recall@k"),
            ("evaluation", "评估指标与上线取舍", "RAG recall evaluation recall@k nDCG latency noise cost tradeoff"),
        ]
    else:
        topics = [
            ("mechanism", "核心机制", "原理 机制 为什么有效"),
            ("methods", "可执行方法", "方法 步骤 最佳实践 实施方案"),
            ("risk", "限制、代价与反例", "风险 限制 成本 副作用 失败原因"),
            ("evaluation", "评估指标与落地路径", "评估 指标 落地 路线 优先级"),
        ]
    return [
        ResearchTask(
            id=f"task-{index + 1}",
            title=title,
            query=keywords if _is_framework_selection_query(brief.original_query) else f"{brief.original_query} {keywords}",
            rationale=f"该子任务用于回答：{title}。",
        )
        for index, (_, title, keywords) in enumerate(topics)
    ]


def _is_framework_selection_query(query: str) -> bool:
    lowered = query.lower()
    return all(name in lowered for name in ["langgraph", "autogen", "crewai"])


def _is_rag_recall_query(query: str) -> bool:
    lowered = query.lower()
    return "rag" in lowered and any(word in lowered for word in ["召回", "recall", "检索"])


def _is_rag_trust_query(query: str) -> bool:
    lowered = query.lower()
    trust_words = ["幻觉", "可追溯", "追溯", "溯源", "引用", "可信", "trace", "ground", "faithfulness"]
    return "rag" in lowered and any(word in lowered for word in trust_words)
