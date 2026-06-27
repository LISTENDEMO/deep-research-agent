# 任务计划：Deep Research Agent

## 目标
规划一个可用于面试展示和后续完整实现的 Deep Research Agent，支持复用 Open Deep Research 的架构思想与部分 MIT 代码，并形成清晰的产品、技术、前端和实施路线。

## 当前阶段
阶段 6 已完成；项目具备可运行后端、前端、LangGraph 编排、流式事件、评估脚本和面试材料。

## 各阶段

### 阶段 1：需求与发现
- [x] 理解用户意图：放弃旅行 Agent，转向更有价值的 Deep Research Agent
- [x] 确定约束：LangChain/LangGraph 方向、可沿用 Open Deep Research、面试展示价值优先
- [x] 将发现记录到 findings.md
- **状态：** complete

### 阶段 2：规划与结构
- [x] 确定产品定位和差异化亮点
- [x] 确定技术架构、Agent 流程和模块边界
- [x] 输出主设计文档 docs/deep-research-agent-design.md
- **状态：** complete

### 阶段 3：实现准备
- [x] 确认直接开始编码
- [x] 决定复用方式：A + 少量 B，原创实现为主，借鉴 Open Deep Research 架构
- [x] 初始化 Python 后端与 React/Three.js 前端工程
- **状态：** complete

### 阶段 4：MVP 实现
- [x] 实现 Scope -> Research -> Write 的可运行流程
- [x] 实现 Supervisor + Researcher 子 Agent 的最小版本
- [x] 实现 mock 搜索、引用、证据抽取、报告生成
- [x] 实现基础前端研究工作台和 Three.js 研究星图
- **状态：** complete

### 阶段 5：亮点增强
- [x] 实现基础证据图谱
- [x] 实现时间线、观点对立矩阵
- [x] 实现研究过程可视化和可追溯引用
- [x] 加入评估脚本和演示样例
- **状态：** complete

### 阶段 6：测试与交付
- [x] 单元测试：状态迁移、引用解析、报告结构
- [x] 集成测试：一次完整研究任务
- [x] 前端验证：桌面关键页面
- [x] README、面试讲解稿、演示数据
- **状态：** complete

## 关键问题
1. 项目目标更偏“面试项目作品”还是“真实可用工具”？
2. 搜索源优先使用 Tavily、SerpAPI、Firecrawl，还是先做可插拔接口？
3. 前端是否继续使用 Three.js 做“研究星图/证据宇宙”的动态视觉亮点？

## 已做决策
| 决策 | 理由 |
|------|------|
| 方向改为 Deep Research Agent | 比旅行 Agent 更有技术含量，更适合展示 LangGraph、多 Agent、RAG、工具调用和评估 |
| 借鉴 Open Deep Research 三阶段架构 | Scope/Research/Write 简洁且可解释，适合面试讲解 |
| 不照搬多段并行写作 | Open Deep Research 经验显示并行写作会导致报告割裂，最终报告应由一个 Writer 统一生成 |
| 先规划，不直接实现 | 用户当前要求是“规划一下”，需要确认后再进入编码 |
| API Key 不写入仓库 | 用户提供了 Tavily key，但密钥应通过环境变量读取 |
| 前端默认使用 mock research | 没有模型 key 也能演示完整链路，后续再切真实搜索和 LLM |
| 使用 LangGraph StateGraph 作为唯一后端编排入口 | 避免顺序 runner 和图编排双轨漂移 |
| 增加 NDJSON 流式事件接口 | 前端可以展示 Agent 研究过程，而不是只等待最终结果 |

## 遇到的错误
| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| 无 | 0 | 无 |

## 备注
- Open Deep Research 为 MIT 许可，若复用代码需保留许可证与来源说明。
- 后续实现建议先做 MVP，再做视觉和评估亮点。
