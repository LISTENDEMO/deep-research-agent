# Deep Research Agent

中文优先的 Deep Research Agent，面向复杂研究任务，强调可解释、多 Agent 协作、证据追溯、观点对立矩阵和高质量报告生成。

## 系统架构

### LangGraph 工作流编排

```mermaid
graph TB
    A[用户输入研究问题] --> B[Scope Agent]
    
    B --> C[生成 Research Brief<br/>研究简报]
    C --> D[Supervisor/Planner Agent]
    
    D --> E[拆解子研究任务]
    E --> F1[Researcher Agent A]
    E --> F2[Researcher Agent B]
    E --> F3[Researcher Agent C]
    
    F1 --> G[Tavily Search Tool<br/>实时搜索]
    F2 --> G
    F3 --> G
    
    G --> H[提取证据 Extract Evidence]
    H --> I[Evidence Store<br/>证据存储]
    
    I --> J[Verifier Agent]
    J --> K[构建观点对立矩阵<br/>Opposition Matrix]
    J --> L[生成时间线 Timeline]
    J --> M[质量评估 Quality Metrics]
    
    K --> N[Writer Agent]
    L --> N
    M --> N
    
    N --> O[生成 Markdown 报告<br/>带引用和置信度]
    O --> P[Visualizer Agent]
    
    P --> Q[生成可视化数据<br/>星图/矩阵/证据卡片]
    Q --> R[前端 Research Studio]
    
    R --> S[研究报告展示]
    R --> T[证据卡片板 Evidence Board]
    R --> U[观点矩阵 Opposition Matrix]
    R --> V[执行时间线 Timeline]
    
    style B fill:#4A90E2,color:#fff
    style D fill:#FFA500,color:#fff
    style F1 fill:#7B68EE,color:#fff
    style F2 fill:#7B68EE,color:#fff
    style F3 fill:#7B68EE,color:#fff
    style J fill:#FF6B6B,color:#fff
    style N fill:#50C878,color:#fff
    style I fill:#00CED1,color:#fff
    style G fill:#FFD700,color:#fff
```

### 多 Agent 协作流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant S as Scope Agent
    participant P as Supervisor
    participant R as Researcher Agents
    participant E as Evidence Store
    participant V as Verifier
    participant W as Writer
    participant F as Frontend
    
    U->>S: 输入研究问题
    S->>S: 生成 Research Brief<br/>明确目标和范围
    S->>P: 提交研究简报
    
    P->>P: 拆解子任务<br/>技术/生态/成本/风险
    P->>R: 分配并行任务
    
    par 并行研究
        R->>R: Task A - 技术架构
        R->>E: 存储证据
    and
        R->>R: Task B - 生态社区
        R->>E: 存储证据
    and
        R->>R: Task C - 成本部署
        R->>E: 存储证据
    end
    
    E->>V: 提交所有证据
    V->>V: 构建观点对立矩阵<br/>评估质量指标
    V->>W: 提交验证结果
    
    W->>W: 生成带引用报告<br/>支持/反对/置信度
    W->>F: 输出最终报告
    
    F->>U: 展示报告+证据+矩阵
```

### Evidence Store 数据模型

```mermaid
graph LR
    A[Evidence Store<br/>证据存储中心] --> B[Claim 声明]
    A --> C[Source 来源]
    A --> D[Quote 原文引用]
    A --> E[Stance 观点立场]
    A --> F[Confidence 置信度]
    A --> G[Topic 主题分类]
    
    B --> H[结论或主张]
    C --> I[标题 + URL]
    D --> J[原文摘录片段]
    E --> K[支持/反对/中立]
    F --> L[可信度评分 0-1]
    G --> M[研究主题标签]
    
    style A fill:#00CED1,color:#fff
    style E fill:#FF6B6B,color:#fff
    style F fill:#FFA500,color:#fff
```

**Evidence 数据结构**：
```json
{
  "id": "evidence-001",
  "task_id": "task-architecture",
  "claim": "LangGraph 支持状态图和检查点恢复",
  "source_title": "LangGraph Official Documentation",
  "source_url": "https://github.com/langchain-ai/langgraph",
  "quote": "Build resilient agents with stateful workflows",
  "stance": "support",
  "confidence": 0.84,
  "topic": "architecture"
}
```

### 观点对立矩阵

```mermaid
graph TB
    A[观点对立矩阵<br/>Opposition Matrix] --> B[主题 Topic]
    A --> C[支持证据<br/>Support Claims]
    A --> D[反对证据<br/>Oppose Claims]
    A --> E[中立证据<br/>Neutral Claims]
    A --> F[综合置信度<br/>Confidence]
    
    B --> G[技术架构]
    B --> H[生态成熟度]
    B --> I[成本效益]
    B --> J[风险评估]
    
    C --> K[证据1: 状态图支持]
    C --> L[证据2: Checkpoint 可恢复]
    
    D --> M[证据A: 学习曲线陡峭]
    D --> N[证据B: 文档不够完善]
    
    E --> O[中性观察: 社区活跃度中等]
    
    F --> P[综合评分: 0.72 高置信度]
    
    style A fill:#FF6B6B,color:#fff
    style C fill:#50C878,color:#fff
    style D fill:#FFD700,color:#fff
    style E fill:#87CEEB,color:#fff
```

**矩阵示例**：
| 主题 | 支持证据 | 反对证据 | 置信度 |
|------|---------|---------|--------|
| LangGraph 适合复杂工作流 | 状态图、checkpoint、human-in-loop | 学习曲线更高 | 高 (0.72) |
| AutoGen 社区活跃 | Microsoft 支持、多 Agent 协作 | API 变化频繁 | 中 (0.65) |
| CrewAI 易于上手 | 简洁 API、角色定义清晰 | 企业级能力待验证 | 中 (0.58) |

### 前端 Research Studio 架构

```mermaid
graph TB
    A[Research Studio<br/>前端工作台] --> B[研究问题输入区]
    A --> C[经典问题轮换入口]
    A --> D[报告质量概览]
    
    D --> E[证据数量]
    D --> F[引用覆盖率]
    D --> G[来源数量]
    D --> H[观点平衡度]
    D --> I[幻觉风险评分]
    
    B --> J[执行流程展示]
    J --> K[任务拆解列表]
    J --> L[Agent 状态流]
    J --> M[执行时间线]
    
    J --> N[Evidence Board<br/>证据卡片板]
    N --> O[证据卡片]
    N --> P[来源域名]
    N --> Q[观点标签<br/>支持/反对/中立]
    N --> R[置信度评分]
    
    J --> S[观点矩阵可视化]
    S --> T[支持证据集合]
    S --> U[反对证据集合]
    S --> V[中立观点集合]
    
    J --> W[Report Preview<br/>报告预览]
    W --> X[Markdown 报告]
    W --> Y[引用 Hover 预览]
    W --> Z[PDF 导出功能]
    
    style A fill:#61DAFB,color:#fff
    style N fill:#00CED1,color:#fff
    style S fill:#FF6B6B,color:#fff
    style W fill:#50C878,color:#fff
```

### 核心组件说明

#### 🔍 Scope Agent（范围定义）
**职责**：澄清用户模糊问题，生成研究简报

**输出**：
- 研究背景
- 明确目标
- 研究范围（包含项/排除项）
- 交付格式
- 成功标准

**示例**：
```
输入: "研究 LangGraph 和 AutoGen 哪个更好"

输出: 
Research Brief {
  objective: "对比 LangGraph、AutoGen、CrewAI 在企业级多 Agent 系统中的适用性",
  scope: ["技术架构", "生态成熟度", "成本部署", "风险限制"],
  deliverables: ["选型报告", "评分矩阵", "风险分析"],
  success_criteria: ["至少 10 个引用来源", "包含反对观点"]
}
```

#### 📋 Supervisor（任务拆解）
**职责**：将研究问题拆解为可并行子任务

**拆解策略**：
- 按主题维度拆分（技术/生态/成本/风险）
- 按对比对象拆分（LangGraph/AutoGen/CrewAI）
- 按时间维度拆分（现状/趋势/历史）

**输出**：3-5 个并行 ResearchTask

#### 🔬 Researcher Agent（证据收集）
**职责**：执行搜索并提取结构化证据

**能力**：
- Tavily Live Search 实时搜索
- Mock Search 离线测试
- Evidence Extraction 证据抽取
- Stance Classification 观点分类
- Confidence Scoring 置信度评估

**工具权限**：
- `search(query, max_results=3)`
- `extract_evidence(task, search_results)`
- `classify_stance(claim, context)`
- `calculate_confidence(source, quote)`

#### ✅ Verifier Agent（质量验证）
**职责**：检查证据完整性、观点对立和引用质量

**能力**：
- Opposition Matrix 构建（支持/反对/中立）
- Timeline 生成（研究步骤时间线）
- Quality Metrics 计算：
  - Evidence Count（证据数量）
  - Citation Coverage（引用覆盖率）
  - Source Diversity（来源多样性）
  - Stance Balance（观点平衡度）
  - Hallucination Risk（幻觉风险）

#### 📝 Writer Agent（报告生成）
**职责**：生成带引用、带置信度的 Markdown 报告

**输出结构**：
```markdown
# 研究报告标题

## 直接答案
简明结论 [引用1]

## 执行方案
分步骤建议 [引用2, 引用3]

## 指标验收
量化验收标准 [引用4]

## 落地计划
实施时间表 [引用5]

## 证据引用
[1] Source A - 证据原文
[2] Source B - 证据原文
```

#### 🎨 Visualizer Agent（可视化生成）
**职责**：生成前端展示所需的 JSON 数据

**输出**：
- Visual Graph（星图/知识图谱）
- Evidence Cards（证据卡片列表）
- Opposition Matrix（观点矩阵）
- Timeline（时间线数据）

### LangGraph 状态流转

```mermaid
stateDiagram-v2
    [*] --> Scope
    Scope --> Plan: Research Brief<br/>生成完成
    Plan --> Research: 子任务拆解完成
    Research --> Verify: 证据收集完成
    Verify --> Write: 质量验证通过
    Write --> Visualize: 报告生成完成
    Visualize --> [*]: 可视化数据就绪
    
    note right of Scope
        输出: ResearchBrief
        - objective
        - scope
        - deliverables
    end note
    
    note right of Plan
        输出: list[ResearchTask]
        - task_id
        - query
        - rationale
    end note
    
    note right of Research
        输出: list[Evidence]
        - claim
        - source_url
        - stance
        - confidence
    end note
    
    note right of Verify
        输出: OppositionMatrix
        + Timeline
        + QualityMetrics
    end note
    
    note right of Write
        输出: ResearchReport
        - markdown
        - exports
    end note
    
    note right of Visualize
        输出: VisualGraph
        - nodes
        - edges
        - layout
    end note
```

### 质量评估指标体系

```mermaid
graph LR
    A[质量评估<br/>Quality Metrics] --> B[证据完整性<br/>Evidence Count]
    A --> C[引用覆盖率<br/>Citation Coverage]
    A --> D[来源多样性<br/>Source Diversity]
    A --> E[观点平衡度<br/>Stance Balance]
    A --> F[幻觉风险<br/>Hallucination Risk]
    
    B --> G[≥ 10 条证据<br/>合格标准]
    C --> H[≥ 80% 覆盖率<br/>合格标准]
    D --> I[≥ 5 个来源<br/>合格标准]
    E --> J[支持/反对比例<br/>接近 1:1]
    F --> K[≤ 0.3 风险<br/>低风险标准]
    
    style A fill:#FF6B6B,color:#fff
    style B fill:#50C878,color:#fff
    style C fill:#FFA500,color:#fff
    style D fill:#00CED1,color:#fff
    style E fill:#FFD700,color:#fff
    style F fill:#87CEEB,color:#fff
```

**评估脚本输出示例**：
```powershell
python scripts/evaluate_demo.py

输出:
- 证据数量: 28 条
- 引用覆盖率: 92%
- 来源数量: 12 个独立来源
- 观点平衡度: 支持 14 条 / 反对 8 条 / 中立 6 条
- 幻觉风险评分: 0.18 (低风险)
```

This project imports `medical.json` into Neo4j as a medical knowledge graph.

## 当前能力

- LangGraph：用 `StateGraph` 编排 Scope -> Plan -> Research -> Verify -> Write -> Visualize
- Scope Agent：把用户问题转成中文 research brief
- Supervisor：拆解子研究任务
- Researcher：调用 Tavily live search 并抽取证据，保留 mock search 供测试和离线开发
- Evidence Store：保留 claim、source、quote、stance、confidence
- Verifier：生成观点对立矩阵和质量指标
- Writer：生成带引用的中文 Markdown 报告，并输出直接答案、执行方案、指标验收和落地计划
- LLM adapter：支持 OpenAI-compatible 模型，未配置时规则兜底
- FastAPI：提供 `/api/research`、`/api/research/events`、`/api/export/markdown`
- React：研究生成器、经典问题轮换入口、证据板、观点矩阵、时间线、Report Studio、新页面报告预览和 PDF 导出

## 运行后端

```powershell
python -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

## 运行前端

```powershell
cd frontend
npm install
npm run dev
```

打开：

```text
http://127.0.0.1:5173
```

## 环境变量

复制 `.env.example` 为 `.env`，填入自己的 key。

```powershell
Copy-Item .env.example .env
```

当前前端默认使用 Live Tavily search，因此演示真实研究前需要配置 `TAVILY_API_KEY`。后端仍保留 `use_mock_search` 参数，主要用于自动化测试和离线开发。

如果配置 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`MODEL_NAME`，Writer 会尝试使用 OpenAI-compatible 模型；未配置时使用规则化中文兜底，保证演示链路可运行。

配置或修改 `.env` 后需要重启后端服务，否则当前运行中的进程读不到新的环境变量。

真实搜索最小配置：

```env
TAVILY_API_KEY=your_tavily_api_key
```

如果真实模式提示 `TAVILY_API_KEY is required for live Tavily search.`，说明后端进程没有读到 key。检查 `.env` 是否位于项目根目录，并重启：

```powershell
python -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

## 测试

```powershell
python -m pytest backend/tests
cd frontend
npm run build
```

## 评估 Demo

```powershell
python scripts/evaluate_demo.py
```

该脚本会跑 `examples/demo_tasks.json` 中的中文研究任务，并输出：

- 证据数量
- 引用覆盖率
- 来源数量
- 观点平衡度
- 幻觉风险评分

## 面试材料

- 设计文档：`docs/deep-research-agent-design.md`
- 面试讲解稿：`docs/interview-script.md`
- 项目现状报告：`docs/project-status-report.md`
- 演示任务：`examples/demo_tasks.json`

## Open Deep Research 复用策略

本项目选择 A + 少量 B：

- 原创实现核心数据模型、Evidence Store、Verifier、Research Studio 前端
- 借鉴 Open Deep Research 的 Scope / Research / Write 分阶段思想
- 后续如引入 Open Deep Research 代码，需要保留 MIT License 和来源说明
