from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.models import ResearchResult


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = PROJECT_ROOT / "backend" / "data" / "research_history.sqlite3"


class HistoryStore:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path or os.getenv("RESEARCH_HISTORY_DB") or DEFAULT_DB_PATH)

    def save_result(self, result: ResearchResult) -> str:
        payload = _to_payload(result)
        report_id = uuid4().hex
        created_at = datetime.now(timezone.utc).isoformat()
        report = payload["report"]
        evidence = payload.get("evidence", [])
        quality = payload.get("quality_metrics", {})

        with self._connect() as connection:
            self._ensure_schema(connection)
            connection.execute(
                """
                INSERT INTO reports (
                    id, query, title, markdown, payload_json, created_at,
                    source_count, evidence_count, quality_score, hallucination_risk
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    report_id,
                    payload["brief"]["original_query"],
                    report["title"],
                    report["markdown"],
                    json.dumps(payload, ensure_ascii=False),
                    created_at,
                    int(quality.get("source_count", len({item.get("source_url") for item in evidence}))),
                    len(evidence),
                    _quality_score(quality),
                    float(quality.get("hallucination_risk", 0)),
                ),
            )
            for label, item in _evidence_with_labels(evidence):
                connection.execute(
                    """
                    INSERT INTO evidence (
                        report_id, evidence_id, source_label, task_id, topic, stance,
                        confidence, claim, quote, source_title, source_url
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        report_id,
                        item.get("id", ""),
                        label,
                        item.get("task_id", ""),
                        item.get("topic", ""),
                        item.get("stance", "neutral"),
                        float(item.get("confidence", 0)),
                        item.get("claim", ""),
                        item.get("quote", ""),
                        item.get("source_title", ""),
                        item.get("source_url", ""),
                    ),
                )
        return report_id

    def list_reports(self, limit: int = 30) -> list[dict[str, Any]]:
        with self._connect() as connection:
            self._ensure_schema(connection)
            rows = connection.execute(
                """
                SELECT id, query, title, created_at, source_count, evidence_count,
                       quality_score, hallucination_risk
                FROM reports
                ORDER BY datetime(created_at) DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_report(self, report_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            self._ensure_schema(connection)
            row = connection.execute(
                """
                SELECT id, query, title, created_at, source_count, evidence_count,
                       quality_score, hallucination_risk, payload_json
                FROM reports
                WHERE id = ?
                """,
                (report_id,),
            ).fetchone()
        if row is None:
            return None
        data = dict(row)
        payload = json.loads(data.pop("payload_json"))
        data["payload"] = payload
        return data

    def delete_report(self, report_id: str) -> bool:
        with self._connect() as connection:
            self._ensure_schema(connection)
            cursor = connection.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        return cursor.rowcount > 0

    def _connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _ensure_schema(self, connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                title TEXT NOT NULL,
                markdown TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                source_count INTEGER NOT NULL,
                evidence_count INTEGER NOT NULL,
                quality_score INTEGER NOT NULL,
                hallucination_risk REAL NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS evidence (
                report_id TEXT NOT NULL,
                evidence_id TEXT NOT NULL,
                source_label TEXT NOT NULL,
                task_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                stance TEXT NOT NULL,
                confidence REAL NOT NULL,
                claim TEXT NOT NULL,
                quote TEXT NOT NULL,
                source_title TEXT NOT NULL,
                source_url TEXT NOT NULL,
                FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE
            )
            """
        )
        connection.execute("CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_evidence_report_id ON evidence(report_id)")


def get_history_store() -> HistoryStore:
    return HistoryStore()


def _to_payload(result: ResearchResult) -> dict[str, Any]:
    if is_dataclass(result):
        return asdict(result)
    return result


def _quality_score(quality: dict[str, Any]) -> int:
    citation = float(quality.get("citation_coverage", 0))
    balance = float(quality.get("opposition_balance", 0))
    risk = float(quality.get("hallucination_risk", 1))
    return round((citation * 0.5 + balance * 0.3 + (1 - risk) * 0.2) * 100)


def _evidence_with_labels(evidence: list[dict[str, Any]]) -> list[tuple[str, dict[str, Any]]]:
    labels: dict[str, str] = {}
    rows: list[tuple[str, dict[str, Any]]] = []
    for item in evidence:
        source_url = item.get("source_url", "")
        if source_url not in labels:
            labels[source_url] = f"S{len(labels) + 1}"
        rows.append((labels[source_url], item))
    return rows
