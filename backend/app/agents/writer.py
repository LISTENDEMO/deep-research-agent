from app.agents.verifier import summarize_evidence_health
import re

from app.llm import ChineseLLM
from app.models import Evidence, ResearchBrief, ResearchReport, ResearchTask


def _group_by_topic(evidence: list[Evidence]) -> dict[str, list[Evidence]]:
    grouped: dict[str, list[Evidence]] = {}
    for item in evidence:
        grouped.setdefault(item.topic, []).append(item)
    return grouped


def _source_index(evidence: list[Evidence]) -> dict[str, str]:
    labels: dict[str, str] = {}
    for item in evidence:
        if item.source_url not in labels:
            labels[item.source_url] = f"S{len(labels) + 1}"
    return labels


def _pick(items: list[Evidence], stance: str | None = None) -> Evidence | None:
    candidates = [item for item in items if stance is None or item.stance == stance]
    if not candidates:
        return None
    return sorted(candidates, key=lambda item: item.confidence, reverse=True)[0]


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


def _framework_selection_section() -> list[str]:
    return [
        "",
        "## 框架选型矩阵",
        "| 框架 | 最适合场景 | 企业级优势 | 主要风险 | 结论 |",
        "|------|------------|------------|----------|------|",
        "| LangGraph | 有状态、多步骤、可恢复的复杂 Agent 工作流 | 图编排清晰，适合 checkpoint、human-in-the-loop、可观测和生产化控制 | 学习曲线更高，需要更强工程设计 | 企业级复杂流程优先选 LangGraph |",
        "| AutoGen | 多 Agent 对话协作、研究原型、角色间辩论 | 适合快速探索 agent-to-agent 协作模式，表达灵活 | 流程确定性和生产控制需要额外工程约束 | 适合研究/原型，不作为首选生产编排内核 |",
        "| CrewAI | 角色/任务驱动的业务流程自动化 | 上手快，任务分工直观，适合演示和轻量业务工作流 | 复杂状态、回滚、审计和长期运行能力相对弱 | 适合轻量团队式 Agent，不适合最复杂的企业编排 |",
        "",
        "### 推荐结论",
        "如果目标是企业级多 Agent 系统，优先选择 **LangGraph** 作为编排核心；"
        "如果目标是快速验证多角色协作，可以用 **AutoGen** 做研究原型；"
        "如果目标是把业务任务拆给固定角色执行，可以用 **CrewAI** 做轻量自动化。"
        "真正落地时也可以组合使用：LangGraph 负责可靠流程，CrewAI/AutoGen 的思想用于角色建模和协作策略。",
    ]


def _rag_recall_direct_answer() -> list[str]:
    return [
        "",
        "## 直接答案：RAG 提高召回率优先做什么",
        "如果目标是提高 RAG 召回率，优先级通常不是先换大模型，而是按下面顺序优化检索链路：",
        "",
        "| 优先级 | 做法 | 为什么能提高召回 | 主要代价 |",
        "|---|---|---|---|",
        "| P0 | 建立 Recall@k 评估集 | 先知道哪些问题没召回，避免凭感觉调参 | 需要人工标注标准答案/相关文档 |",
        "| P1 | 优化知识覆盖与分块 | 文档没入库、切块割裂上下文时，后续检索再强也找不到 | 需要清洗数据和重建索引 |",
        "| P2 | Query rewrite / Multi-query / HyDE | 扩展用户问题表达，降低 query 与文档表述不一致造成的漏召回 | 增加 LLM 调用成本和延迟 |",
        "| P3 | 混合检索 BM25 + 向量检索 | 同时覆盖关键词精确匹配和语义相似匹配 | 需要融合排序和权重调参 |",
        "| P4 | 扩大候选池后再 rerank | 先多召回，再用重排控制精度，减少早期过滤造成的漏召回 | rerank 成本上升，候选太多会变慢 |",
        "| P5 | Metadata filter / 路由检索 | 按产品、时间、权限、文档类型缩小搜索空间，提高相关文档覆盖 | 元数据质量差会误过滤 |",
        "",
        "推荐默认组合：**评估集 + 分块重建 + hybrid search + multi-query + rerank**。如果只能先做一件事，先做 Recall@k 评估集；如果只能做工程优化，先做分块和混合检索。",
    ]


def _rag_recall_execution_section() -> list[str]:
    return [
        "",
        "## 详细执行方案",
        "| 阶段 | 具体动作 | 产物 | 验收标准 |",
        "|---|---|---|---|",
        "| 1. 建立基线 | 抽取 30-100 个真实用户问题，为每题标注应命中文档、答案片段和不可接受来源 | `recall_eval_set.jsonl`、基线报告 | 有 Recall@5、Recall@10、MRR/nDCG、答案引用覆盖率的初始分数 |",
        "| 2. 数据与分块 | 清理重复/过期文档，按标题层级、段落语义和表格边界切块，保留 parent doc 与 section metadata | 新索引、chunk 质量抽样表 | 漏召回问题中由“文档没入库/切块断裂”造成的比例明显下降 |",
        "| 3. Query 扩展 | 对短问题做 query rewrite，对复杂问题做 multi-query，对概念型问题可测试 HyDE | query expansion 模块与日志 | Recall@10 上升，且无关候选比例没有大幅恶化 |",
        "| 4. 混合召回 | 同时跑 BM25 和向量检索，用 RRF 或加权融合合并候选 | hybrid retriever | 精确关键词问题和语义问题都能命中，不再偏向单一检索方式 |",
        "| 5. 扩大候选池 + 重排 | top_k 从小到大做网格实验，再用 reranker 控制最终上下文 | rerank 配置和阈值表 | Recall@10 提升，同时最终引用相关性和回答正确率不下降 |",
        "| 6. 路由与过滤 | 按产品线、权限、时间、文档类型做 metadata filter，但保留 fallback 检索 | retriever router | 权限正确，误过滤率可解释，低置信度时能回退到更宽召回 |",
        "",
        "## 指标与验收标准",
        "- **主指标**：Recall@5 / Recall@10，用来判断相关文档是否被召回。",
        "- **排序指标**：MRR 或 nDCG，用来判断相关文档是否排在前面。",
        "- **答案指标**：引用覆盖率、faithfulness、人工正确率，避免只提高召回却让答案变差。",
        "- **工程指标**：P95 延迟、token 成本、rerank 成本、无关候选比例。",
        "- **上线门槛**：固定评估集 Recall@10 提升，并且 P95 延迟和成本在业务可接受范围内。",
        "",
        "## 30 天落地计划",
        "1. **第 1 周**：整理真实问题、标注黄金文档、跑当前 RAG 基线，定位漏召回类型。",
        "2. **第 2 周**：重做数据清洗、分块策略和 metadata，重新构建索引。",
        "3. **第 3 周**：接入 query rewrite、multi-query、hybrid search，并做 top_k / 权重实验。",
        "4. **第 4 周**：加入 rerank、阈值和路由策略，灰度上线并持续记录错误样本。",
    ]


def _rag_trust_direct_answer() -> list[str]:
    return [
        "",
        "## 直接答案：企业知识库 RAG 如何降低幻觉并保证可追溯",
        "核心答案：不要只靠提示词要求模型“不要乱说”，而要把系统设计成 **先检索、再校验、后生成、可回放** 的证据链。企业知识库 RAG 的可信度来自四层防线：知识治理、检索约束、生成约束、答案审计。",
        "",
        "| 防线 | 具体做法 | 降低幻觉的机制 | 可追溯产物 |",
        "|---|---|---|---|",
        "| 1. 知识治理 | 文档入库前做去重、版本控制、权限标签、有效期和负责人标记 | 避免模型引用过期、重复、无权限或来源不明内容 | doc_id、version、owner、updated_at、acl、source_url |",
        "| 2. 检索约束 | 使用 hybrid search、metadata filter、rerank、最小置信度阈值 | 让模型只看到与问题相关且权限正确的上下文 | query、retrieved_chunk_ids、score、rerank_score、filter 条件 |",
        "| 3. 生成约束 | Prompt 强制“答案必须引用 chunk id；证据不足就说不知道；不得使用未检索知识” | 把自由生成改成基于证据的受控生成 | answer、citation_map、unsupported_claims |",
        "| 4. 答案审计 | 生成后做 citation coverage、faithfulness check、事实一致性检查和人工抽检 | 拦截没有证据支撑的句子，沉淀错误样本 | run_id、claim_to_evidence、risk_score、review_status |",
        "",
        "一句话落地方案：**所有回答必须能从句子追到 chunk，再从 chunk 追到文档版本、权限、来源和检索日志；追不到就不允许作为确定答案输出。**",
    ]


def _rag_trust_execution_section() -> list[str]:
    return [
        "",
        "## 详细执行方案",
        "| 阶段 | 要做什么 | 关键实现 | 验收标准 |",
        "|---|---|---|---|",
        "| 1. 建立知识资产台账 | 给每份知识文档绑定唯一 `doc_id`、版本、来源、负责人、更新时间、权限范围 | 文档清洗流水线 + metadata schema + ACL 同步 | 任意 chunk 都能反查原文、版本、来源和权限 |",
        "| 2. 做可追溯分块 | 分块时保留 `chunk_id`、标题路径、页码/段落、父文档、字符范围 | hierarchical chunking + parent-child retrieval | 引用能定位到原文段落，而不是只定位到整篇文档 |",
        "| 3. 控制检索入口 | 查询先做意图识别和权限过滤，再执行 BM25 + vector + rerank | metadata filter、hybrid retriever、reranker | 无权限文档不会进入上下文，top_k 结果可解释 |",
        "| 4. 约束生成格式 | 要求模型输出答案、引用列表、证据不足说明和置信度 | structured output / JSON schema / citation required prompt | 每个关键句至少对应一个 chunk_id；无证据句子被标记 |",
        "| 5. 二次校验 | 对生成答案做 claim 分解，逐条检查是否被引用证据支持 | faithfulness checker、NLI/LLM judge、规则检查 | unsupported claim 比例低于阈值，失败则改写或拒答 |",
        "| 6. 日志与回放 | 保存 query、检索结果、rerank 分数、上下文、prompt、答案和引用映射 | run store + evidence store + report id | 出问题时能复现当时为什么这样回答 |",
        "",
        "## 关键指标",
        "- **Citation coverage**：报告中有多少关键句绑定了引用，建议核心答案达到 90%+。",
        "- **Faithfulness / groundedness**：答案中的 claim 是否被检索证据支持。",
        "- **Unsupported claim rate**：没有证据支撑的句子比例，超过阈值就拒答或降级。",
        "- **Retrieval precision@k**：进入上下文的 chunk 是否真的相关，避免噪声诱导幻觉。",
        "- **ACL violation rate**：是否错误引用了无权限文档，企业场景必须接近 0。",
        "- **Trace replay success rate**：抽样答案能否完整回放 query -> chunks -> answer -> citations。",
        "",
        "## 推荐系统策略",
        "1. **证据不足时拒答**：不要让模型“补全常识”，输出“当前知识库没有足够证据”。",
        "2. **引用不是装饰**：引用必须绑定到 chunk_id，而不是只给一个网页链接或文档名。",
        "3. **答案生成后再验一次**：先生成不等于可信，必须做 claim-level 校验。",
        "4. **低置信度要降级**：当检索分数低、来源冲突或引用覆盖不足时，给出不确定性说明。",
        "5. **把错误变成评估集**：每次幻觉或错误引用都进入 regression dataset，防止下次复发。",
    ]


def _generic_execution_section(
    brief: ResearchBrief,
    grouped: dict[str, list[Evidence]],
    source_labels: dict[str, str],
) -> list[str]:
    lines = [
        "",
        "## 详细执行方案",
        "| 阶段 | 要回答的问题 | 推荐动作 | 验收标准 |",
        "|---|---|---|---|",
    ]
    for index, (topic, items) in enumerate(grouped.items(), start=1):
        best = _pick(items, "support") or _pick(items)
        risk = _pick(items, "oppose")
        evidence_note = f"{best.claim}[{source_labels[best.source_url]}]" if best else "补充权威来源"
        risk_note = f"；同时验证风险：{risk.claim}[{source_labels[risk.source_url]}]" if risk else ""
        lines.append(
            f"| {index}. {topic} | 这个主题对“{brief.original_query}”意味着什么 | "
            f"基于证据形成判断：{evidence_note}{risk_note} | 能给出明确结论、引用来源和风险边界 |"
        )
    if len(lines) == 4:
        lines.append(
            "| 1. 补充证据 | 当前资料是否足够支持结论 | 优先搜索官方文档、论文、源码仓库或一手数据 | 至少有 3 个高质量来源，且包含反方风险 |"
        )
    lines.extend(
        [
            "",
            "## 验收标准",
            "- 结论必须直接回答原问题，而不是只复述搜索结果。",
            "- 每个关键判断至少绑定一个来源编号。",
            "- 风险和反方观点必须单独列出，避免单边推荐。",
            "- 最终建议必须能转化成下一步行动。",
        ]
    )
    return lines


def _generic_direct_answer(
    brief: ResearchBrief,
    grouped: dict[str, list[Evidence]],
    source_labels: dict[str, str],
) -> list[str]:
    lines = ["", "## 直接答案"]
    best_items: list[Evidence] = []
    for items in grouped.values():
        best = _pick(items, "support") or _pick(items)
        if best:
            best_items.append(best)
    if not best_items:
        lines.append(f"围绕“{brief.original_query}”，当前证据不足以给出强结论，建议先补充更权威来源和评估指标。")
        return lines
    for index, item in enumerate(best_items[:4], start=1):
        lines.append(f"{index}. {item.claim}[{source_labels[item.source_url]}]")
    return lines


def _topic_specific_final_advice(query: str) -> list[str]:
    if _is_framework_selection_query(query):
        return [
            "优先选择能提供可恢复状态、明确工具边界、可观测执行过程的 Agent 框架；对学习曲线、运行成本、来源质量和工具稳定性要单独评估。"
        ]
    if _is_rag_trust_query(query):
        return [
            "企业知识库 RAG 的可信度不是靠模型自觉，而是靠可追溯数据结构、受控检索、引用约束和生成后校验共同保证。",
            "如果短期只能做一件事，先把 citation map 和 run log 做完整：每句答案能追到 chunk，每个 chunk 能追到文档版本和权限。",
        ]
    if _is_rag_recall_query(query):
        return [
            "落地时不要只看单次回答是否变好，而要建立固定问题集，持续观察 Recall@5/Recall@10、命中来源质量、重排后准确率、延迟和 token 成本。",
            "当召回率上升但答案质量下降时，说明候选池噪声过高，需要 rerank、阈值控制或按场景路由，而不是继续盲目扩大 top_k。",
        ]
    return ["先把问题拆成可验证假设，再用证据和指标决定优先级；不要把搜索结果摘要当成最终结论。"]


def _evidence_context(evidence: list[Evidence], source_labels: dict[str, str]) -> str:
    lines: list[str] = []
    for item in evidence:
        label = source_labels[item.source_url]
        lines.append(
            "\n".join(
                [
                    f"[{label}]",
                    f"topic: {item.topic}",
                    f"stance: {item.stance}",
                    f"claim: {item.claim}",
                    f"quote: {item.quote}",
                    f"source_title: {item.source_title}",
                    f"source_url: {item.source_url}",
                ]
            )
        )
    return "\n\n".join(lines)


def _plan_context(plan: list[ResearchTask]) -> str:
    return "\n".join(f"- {task.title}: {task.rationale}" for task in plan)


def _build_llm_writer_prompt(
    brief: ResearchBrief,
    plan: list[ResearchTask],
    evidence: list[Evidence],
    source_labels: dict[str, str],
    fallback_markdown: str,
) -> str:
    return f"""你是一个中文 Deep Research Writer。请基于给定 Evidence 写一份可执行中文研究报告。

硬性要求：
1. 只能使用 Evidence 中的信息和明确可由 Evidence 推出的结论，不要编造来源、数据、论文或产品能力。
2. 关键判断必须使用 [S1]、[S2] 这种来源编号引用，编号只能来自 Evidence。
3. 如果证据不足，必须写“当前证据不足”，不能自由补全。
4. 输出 Markdown，不要输出 JSON，不要解释你的写作过程。
5. 必须包含这些二级标题：## 执行摘要、## 直接答案、## 关键判断、## 风险与反方观点、## 落地路线、## 引用来源。
6. 报告要直接回答用户问题，不要只复述搜索结果。

用户问题：
{brief.original_query}

研究目标：
{brief.objective}

研究拆解：
{_plan_context(plan)}

Evidence：
{_evidence_context(evidence, source_labels)}

下面是系统规则 Writer 的兜底结构，你可以参考它的结构，但不要照抄噪声 claim：
{fallback_markdown[:4000]}
"""


def _unknown_citations(markdown: str, source_labels: dict[str, str]) -> set[str]:
    valid = set(source_labels.values())
    used = set(re.findall(r"\[(S\d+)\]", markdown))
    return used - valid


def _is_valid_llm_markdown(markdown: str, source_labels: dict[str, str]) -> bool:
    if len(markdown.strip()) < 300:
        return False
    required_sections = ["## 执行摘要", "## 直接答案", "## 关键判断", "## 落地路线"]
    if not all(section in markdown for section in required_sections):
        return False
    if source_labels and not re.search(r"\[S\d+\]", markdown):
        return False
    return not _unknown_citations(markdown, source_labels)


def _append_source_index_if_missing(markdown: str, evidence: list[Evidence], source_labels: dict[str, str]) -> str:
    if "## 引用来源" in markdown:
        return markdown
    lines = [markdown.rstrip(), "", "## 引用来源"]
    for url, label in source_labels.items():
        source = next(item for item in evidence if item.source_url == url)
        lines.append(f"- [{label}] [{source.source_title}]({source.source_url})：{source.quote[:140]}")
    return "\n".join(lines)


def _try_llm_report(
    *,
    brief: ResearchBrief,
    plan: list[ResearchTask],
    evidence: list[Evidence],
    source_labels: dict[str, str],
    fallback_markdown: str,
    llm: ChineseLLM | None,
) -> ResearchReport | None:
    if llm is None:
        return None
    if llm.__class__.__name__ == "RuleBasedChineseLLM":
        return None
    try:
        prompt = _build_llm_writer_prompt(brief, plan, evidence, source_labels, fallback_markdown)
        markdown = llm.generate(prompt).strip()
    except Exception:
        return None
    if not markdown.startswith("# "):
        markdown = f"# Deep Research 报告：{brief.original_query}\n\n{markdown}"
    markdown = _append_source_index_if_missing(markdown, evidence, source_labels)
    if not _is_valid_llm_markdown(markdown, source_labels):
        return None
    return ResearchReport(title=markdown.splitlines()[0], markdown=markdown)


def _write_rule_report(
    brief: ResearchBrief,
    plan: list[ResearchTask],
    evidence: list[Evidence],
) -> ResearchReport:
    health = summarize_evidence_health(evidence)
    grouped = _group_by_topic(evidence)
    source_labels = _source_index(evidence)

    lines = [
        f"# Deep Research 报告：{brief.original_query}",
        "",
        "## 执行摘要",
        f"本报告直接回答“{brief.original_query}”，并把建议拆成机制、证据、风险和落地验证。重点不是堆资料，而是给出可执行优先级。",
    ]

    if _is_rag_trust_query(brief.original_query):
        lines.extend(_rag_trust_direct_answer())
    elif _is_rag_recall_query(brief.original_query):
        lines.extend(_rag_recall_direct_answer())
    else:
        lines.extend(_generic_direct_answer(brief, grouped, source_labels))

    lines.extend(["", "## 研究目标", brief.objective, "", "## 研究拆解"])
    for task in plan:
        lines.append(f"- **{task.title}**：{task.rationale}")

    if _is_framework_selection_query(brief.original_query):
        lines.extend(_framework_selection_section())

    if _is_rag_trust_query(brief.original_query):
        lines.extend(_rag_trust_execution_section())
    elif _is_rag_recall_query(brief.original_query):
        lines.extend(_rag_recall_execution_section())
    else:
        lines.extend(_generic_execution_section(brief, grouped, source_labels))

    lines.extend(["", "## 关键判断"])
    for topic, items in grouped.items():
        support = _pick(items, "support") or _pick(items)
        risk = _pick(items, "oppose")
        if support is None:
            continue
        support_label = source_labels[support.source_url]
        if risk:
            risk_label = source_labels[risk.source_url]
            lines.append(
                f"- **{topic}**：{support.claim}。需要同时关注：{risk.claim}。"
                f"[{support_label}][{risk_label}]"
            )
        else:
            lines.append(f"- **{topic}**：{support.claim}。[{support_label}]")

    lines.extend(["", "## 观点对立与风险"])
    for topic, items in grouped.items():
        supports = [item for item in items if item.stance == "support"]
        risks = [item for item in items if item.stance == "oppose"]
        neutrals = [item for item in items if item.stance == "neutral"]
        lines.append(f"### {topic}")
        if supports:
            lines.append("- 支持侧：" + "；".join(f"{item.claim}[{source_labels[item.source_url]}]" for item in supports[:2]))
        if risks:
            lines.append("- 风险侧：" + "；".join(f"{item.claim}[{source_labels[item.source_url]}]" for item in risks[:2]))
        if neutrals:
            lines.append("- 背景信息：" + "；".join(f"{item.claim}[{source_labels[item.source_url]}]" for item in neutrals[:2]))

    lines.extend(
        [
            "",
            "## 落地路线",
            "1. **先建立评估集**：固定一批代表性问题和应命中文档，用指标验证改动是否真的提升。",
            "2. **再调关键链路**：按数据覆盖、分块、检索策略、重排、阈值的顺序优化，避免一开始就堆复杂方案。",
            "3. **记录副作用**：每次优化同时记录延迟、成本、噪声比例和最终答案质量。",
            "4. **小流量上线**：先在低风险场景灰度验证，再扩展到核心业务流程。",
            "",
            "## 证据健康度",
            f"- 支持证据：{health['support']}",
            f"- 风险/反对证据：{health['oppose']}",
            f"- 中立证据：{health['neutral']}",
            "",
            "## 引用来源",
        ]
    )
    for url, label in source_labels.items():
        source = next(item for item in evidence if item.source_url == url)
        lines.append(f"- [{label}] [{source.source_title}]({source.source_url})：{source.quote[:140]}")

    lines.extend(["", "## 初步建议"])
    lines.extend(_topic_specific_final_advice(brief.original_query))

    markdown = "\n".join(lines)
    return ResearchReport(title=lines[0], markdown=markdown)


def write_report(
    brief: ResearchBrief,
    plan: list[ResearchTask],
    evidence: list[Evidence],
    llm: ChineseLLM | None = None,
) -> ResearchReport:
    rule_report = _write_rule_report(brief, plan, evidence)
    source_labels = _source_index(evidence)
    llm_report = _try_llm_report(
        brief=brief,
        plan=plan,
        evidence=evidence,
        source_labels=source_labels,
        fallback_markdown=rule_report.markdown,
        llm=llm,
    )
    return llm_report or rule_report
