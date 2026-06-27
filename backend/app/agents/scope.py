from app.models import ResearchBrief


def generate_brief(user_query: str) -> ResearchBrief:
    normalized = " ".join(user_query.strip().split())
    objective = f"直接回答“{normalized}”，并给出可验证、可执行、可落地的中文研究结论。"
    return ResearchBrief(
        original_query=normalized,
        objective=objective,
        scope=[
            "核心机制",
            "优先级方案",
            "实施代价与风险",
            "评估指标与落地步骤",
        ],
        deliverables=[
            "直接结论",
            "优先级行动清单",
            "带来源引用的关键证据",
            "风险与验证指标",
        ],
        success_criteria=[
            "开头必须直接回答用户问题",
            "每个核心建议至少有证据或机制解释",
            "最终输出必须包含可执行下一步",
        ],
    )
