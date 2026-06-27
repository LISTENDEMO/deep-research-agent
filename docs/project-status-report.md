# Deep Research Agent 项目现状报告

## 当前已经完成的内容

本项目已经从“旅行 Agent”方向调整为更适合面试展示的 Deep Research Agent。当前版本具备一条完整研究链路：用户输入中文研究问题后，后端通过 LangGraph 编排 Scope、Supervisor、Researcher、Verifier、Writer 等阶段，生成研究简报、拆解任务、调用 Tavily live search 收集证据，最后输出带引用的中文 Markdown 报告。

后端已完成的核心能力：

- FastAPI 服务，提供 `/api/health`、`/api/config/status`、`/api/research`、`/api/research/events`、`/api/export/markdown`。
- LangGraph workflow，覆盖 scope、plan、research、verify、write、visualize 阶段。
- Tavily live search 接入，后端保留 mock search 供测试和离线开发。
- OpenAI-compatible LLM adapter，支持中转 key，未配置时有规则兜底。
- Evidence 数据结构，保存 claim、source、quote、stance、confidence、topic。
- Opposition Matrix，按主题聚合支持、风险、中立观点。
- Report Writer，输出直接答案、详细执行方案、指标验收、落地路线、引用来源和初步建议。
- 对 RAG 召回率问题做了专项增强：能输出 Recall@k、分块、query rewrite、hybrid search、rerank、metadata filter 等可执行方案。
- backend tests，覆盖 API、pipeline、LLM、工具、导出、报告质量和评估逻辑。

前端已完成的核心能力：

- 重新设计后的 Research Studio，不再是普通聊天页。
- 顶部轻量导航，移除了无用侧边栏、旧可视化区域和夸张大标题。
- 研究生成器输入区默认使用 Live Tavily search，不再显示演示搜索开关。
- 经典问题轮换入口，点击问题即可直接启动研究。
- Quality Overview，展示报告准备度、来源数、证据数和幻觉风险，百分比已居中。
- Agent Run，展示研究流程状态。
- Research Plan 和 Deliverables，展示任务拆解与交付标准。
- Report Studio，使用 Markdown 富渲染展示报告。
- 报告可以在新页面打开，并支持浏览器打印导出 PDF。
- Evidence Board，展示证据卡片、来源链接、立场和置信度。
- Opposition Matrix，展示支持/风险/中立观点。
- Agent Timeline，展示完整研究过程。
- 保留鼠标移动彩色流体效果，但不再干扰操作。

## 对面试展示的匹配度

整体匹配度较高。它比普通工具调用 demo 更能展示 Agent 工程能力，因为它不是“输入问题然后让模型写一段话”，而是把研究任务拆成了可观察、可测试、可追溯的流程。

它能体现的面试价值：

- **LangGraph 状态机能力**：用图编排组织研究流程，节点职责清楚。
- **多 Agent 分工**：Scope、Supervisor、Researcher、Verifier、Writer 的边界明确。
- **真实工具调用**：前端默认走 Tavily live search，能展示联网研究。
- **证据驱动生成**：报告来自 Evidence Store，而不是直接让 LLM 自由发挥。
- **反方观点意识**：Opposition Matrix 能体现对幻觉和单边结论的控制。
- **产品化表达**：前端有报告、证据、矩阵、时间线和导出，不只是聊天窗口。
- **可测试性**：backend tests 和 frontend build 能证明项目不是纯静态演示。

面试讲解主线建议：

1. 为什么选择 Deep Research：复杂、可拆解、可验证，比旅行 Agent 更能展示 Agent 架构。
2. 如何用 LangGraph 建模：每个节点负责一个研究阶段，状态在节点间传递。
3. 如何降低幻觉：所有结论先进入 Evidence Store，再由 Writer 汇总。
4. 如何做产品化：前端展示任务、证据、矩阵和报告，不只是聊天窗口。
5. 如何做工程保障：Tavily 真实搜索、mock 测试兜底、API 状态检查、测试、降级策略。

## 当前不足

当前项目已经适合演示，但还没有达到“生产级 Deep Research”的完整形态，主要差距在这里：

- **流式输出还比较浅**：`/api/research/events` 现在主要推送阶段消息，阶段产物还没有真正增量展示。
- **搜索深度仍有限**：目前每个子任务搜索结果数量有限，还没有多轮追问、交叉验证和来源去重策略。
- **引用粒度还不够细**：报告中有来源编号，但还没有做到句子级 hover 溯源和点击定位证据卡。
- **结果持久化缺失**：当前研究结果主要在内存和前端状态中，没有保存历史报告。
- **评估体系偏轻**：已有 quality metrics，但还可以加入 benchmark、人工评分和 regression dataset。
- **报告可信度可继续增强**：可以加入来源等级、发布日期、新旧冲突判断和“证据不足”标记。
- **真实 LLM 结构化输出还可强化**：当前已有 OpenAI-compatible adapter，但还可以让 Scope、Supervisor、Verifier 使用更严格的 schema output。

## 建议的下一步增强

优先级从高到低：

1. **报告历史与详情页**
   - 每次研究生成一个 report id。
   - 新页面通过 `/reports/:id` 打开。
   - 支持历史列表、重新运行、复制分享。

2. **句子级引用 hover 溯源**
   - 报告中的 `[S1]` 悬浮后展示 source title、quote、confidence。
   - 点击跳到 Evidence Board 对应证据卡。

3. **真正的流式研究事件**
   - 每个 Agent 节点完成后推送 brief、plan、evidence count、matrix preview。
   - 前端不用等最终结果才更新。

4. **来源质量评分**
   - 官方文档、论文、GitHub、博客、社交内容分级。
   - 将来源质量纳入 hallucination risk。

5. **持久化 Evidence Store**
   - SQLite 或 Postgres 保存 reports、evidence、runs。
   - 面试时可强调工程闭环。

6. **评估集**
   - 准备 5-10 个固定研究任务。
   - 记录引用覆盖率、来源数量、反方证据比例、报告结构完整度。

## 面试结论

这个项目当前已经比普通 Agent demo 更有说服力，适合定位为：

> 一个基于 LangGraph 的中文 Deep Research Agent，强调任务拆解、证据追溯、反方观点、可执行报告和产品化研究工作台，展示的是 Agent 工程化能力，而不是单次聊天生成能力。

如果面试时间只有 5 分钟，建议直接点击前端经典问题里的“RAG 怎么提高召回率？”或“LangGraph、AutoGen、CrewAI 哪个更适合企业级多 Agent 系统？”，展示从真实搜索到报告生成的完整链路。
