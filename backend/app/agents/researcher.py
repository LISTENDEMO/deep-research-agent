from app.models import Evidence, ResearchTask, SearchResult


def extract_evidence(task: ResearchTask, results: list[SearchResult]) -> list[Evidence]:
    evidence: list[Evidence] = []
    for index, result in enumerate(results, start=1):
        content = result.content.strip()
        stance = _infer_stance(content)
        evidence.append(
            Evidence(
                id=f"{task.id}-e{index}",
                task_id=task.id,
                claim=_build_claim(task, content, stance),
                source_title=result.title,
                source_url=result.url,
                quote=content[:220],
                stance=stance,
                confidence=_confidence_for_stance(stance),
                topic=task.title,
            )
        )
    return evidence


def _infer_stance(content: str) -> str:
    lower = content.lower()
    support_words = ["support", "suitable", "优势", "适合", "具备", "成熟", "提高", "提升", "优化", "扩大", "改善", "建立", "降低"]
    risk_words = ["risk", "limitation", "限制", "风险", "学习曲线", "成本", "错误", "漏召回", "噪声"]
    if any(phrase in lower for phrase in ["风险包括", "主要风险", "需要防范", "risk includes"]):
        return "oppose"
    if any(word in lower for word in support_words):
        return "support"
    if any(word in lower for word in risk_words):
        return "oppose"
    return "neutral"


def _confidence_for_stance(stance: str) -> float:
    if stance == "support":
        return 0.82
    if stance == "oppose":
        return 0.74
    return 0.62


def _build_claim(task: ResearchTask, content: str, stance: str) -> str:
    sentence = _first_sentence(content)
    if stance == "support":
        return f"{task.title}建议：{sentence}"
    if stance == "oppose":
        return f"{task.title}需要防范：{sentence}"
    return f"{task.title}补充信息：{sentence}"


def _first_sentence(content: str) -> str:
    compact = " ".join(content.split())
    for separator in ["。", "；", ";", ". "]:
        if separator in compact:
            first = compact.split(separator, 1)[0].strip()
            if len(first) >= 18:
                return first[:120]
    return compact[:120]
