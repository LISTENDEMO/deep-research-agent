import type { ResearchResponse } from "./types";

export const sampleResearch: ResearchResponse = {
  brief: {
    original_query: "研究 LangGraph、AutoGen、CrewAI 哪个更适合企业级多 Agent 系统",
    objective: "形成一份可追溯、可比较、可落地的中文深度研究报告。",
    language: "zh",
    scope: ["技术架构", "生态成熟度", "风险限制", "落地建议"],
    deliverables: ["报告", "证据", "观点矩阵"],
    success_criteria: ["每个核心结论有来源", "同时呈现优势与风险"]
  },
  plan: [
    { id: "task-1", title: "技术架构与工作流能力", query: "", rationale: "比较状态管理和多 Agent 编排。" },
    { id: "task-2", title: "生态成熟度与工具集成", query: "", rationale: "比较社区、文档和工具。" },
    { id: "task-3", title: "风险、限制与反方观点", query: "", rationale: "识别学习曲线、成本和稳定性。" }
  ],
  evidence: [
    {
      id: "task-1-e1",
      task_id: "task-1",
      claim: "支持性结论：LangGraph 更适合有状态工作流和可恢复执行。",
      source_title: "LangGraph",
      source_url: "https://github.com/langchain-ai/langgraph",
      quote: "Build resilient language agents as graphs.",
      stance: "support",
      confidence: 0.86,
      topic: "技术架构与工作流能力"
    },
    {
      id: "task-3-e1",
      task_id: "task-3",
      claim: "风险性结论：复杂 Agent 框架存在学习曲线和成本限制。",
      source_title: "Agent risk memo",
      source_url: "https://example.com/agent-risk",
      quote: "企业落地需要关注学习曲线、运行成本和工具调用稳定性。",
      stance: "oppose",
      confidence: 0.74,
      topic: "风险、限制与反方观点"
    }
  ],
  report: {
    title: "# Deep Research 报告",
    markdown: "# Deep Research 报告\n\n## 核心发现\n\n- [支持] LangGraph 更适合有状态工作流。引用：[LangGraph](https://github.com/langchain-ai/langgraph)\n- [反对/风险] 复杂框架存在学习曲线。引用：[Agent risk memo](https://example.com/agent-risk)"
  },
  visual_graph: {
    nodes: [
      { id: "brief", label: "企业级多 Agent 选型", type: "brief", stance: "neutral", confidence: 1 },
      { id: "task-1", label: "架构能力", type: "task", stance: "neutral", confidence: 0.8 },
      { id: "task-3", label: "风险限制", type: "task", stance: "neutral", confidence: 0.8 },
      { id: "task-1-e1", label: "状态图优势", type: "evidence", stance: "support", confidence: 0.86 },
      { id: "task-3-e1", label: "学习曲线", type: "evidence", stance: "oppose", confidence: 0.74 }
    ],
    links: [
      { source: "brief", target: "task-1", type: "decomposes" },
      { source: "brief", target: "task-3", type: "decomposes" },
      { source: "task-1", target: "task-1-e1", type: "supports" },
      { source: "task-3", target: "task-3-e1", type: "supports" }
    ]
  },
  opposition_matrix: [
    {
      topic: "技术架构与工作流能力",
      support_claims: ["支持性结论：LangGraph 更适合有状态工作流和可恢复执行。"],
      oppose_claims: [],
      neutral_claims: [],
      confidence: 0.86
    },
    {
      topic: "风险、限制与反方观点",
      support_claims: [],
      oppose_claims: ["风险性结论：复杂 Agent 框架存在学习曲线和成本限制。"],
      neutral_claims: [],
      confidence: 0.74
    }
  ],
  timeline: [
    {
      step: "scope",
      title: "Scope Agent 生成研究简报",
      description: "将模糊问题转成中文研究目标。",
      status: "complete"
    },
    {
      step: "research",
      title: "Researcher 抽取证据",
      description: "收集支持与风险证据。",
      status: "complete"
    }
  ],
  exports: {
    markdown: "# Deep Research 报告\n\n## 核心发现\n\n- [支持] LangGraph 更适合有状态工作流。引用：[LangGraph](https://github.com/langchain-ai/langgraph)\n- [反对/风险] 复杂框架存在学习曲线。引用：[Agent risk memo](https://example.com/agent-risk)"
  },
  quality_metrics: {
    citation_coverage: 1,
    source_count: 2,
    opposition_balance: 0.5,
    hallucination_risk: 0.18
  }
};
