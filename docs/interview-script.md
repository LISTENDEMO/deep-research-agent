# Deep Research Agent 面试讲解稿

## 30 秒版本

这是一个中文优先的 Deep Research Agent。它不是简单搜索总结，而是用 LangGraph 把研究流程拆成 Scope、Plan、Research、Verify、Write 和 Visualize。系统会生成研究简报，拆解子任务，抽取支持/反对/中立证据，形成观点对立矩阵，最后生成带引用的中文报告，并在前端提供可追溯的研究工作台。

## 技术亮点

1. **LangGraph 状态编排**
   - 用 `StateGraph` 串起研究流程，节点职责清晰。
   - 后续可以扩展 checkpoint、human-in-the-loop 和并行 research 子图。

2. **Evidence-grounded 报告**
   - 每条结论都有 `source_url`、`quote`、`stance` 和 `confidence`。
   - 最终报告不是凭空写，而是从 Evidence Store 汇总。

3. **观点对立矩阵**
   - 不只输出支持观点，也主动呈现风险和反方证据。
   - 用 `opposition_balance` 衡量研究是否过于单边。

4. **可插拔模型和搜索**
   - 前端默认走 Tavily 真实搜索，后端保留 mock search 供测试和离线开发。
   - LLM 层支持 OpenAI-compatible 配置，未配置 key 时有规则兜底。

5. **产品化前端**
   - 前端不是普通聊天页，而是研究任务控制台。
   - 鼠标移动有流体光轨效果，经典问题可以轮换并一键启动研究。
   - 报告、证据、观点矩阵和流程时间线都能独立展示。

## 为什么不用完全复制 Open Deep Research

Open Deep Research 的 Scope/Research/Write 架构非常适合借鉴，但完整复制会削弱项目原创性。因此本项目选择 A + 少量 B：

- 借鉴三阶段研究流程和 Supervisor 思想。
- 自己实现 Evidence Store、观点矩阵、质量指标和 Research Studio 前端。
- 保持 MIT 项目的复用边界清晰。

## 演示顺序

1. 打开前端研究控制台。
2. 输入“研究 LangGraph、AutoGen、CrewAI 哪个更适合企业级多 Agent 系统”。
3. 点击启动研究，展示流式 Agent 步骤。
4. 指出经典问题入口、运行流程和报告质量概览。
5. 展示 Evidence Board 和观点对立矩阵。
6. 展示 Report Studio 和 Markdown 下载。
7. 最后展示后端测试和评估脚本。

## 可继续扩展

- 接真实 LLM structured output。
- Researcher 子图并行化。
- 引用原文片段二次校验。
- 加入研究历史、报告详情页和句子级引用 hover。
- 引入 Deep Research Bench 风格评测集。
