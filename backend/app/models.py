from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


Stance = Literal["support", "oppose", "neutral"]


@dataclass(slots=True)
class ResearchBrief:
    original_query: str
    objective: str
    language: str = "zh"
    scope: list[str] = field(default_factory=list)
    deliverables: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ResearchTask:
    id: str
    title: str
    query: str
    rationale: str


@dataclass(slots=True)
class SearchResult:
    title: str
    url: str
    content: str


@dataclass(slots=True)
class Evidence:
    id: str
    task_id: str
    claim: str
    source_title: str
    source_url: str
    quote: str
    stance: Stance
    confidence: float
    topic: str


@dataclass(slots=True)
class OppositionMatrixRow:
    topic: str
    support_claims: list[str]
    oppose_claims: list[str]
    neutral_claims: list[str]
    confidence: float


@dataclass(slots=True)
class TimelineEvent:
    step: str
    title: str
    description: str
    status: Literal["complete", "running", "pending"] = "complete"


@dataclass(slots=True)
class ResearchReport:
    title: str
    markdown: str


@dataclass(slots=True)
class ResearchResult:
    brief: ResearchBrief
    plan: list[ResearchTask]
    evidence: list[Evidence]
    report: ResearchReport
    visual_graph: dict
    opposition_matrix: list[OppositionMatrixRow]
    timeline: list[TimelineEvent]
    exports: dict[str, str]
    quality_metrics: dict[str, float | int]
