from collections import defaultdict

from app.models import Evidence, OppositionMatrixRow, ResearchBrief, ResearchTask, TimelineEvent


def build_opposition_matrix(evidence: list[Evidence]) -> list[OppositionMatrixRow]:
    grouped: dict[str, dict[str, list[Evidence]]] = defaultdict(lambda: defaultdict(list))
    for item in evidence:
        grouped[item.topic][item.stance].append(item)

    rows: list[OppositionMatrixRow] = []
    for topic, stance_groups in grouped.items():
        topic_evidence = [item for items in stance_groups.values() for item in items]
        avg_confidence = (
            sum(item.confidence for item in topic_evidence) / len(topic_evidence)
            if topic_evidence
            else 0
        )
        rows.append(
            OppositionMatrixRow(
                topic=topic,
                support_claims=[item.claim for item in stance_groups["support"]],
                oppose_claims=[item.claim for item in stance_groups["oppose"]],
                neutral_claims=[item.claim for item in stance_groups["neutral"]],
                confidence=round(avg_confidence, 2),
            )
        )
    return rows


def build_timeline(
    brief: ResearchBrief,
    plan: list[ResearchTask],
    evidence: list[Evidence],
) -> list[TimelineEvent]:
    return [
        TimelineEvent(
            step="scope",
            title="Scope Agent 生成研究简报",
            description=f"明确研究目标：{brief.objective}",
        ),
        TimelineEvent(
            step="plan",
            title="Supervisor 拆解研究任务",
            description=f"生成 {len(plan)} 个可并行研究子任务。",
        ),
        TimelineEvent(
            step="research",
            title="Researcher 搜索并抽取证据",
            description=f"收集 {len(evidence)} 条支持、反对或中立证据。",
        ),
        TimelineEvent(
            step="verify",
            title="Verifier 生成观点对立矩阵",
            description="按主题聚合支持证据、风险证据与置信度。",
        ),
        TimelineEvent(
            step="write",
            title="Writer 统一生成报告",
            description="统一写作，避免多 Agent 分段写作造成风格割裂。",
        ),
    ]
