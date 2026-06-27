export type Stance = "support" | "oppose" | "neutral";

export type VisualNode = {
  id: string;
  label: string;
  type: "brief" | "task" | "evidence";
  stance: Stance;
  confidence: number;
  url?: string;
};

export type VisualLink = {
  source: string;
  target: string;
  type: string;
};

export type Evidence = {
  id: string;
  task_id: string;
  claim: string;
  source_title: string;
  source_url: string;
  quote: string;
  stance: Stance;
  confidence: number;
  topic: string;
};

export type ResearchTask = {
  id: string;
  title: string;
  query: string;
  rationale: string;
};

export type OppositionMatrixRow = {
  topic: string;
  support_claims: string[];
  oppose_claims: string[];
  neutral_claims: string[];
  confidence: number;
};

export type TimelineEvent = {
  step: string;
  title: string;
  description: string;
  status: "complete" | "running" | "pending";
};

export type ResearchResponse = {
  report_id?: string;
  brief: {
    original_query: string;
    objective: string;
    language: string;
    scope: string[];
    deliverables: string[];
    success_criteria: string[];
  };
  plan: ResearchTask[];
  evidence: Evidence[];
  report: {
    title: string;
    markdown: string;
  };
  visual_graph: {
    nodes: VisualNode[];
    links: VisualLink[];
  };
  opposition_matrix: OppositionMatrixRow[];
  timeline: TimelineEvent[];
  exports: {
    markdown: string;
  };
  quality_metrics: {
    citation_coverage: number;
    source_count: number;
    opposition_balance: number;
    hallucination_risk: number;
  };
};

export type ReportSummary = {
  id: string;
  query: string;
  title: string;
  created_at: string;
  source_count: number;
  evidence_count: number;
  quality_score: number;
  hallucination_risk: number;
};

export type ReportDetail = ReportSummary & {
  payload: ResearchResponse;
};
