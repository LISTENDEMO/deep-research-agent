from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.graph.runner import run_research  # noqa: E402


def main() -> None:
    tasks_path = ROOT / "examples" / "demo_tasks.json"
    tasks = json.loads(tasks_path.read_text(encoding="utf-8"))

    for task in tasks:
        result = run_research(task["query"], use_mock_search=True)
        metrics = result.quality_metrics
        print(f"\n## {task['name']}")
        print(f"Query: {task['query']}")
        print(f"Evidence: {len(result.evidence)}")
        print(f"Citation coverage: {metrics['citation_coverage']}")
        print(f"Source count: {metrics['source_count']}")
        print(f"Opposition balance: {metrics['opposition_balance']}")
        print(f"Hallucination risk: {metrics['hallucination_risk']}")


if __name__ == "__main__":
    main()
