import { type CSSProperties, useEffect, useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Activity,
  Clock3,
  ExternalLink,
  FileText,
  Gauge,
  History,
  Layers3,
  Play,
  Printer,
  Search,
  ShieldCheck,
  Sparkles,
  Table2,
  Trash2
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { deleteReport, getReport, listReports, streamResearch } from "./api";
import { MouseWake } from "./components/MouseWake";
import { sampleResearch } from "./sampleData";
import type { Evidence, OppositionMatrixRow, ReportSummary, ResearchResponse, Stance, TimelineEvent } from "./types";

const exampleQuery = "研究 LangGraph、AutoGen、CrewAI 哪个更适合企业级多 Agent 系统";

const rotatingQuestions = [
  "RAG 怎么提高召回率？",
  "企业知识库 RAG 如何降低幻觉并保证可追溯？",
  "LangGraph、AutoGen、CrewAI 哪个更适合企业级多 Agent 系统？",
  "AI Agent 如何做可观测性、评估和上线治理？",
  "向量数据库选型：Milvus、Qdrant、pgvector 怎么选？",
  "长上下文和 RAG 应该如何取舍？",
  "Deep Research Agent 应该如何设计评估集？",
  "企业内部知识库如何做权限过滤和引用溯源？"
];

const sections = [
  { id: "research-console", label: "生成研究" },
  { id: "history-board", label: "历史" },
  { id: "report-studio", label: "报告" },
  { id: "evidence-board", label: "证据" },
  { id: "opposition-matrix", label: "矩阵" },
  { id: "research-timeline", label: "流程" }
];

export function App() {
  const [query, setQuery] = useState(exampleQuery);
  const [research, setResearch] = useState<ResearchResponse>(sampleResearch);
  const [isRunning, setIsRunning] = useState(false);
  const [streamSteps, setStreamSteps] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [questionOffset, setQuestionOffset] = useState(0);
  const [reports, setReports] = useState<ReportSummary[]>([]);
  const [activeReportId, setActiveReportId] = useState<string | null>(sampleResearch.report_id ?? null);
  const [historyError, setHistoryError] = useState<string | null>(null);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setQuestionOffset((offset) => (offset + 1) % rotatingQuestions.length);
    }, 5200);
    return () => window.clearInterval(timer);
  }, []);

  const visibleQuestions = useMemo(
    () => Array.from({ length: 4 }, (_, index) => rotatingQuestions[(questionOffset + index) % rotatingQuestions.length]),
    [questionOffset],
  );

  useEffect(() => {
    void refreshHistory();
  }, []);

  async function refreshHistory() {
    try {
      setHistoryError(null);
      setReports(await listReports());
    } catch (reason) {
      setHistoryError(reason instanceof Error ? reason.message : "历史记录加载失败");
    }
  }

  async function handleRun(nextQuery = query) {
    const researchQuery = nextQuery.trim();
    if (!researchQuery) {
      setError("请输入一个研究问题");
      return;
    }
    setQuery(researchQuery);
    setIsRunning(true);
    setError(null);
    setStreamSteps([]);
    try {
      const result = await streamResearch(researchQuery, false, (event) => {
        if (event.event === "step") {
          setStreamSteps((steps) => [...steps, event.message]);
        }
      });
      setResearch(result);
      setActiveReportId(result.report_id ?? null);
      void refreshHistory();
      window.setTimeout(() => document.getElementById("report-studio")?.scrollIntoView({ behavior: "smooth" }), 120);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "研究任务失败");
    } finally {
      setIsRunning(false);
    }
  }

  async function handleLoadReport(reportId: string) {
    try {
      setError(null);
      setHistoryError(null);
      const detail = await getReport(reportId);
      setResearch(detail.payload);
      setQuery(detail.payload.brief.original_query);
      setActiveReportId(reportId);
      window.setTimeout(() => document.getElementById("report-studio")?.scrollIntoView({ behavior: "smooth" }), 120);
    } catch (reason) {
      setHistoryError(reason instanceof Error ? reason.message : "历史报告加载失败");
    }
  }

  async function handleDeleteReport(reportId: string) {
    try {
      setHistoryError(null);
      await deleteReport(reportId);
      if (activeReportId === reportId) {
        setActiveReportId(null);
      }
      await refreshHistory();
    } catch (reason) {
      setHistoryError(reason instanceof Error ? reason.message : "历史报告删除失败");
    }
  }

  const evidenceStats = useMemo(() => summarizeEvidence(research.evidence), [research.evidence]);
  const qualityMetrics = research.quality_metrics ?? {
    citation_coverage: 0,
    source_count: 0,
    opposition_balance: 0,
    hallucination_risk: 1
  };
  const progress = Math.round(
    (qualityMetrics.citation_coverage * 0.5 + qualityMetrics.opposition_balance * 0.3 + (1 - qualityMetrics.hallucination_risk) * 0.2) * 100
  );

  return (
    <main className="app-shell">
      <MouseWake />
      <div className="product-surface">
        <header className="top-command">
          <div className="brand-block">
            <span className="brand-mark">DR</span>
            <div>
              <p className="eyebrow">Deep Research Agent</p>
              <h1>Research Studio</h1>
            </div>
          </div>
          <ScrollNavigator />
        </header>

        <section className="research-hero scroll-section" id="research-console">
          <div className="query-card">
            <div className="input-shell">
              <Search size={18} />
              <textarea value={query} onChange={(event) => setQuery(event.target.value)} aria-label="研究问题" />
            </div>
            <div className="question-strip" aria-label="推荐研究问题">
              {visibleQuestions.map((question) => (
                <button
                  className="question-suggestion"
                  type="button"
                  key={question}
                  onClick={() => void handleRun(question)}
                  disabled={isRunning}
                >
                  {question}
                </button>
              ))}
            </div>
            <div className="query-footer">
              <span className="live-status">Live Tavily search</span>
              <button className="primary-button" type="button" onClick={() => void handleRun()} disabled={isRunning}>
                <Play size={16} />
                {isRunning ? "研究中..." : "Run research"}
              </button>
            </div>
            {error ? <p className="error-text">{error}</p> : null}
          </div>

          <aside className="status-stack">
            <QualityPanel progress={progress} metrics={qualityMetrics} evidenceStats={evidenceStats} />
            <RunStream steps={streamSteps} isRunning={isRunning} />
          </aside>
        </section>

        <HistoryPanel
          reports={reports}
          activeReportId={activeReportId}
          error={historyError}
          onLoadReport={(reportId) => void handleLoadReport(reportId)}
          onDeleteReport={(reportId) => void handleDeleteReport(reportId)}
        />

        <section className="ops-board">
          <MiniPlan research={research} />
          <BriefPanel research={research} />
        </section>

        <section className="content-grid">
          <ReportPanel title={research.report.title} markdown={research.report.markdown} evidence={research.evidence} />
          <EvidenceBoard evidence={research.evidence} />
          <MatrixPanel rows={research.opposition_matrix} />
          <TimelinePanel events={research.timeline} />
        </section>
      </div>
    </main>
  );
}

function HistoryPanel({
  reports,
  activeReportId,
  error,
  onLoadReport,
  onDeleteReport
}: {
  reports: ReportSummary[];
  activeReportId: string | null;
  error: string | null;
  onLoadReport: (reportId: string) => void;
  onDeleteReport: (reportId: string) => void;
}) {
  const [historyQuery, setHistoryQuery] = useState("");
  const filteredReports = useMemo(() => {
    const keyword = historyQuery.trim().toLowerCase();
    if (!keyword) return reports;
    return reports.filter((report) => {
      const text = `${report.query} ${report.title}`.toLowerCase();
      return text.includes(keyword);
    });
  }, [historyQuery, reports]);

  return (
    <section className="history-panel scroll-section" id="history-board">
      <div className="panel-toolbar">
        <PanelTitle icon={History} title="Research History" />
        <span>{filteredReports.length}/{reports.length} saved</span>
      </div>
      <div className="history-tools">
        <label className="history-search">
          <Search size={15} />
          <input
            type="search"
            value={historyQuery}
            onChange={(event) => setHistoryQuery(event.target.value)}
            placeholder="搜索历史问题"
            aria-label="搜索历史问题"
          />
        </label>
        <span className="history-hint">点击记录恢复报告和证据链</span>
      </div>
      {error ? <p className="error-text">{error}</p> : null}
      {reports.length === 0 ? (
        <p className="history-empty">暂无历史。运行一次研究后，报告、证据和时间线会自动保存到本地 SQLite。</p>
      ) : filteredReports.length === 0 ? (
        <p className="history-empty">没有匹配的历史记录。</p>
      ) : (
        <div className="history-list">
          {filteredReports.map((report) => (
            <article className={report.id === activeReportId ? "history-item active" : "history-item"} key={report.id}>
              <button className="history-load" type="button" onClick={() => onLoadReport(report.id)}>
                <span>{formatReportTime(report.created_at)}</span>
                <strong>{report.query}</strong>
                <small>
                  {report.source_count} sources · {report.evidence_count} evidence · {report.quality_score}% quality
                </small>
              </button>
              <button
                className="history-delete"
                type="button"
                aria-label={`删除历史报告：${report.query}`}
                onClick={() => onDeleteReport(report.id)}
              >
                <Trash2 size={15} />
              </button>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

function ScrollNavigator() {
  const [activeId, setActiveId] = useState(sections[0].id);

  useEffect(() => {
    function updateActiveSection() {
      const current = sections
        .map((section) => {
          const element = document.getElementById(section.id);
          const top = element ? Math.abs(element.getBoundingClientRect().top - 100) : Number.MAX_SAFE_INTEGER;
          return { id: section.id, top };
        })
        .sort((a, b) => a.top - b.top)[0];
      if (current) setActiveId(current.id);
    }
    updateActiveSection();
    window.addEventListener("scroll", updateActiveSection, { passive: true });
    window.addEventListener("resize", updateActiveSection);
    return () => {
      window.removeEventListener("scroll", updateActiveSection);
      window.removeEventListener("resize", updateActiveSection);
    };
  }, []);

  return (
    <nav className="section-tabs" aria-label="页面目录">
      {sections.map((section) => (
        <a className={section.id === activeId ? "active" : ""} href={`#${section.id}`} key={section.id}>
          {section.label}
        </a>
      ))}
    </nav>
  );
}

function PanelTitle({ icon: Icon, title }: { icon: LucideIcon; title: string }) {
  return (
    <div className="panel-title">
      <Icon size={18} />
      <span>{title}</span>
    </div>
  );
}

function QualityPanel({
  progress,
  metrics,
  evidenceStats
}: {
  progress: number;
  metrics: ResearchResponse["quality_metrics"];
  evidenceStats: Record<Stance, number>;
}) {
  const risk = Math.round(metrics.hallucination_risk * 100);
  return (
    <section className="quality-panel">
      <PanelTitle icon={Gauge} title="质量概览" />
      <div className="score-ring" style={{ "--score": `${Math.round(metrics.citation_coverage * 100)}%` } as CSSProperties}>
        <strong>{progress}%</strong>
        <span>report readiness</span>
      </div>
      <div className="metric-list">
        <Metric label="Sources" value={String(metrics.source_count)} tone="neutral" />
        <Metric label="Evidence" value={String(evidenceStats.support + evidenceStats.oppose + evidenceStats.neutral)} tone="support" />
        <Metric label="Risk" value={`${risk}%`} tone={risk > 45 ? "oppose" : "support"} />
      </div>
    </section>
  );
}

function Metric({ label, value, tone }: { label: string; value: string; tone: Stance }) {
  return (
    <div className={`metric ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function RunStream({ steps, isRunning }: { steps: string[]; isRunning: boolean }) {
  const visibleSteps = steps.length > 0 ? steps : ["等待研究任务", "Scope Agent", "Researcher", "Writer"];
  return (
    <section className="stream-panel">
      <PanelTitle icon={Activity} title="运行流程" />
      <div className={isRunning ? "pulse-line active" : "pulse-line"} />
      <div className="stream-list">
        {visibleSteps.slice(-5).map((step, index) => (
          <span key={`${step}-${index}`}>{step}</span>
        ))}
      </div>
    </section>
  );
}

function MiniPlan({ research }: { research: ResearchResponse }) {
  return (
    <section className="plan-panel">
      <PanelTitle icon={Layers3} title="Research Plan" />
      {research.plan.slice(0, 4).map((task) => (
        <article key={task.id}>
          <strong>{task.title}</strong>
          <p>{task.rationale}</p>
        </article>
      ))}
    </section>
  );
}

function BriefPanel({ research }: { research: ResearchResponse }) {
  return (
    <section className="brief-panel">
      <PanelTitle icon={Sparkles} title="Deliverables" />
      <div className="brief-grid">
        {research.brief.deliverables.map((item) => (
          <span key={item}>{item}</span>
        ))}
      </div>
      <div className="criteria-list">
        {research.brief.success_criteria.map((item) => (
          <p key={item}>{item}</p>
        ))}
      </div>
    </section>
  );
}

function EvidenceBoard({ evidence }: { evidence: Evidence[] }) {
  const sourceLabels = useMemo(() => buildSourceLabels(evidence), [evidence]);
  const renderedSourceAnchors = new Set<string>();
  return (
    <section className="evidence-board scroll-section" id="evidence-board">
      <div className="panel-toolbar">
        <PanelTitle icon={ShieldCheck} title="Evidence Board" />
        <span>{evidence.length} items</span>
      </div>
      <div className="evidence-list">
        {evidence.map((item) => {
          const label = sourceLabels[item.source_url];
          const anchorId = label && !renderedSourceAnchors.has(label) ? `evidence-${label}` : undefined;
          if (label) renderedSourceAnchors.add(label);
          return (
          <article className={`evidence-card ${item.stance}`} id={anchorId} data-source-label={label} key={item.id}>
            <div className="evidence-meta">
              <span>{label ? `${label} · ${labelForStance(item.stance)}` : labelForStance(item.stance)}</span>
              <span>{Math.round(item.confidence * 100)}%</span>
            </div>
            <h3>{item.claim}</h3>
            <p>{item.quote}</p>
            <a href={item.source_url} target="_blank" rel="noreferrer">
              {item.source_title}
            </a>
          </article>
          );
        })}
      </div>
    </section>
  );
}

function ReportPanel({ title, markdown, evidence }: { title: string; markdown: string; evidence: Evidence[] }) {
  const markdownWithCitationLinks = useMemo(() => linkCitations(markdown, evidence), [markdown, evidence]);

  function handleOpenReportPage() {
    const reportWindow = window.open("", "_blank");
    if (!reportWindow) return;
    reportWindow.document.write(buildReportPage(title, markdown));
    reportWindow.document.close();
  }

  return (
    <section className="report-panel scroll-section" id="report-studio">
      <div className="panel-toolbar">
        <PanelTitle icon={FileText} title="Report Studio" />
        <div className="toolbar-actions">
          <button className="ghost-button compact" type="button" onClick={handleOpenReportPage}>
            <ExternalLink size={15} />
            新页面
          </button>
          <button className="ghost-button compact" type="button" onClick={() => window.print()}>
            <Printer size={15} />
            PDF
          </button>
        </div>
      </div>
      <div className="report-meta">
        <span>中文报告</span>
        <strong>{title.replace(/^#+\s*/, "")}</strong>
      </div>
      <article className="markdown-report">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            a: ({ href, children, ...props }) => {
              if (href?.startsWith("#evidence-")) {
                return (
                  <a
                    className="citation-link"
                    href={href}
                    onClick={(event) => {
                      event.preventDefault();
                      focusEvidence(href.slice(1));
                    }}
                    {...props}
                  >
                    {children}
                  </a>
                );
              }
              return (
                <a href={href} target="_blank" rel="noreferrer" {...props}>
                  {children}
                </a>
              );
            }
          }}
        >
          {markdownWithCitationLinks}
        </ReactMarkdown>
      </article>
    </section>
  );
}

function MatrixPanel({ rows }: { rows: OppositionMatrixRow[] }) {
  return (
    <section className="matrix-panel scroll-section" id="opposition-matrix">
      <div className="panel-toolbar">
        <PanelTitle icon={Table2} title="Opposition Matrix" />
        <span>{rows.length} topics</span>
      </div>
      <div className="matrix-list">
        {rows.map((row) => (
          <article className="matrix-row" key={row.topic}>
            <div className="matrix-title">
              <strong>{row.topic}</strong>
              <span>{Math.round(row.confidence * 100)}%</span>
            </div>
            <div className="matrix-columns">
              <MatrixColumn title="支持" items={row.support_claims} tone="support" />
              <MatrixColumn title="风险" items={row.oppose_claims} tone="oppose" />
              <MatrixColumn title="中立" items={row.neutral_claims} tone="neutral" />
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function MatrixColumn({ title, items, tone }: { title: string; items: string[]; tone: Stance }) {
  return (
    <div className={`matrix-column ${tone}`}>
      <span>{title}</span>
      {items.length === 0
        ? <p>暂无</p>
        : items.slice(0, 3).map((item, index) => <p key={`${tone}-${index}-${item.slice(0, 16)}`}>{item}</p>)}
    </div>
  );
}

function TimelinePanel({ events }: { events: TimelineEvent[] }) {
  return (
    <section className="timeline-panel scroll-section" id="research-timeline">
      <div className="panel-toolbar">
        <PanelTitle icon={Clock3} title="Agent Timeline" />
        <span>{events.length} steps</span>
      </div>
      <div className="timeline-list">
        {events.map((event, index) => (
          <article className={`timeline-item ${event.status}`} key={event.step}>
            <span>{String(index + 1).padStart(2, "0")}</span>
            <div>
              <strong>{event.title}</strong>
              <p>{event.description}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function summarizeEvidence(evidence: Evidence[]) {
  return evidence.reduce(
    (stats, item) => {
      stats[item.stance] += 1;
      return stats;
    },
    { support: 0, oppose: 0, neutral: 0 } as Record<Stance, number>,
  );
}

function formatReportTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  }).format(date);
}

function buildSourceLabels(evidence: Evidence[]) {
  const labels: Record<string, string> = {};
  for (const item of evidence) {
    if (!labels[item.source_url]) {
      labels[item.source_url] = `S${Object.keys(labels).length + 1}`;
    }
  }
  return labels;
}

function linkCitations(markdown: string, evidence: Evidence[]) {
  const sourceLabels = buildSourceLabels(evidence);
  const validLabels = new Set(Object.values(sourceLabels));
  return markdown.replace(/\[(S\d+)\]/g, (match, label: string) => {
    if (!validLabels.has(label)) return match;
    return `[${label}](#evidence-${label})`;
  });
}

function focusEvidence(id: string) {
  const element = document.getElementById(id);
  if (!element) return;
  element.scrollIntoView({ behavior: "smooth", block: "center" });
  element.classList.remove("flash");
  window.setTimeout(() => element.classList.add("flash"), 20);
}

function labelForStance(stance: Stance) {
  return {
    support: "支持证据",
    oppose: "风险证据",
    neutral: "中立证据"
  }[stance];
}

function buildReportPage(title: string, markdown: string) {
  const cleanTitle = title.replace(/^#+\s*/, "");
  return `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" /><title>${escapeHtml(cleanTitle)}</title><style>
body{margin:0;background:#f7f5ef;color:#17130f;font-family:"Aptos","Microsoft YaHei",sans-serif}main{width:min(920px,calc(100vw - 40px));margin:36px auto;background:#fffdf8;border:1px solid #dedbd2;border-radius:10px;padding:38px;box-shadow:0 24px 70px rgba(26,22,15,.09)}h1,h2,h3{font-family:Georgia,"Times New Roman","Microsoft YaHei",serif;line-height:1.15}h1{font-size:40px;margin:0 0 22px}h2{margin-top:34px;padding-top:18px;border-top:1px solid #ece6dc;font-size:26px}h3{margin-top:24px;font-size:20px}p,li{line-height:1.82;color:#39342d}table{width:100%;border-collapse:collapse;margin:20px 0}th,td{border:1px solid #dfd8cc;padding:10px 12px;text-align:left;vertical-align:top}a{color:#7f16bf;font-weight:800}.actions{position:sticky;top:0;display:flex;justify-content:flex-end;margin:-38px -38px 28px;padding:12px;background:rgba(255,253,248,.86);backdrop-filter:blur(12px);border-bottom:1px solid #dedbd2}button{border:1px solid #dedbd2;border-radius:8px;padding:9px 13px;background:#fff;font-weight:800;cursor:pointer}@media print{body{background:#fff}main{width:auto;margin:0;border:0;box-shadow:none;padding:0}.actions{display:none}}</style></head><body><main><div class="actions"><button onclick="window.print()">导出 PDF</button></div>${markdownToHtml(markdown)}</main></body></html>`;
}

function markdownToHtml(markdown: string) {
  const lines = markdown.split("\n");
  const html: string[] = [];
  let inList = false;
  let inTable = false;
  const closeList = () => {
    if (inList) {
      html.push("</ul>");
      inList = false;
    }
  };
  const closeTable = () => {
    if (inTable) {
      html.push("</tbody></table>");
      inTable = false;
    }
  };
  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) {
      closeList();
      closeTable();
      continue;
    }
    if (line.startsWith("|") && line.endsWith("|")) {
      closeList();
      const cells = line.split("|").slice(1, -1).map((cell) => inlineMarkdown(cell.trim()));
      if (cells.every((cell) => /^-+$/.test(cell.replace(/<[^>]*>/g, "")))) continue;
      if (!inTable) {
        html.push("<table><tbody>");
        inTable = true;
      }
      html.push(`<tr>${cells.map((cell) => `<td>${cell}</td>`).join("")}</tr>`);
      continue;
    }
    closeTable();
    if (line.startsWith("### ")) {
      closeList();
      html.push(`<h3>${inlineMarkdown(line.slice(4))}</h3>`);
    } else if (line.startsWith("## ")) {
      closeList();
      html.push(`<h2>${inlineMarkdown(line.slice(3))}</h2>`);
    } else if (line.startsWith("# ")) {
      closeList();
      html.push(`<h1>${inlineMarkdown(line.slice(2))}</h1>`);
    } else if (line.startsWith("- ")) {
      if (!inList) {
        html.push("<ul>");
        inList = true;
      }
      html.push(`<li>${inlineMarkdown(line.slice(2))}</li>`);
    } else {
      closeList();
      html.push(`<p>${inlineMarkdown(line)}</p>`);
    }
  }
  closeList();
  closeTable();
  return html.join("\n");
}

function inlineMarkdown(value: string) {
  return escapeHtml(value)
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>');
}

function escapeHtml(value: string) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
