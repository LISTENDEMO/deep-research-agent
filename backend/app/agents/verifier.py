from collections import Counter

from app.models import Evidence


def summarize_evidence_health(evidence: list[Evidence]) -> dict[str, int]:
    counts = Counter(item.stance for item in evidence)
    return {
        "support": counts["support"],
        "oppose": counts["oppose"],
        "neutral": counts["neutral"],
        "total": len(evidence),
    }
