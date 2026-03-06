# Day 2 AI Agent Handover Document (For Cursor)

## 1. 当前上下文交接 (Context Handover)
你现在对接的是名为 `rag-mvp` 的项目，我们的目标是为商户客服代理（Merchant Customer-Service Agent）开发符合 AI Sprint Plan (V1) 的所需模块。

**目前状态**：
- **Day 1 本地功能（AG-001，AG-002）已完毕**：
  - [x] AG-001 商户模板校验器: `src/agent/template_validator.py` 已实现，并具有确定性、机器可读 (`ValidationResult`) 的错误输出，单测在 `tests/test_template_validator.py`。
  - [x] AG-002 问答协议模型: `src/agent/models.py` 已实现，定义了 `AgentResponse`（包含 `answer`, `sources`, `risk_flag`, `handoff`），单测在 `tests/test_agent_models.py`。
- 测试状态：全部测试跑通，包括 Day 1 要求合并验证的回归测试 (`test_pipeline.py`)。
- Git 状态：Day 1 修改的代码已经 commit 到了仓库中。

**项目环境注意点**：
- Python 环境在根目录的 `.venv` 下。
- 为了让测试找到 `src` 包路径，目前的运行命令需要在前面补充 `PYTHONPATH=. `，例如：`PYTHONPATH=. pytest tests/test_agent_models.py -v`。

---

## 2. 你的任务目标：Day 2 (Safety + Routing)
根据 Sprint Plan 设计文档，你需要接手并完成 **AG-003** 和 **AG-004**。

### 全局研发纪律 (Global Rules)
- TDD 第一：在新建或修改任何 src 代码前，**必须先写能够复现失败行为的测试**，失败后再实现逻辑。
- 每个文件/模块都请关注 `Docs`、`src`、`tests` 的对应更新。

### 任务 1：AG-003 风险拦截与转人工 (Guardrail)
- **目标**：不让大语言模型处理敏感问题（例如：投诉、退款相关词汇），而是应当直接转交人工 (`handoff`)。
- **输入输出**：判断文本中是否含风险关键词，如果有，输出修改过 `risk_flag=True` 和 `handoff=True` 的状态标识。
- **要求步骤**：
  1. 新建并编写 `tests/test_guardrail.py`（包含关键字驱动的用例及负向正常用例）。
  2. 新建并实现 `src/agent/guardrail.py`。

### 任务 2：AG-004 编排层基线 (Orchestrator Baseline)
- **目标**：实现统一路由方法，将前端的输入分配给相应的链路。
  - risky question -> guardrail 层 -> 返回转人工响应。
  - normal question -> rag pipeline 检索回答 -> 组装标准 `AgentResponse` 返回。
- **要求步骤**：
  1. 新建并编写 `tests/test_orchestrator.py`（模拟/stub pipeline 来进行测试隔离，验证分流逻辑）。
  2. 新建并实现 `src/agent/orchestrator.py`。

---

## 3. 合并与验证标准 (Exit Criteria)
1. **测试运行闭环**：
   在 Day 2 结束之时，请使用下述命令确认全部通过：
   ```bash
   cd rag-mvp
   PYTHONPATH=. pytest tests/test_guardrail.py -v
   PYTHONPATH=. pytest tests/test_orchestrator.py -v
   PYTHONPATH=. pytest tests/test_cli.py -v
   PYTHONPATH=. pytest -v
   ```
2. **逻辑业务约束**：
   - 包含敏感词组的问题**绝对不能**进行大模型的自动回答调用。
   - 单轮次聊天链路能在 Orchestrator 层次进行完整的 end-to-end 工作。
3. 如果你在运行测试时，旧有的 Pydantic Warning 仍存在，无需过多忧虑，只要业务用例不 failed 即可通过。

准备好后，请立即开始阅读项目文件并启动 AG-003 的 TDD 周期。祝你好运！
