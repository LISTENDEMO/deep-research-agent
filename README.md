# Deep Research Agent

中文优先的 Deep Research Agent，面向复杂研究任务，强调可解释、多 Agent 协作、证据追溯、观点对立矩阵和高质量报告生成。

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
