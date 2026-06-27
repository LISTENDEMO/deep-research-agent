from app.models import Evidence, OppositionMatrixRow


def evaluate_research_quality(
    evidence: list[Evidence],
    opposition_matrix: list[OppositionMatrixRow],
) -> dict[str, float | int]:
    if not evidence:
        return {
            "citation_coverage": 0.0,
            "source_count": 0,
            "opposition_balance": 0.0,
            "hallucination_risk": 1.0,
        }

    cited = [item for item in evidence if item.source_url and item.quote]
    citation_coverage = len(cited) / len(evidence)
    source_count = len({item.source_url for item in cited})
    topics_with_opposition = [
        row
        for row in opposition_matrix
        if row.support_claims and row.oppose_claims
    ]
    opposition_balance = (
        len(topics_with_opposition) / len(opposition_matrix)
        if opposition_matrix
        else 0.0
    )
    average_confidence = sum(item.confidence for item in evidence) / len(evidence)
    hallucination_risk = 1 - ((citation_coverage * 0.5) + (average_confidence * 0.35) + (opposition_balance * 0.15))

    return {
        "citation_coverage": round(citation_coverage, 2),
        "source_count": source_count,
        "opposition_balance": round(opposition_balance, 2),
        "hallucination_risk": round(max(0.0, min(1.0, hallucination_risk)), 2),
    }
