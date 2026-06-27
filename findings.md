# 发现与决策

## 需求
- 用户希望把原 TravelOps Agent 项目删除后，重新规划一个更有价值的 Deep Research Agent。
- 项目需要适合面试展示，最好体现 LangChain/LangGraph Agent 工程能力。
- 可以沿用 Open Deep Research 的部分代码或架构。

## 研究发现
- Open Deep Research 是 LangChain AI 开源的 Deep Research Agent，仓库地址：https://github.com/langchain-ai/open_deep_research
- 它基于 LangGraph，核心流程是 Scope、Research、Write。
- Scope 阶段负责澄清用户需求并生成 research brief。
- Research 阶段由 Supervisor 将任务拆给多个 Researcher 子 Agent，子 Agent 独立搜索、调用工具、整理带引用的发现。
- Research 后会进行内容压缩，避免上下文膨胀。
- Write 阶段倾向于一次性统一生成最终报告，而不是多个 Agent 分段写作后拼接。
- Open Deep Research 支持多模型、多搜索工具、MCP，并有 Deep Research Bench 评估思路。
- 对本项目最有价值的不是复制 UI，而是复用 LangGraph 状态流、多 Agent 分工、可配置工具、评估方式。

## 技术决策
| 决策 | 理由 |
|------|------|
| 后端使用 Python + LangGraph | 和 Open Deep Research 同栈，便于复用，面试解释成本低 |
| 核心流程采用 Scope -> Plan -> Research -> Synthesize -> Report | 在 Open Deep Research 基础上增强“规划”和“证据整合”能力 |
| 使用 Supervisor/Researcher/Verifier/Writer 四类 Agent | 能体现多 Agent 协作、质量控制和最终表达统一 |
| 引入 Evidence Store | 让报告每个结论可追溯，形成项目亮点 |
| 前端做 Research Mission Control | 比普通聊天框更有展示价值，突出研究过程透明化 |

## 遇到的问题
| 问题 | 解决方案 |
|------|---------|
| Deep Research 项目容易变成“搜索 + 总结” | 增加证据图谱、观点对立矩阵、置信度、引用追溯、评估模块 |
| 直接复制 Open Deep Research 可能缺少个人亮点 | 只复用底层图和工具接口思想，在产品层做更强可视化和质量控制 |

## 资源
- Open Deep Research GitHub：https://github.com/langchain-ai/open_deep_research
- LangChain 博客介绍：https://www.langchain.com/blog/open-deep-research
- LangGraph GitHub：https://github.com/langchain-ai/langgraph

## 视觉/浏览器发现
- Open Deep Research 的亮点主要在 Agent 架构，不在前端视觉。
- 本项目可以通过 Three.js “证据宇宙/研究星图”补足展示冲击力。

---
*每执行2次查看/浏览器/搜索操作后更新此文件*
*防止视觉信息丢失*
