from app.models import Evidence, ResearchBrief, ResearchTask


def build_visual_graph(
    brief: ResearchBrief,
    plan: list[ResearchTask],
    evidence: list[Evidence],
) -> dict:
    nodes = [
        {
            "id": "brief",
            "label": brief.original_query,
            "type": "brief",
            "stance": "neutral",
            "confidence": 1,
        }
    ]
    links = []
    for task in plan:
        nodes.append(
            {
                "id": task.id,
                "label": task.title,
                "type": "task",
                "stance": "neutral",
                "confidence": 0.8,
            }
        )
        links.append({"source": "brief", "target": task.id, "type": "decomposes"})

    for item in evidence:
        nodes.append(
            {
                "id": item.id,
                "label": item.claim,
                "type": "evidence",
                "stance": item.stance,
                "confidence": item.confidence,
                "url": item.source_url,
            }
        )
        links.append({"source": item.task_id, "target": item.id, "type": "supports"})

    return {"nodes": nodes, "links": links}
