# Cursor Agent 使用手册与开发优势 · Day 2 接手说明

> 文档目的：对接 `09-cursor-handover-day2.md` 的接手确认，并说明与本 Agent（Cursor + Skills）协作的使用方式与开发优势。  
> 读者：项目开发者、后续接手 Agent。

---

## 一、接手开发工作确认

### 1.1 已阅读的交接内容

- **文档**：`docs/agent/09-cursor-handover-day2.md`
- **项目**：`rag-mvp`，商户客服代理（Merchant Customer-Service Agent），AI Sprint Plan V1。

### 1.2 当前状态理解

| 项目 | 状态 |
|------|------|
| **Day 1** | ✅ 已完成 |
| AG-001 商户模板校验器 | `src/agent/template_validator.py`，单测 `tests/test_template_validator.py` |
| AG-002 问答协议模型 | `src/agent/models.py`（`AgentResponse`），单测 `tests/test_agent_models.py` |
| 回归与 Git | 测试通过，Day 1 已提交 |
| **Day 2 目标** | AG-003 风险拦截（Guardrail）、AG-004 编排层基线（Orchestrator） |

### 1.3 环境与命令约定

- **Python 环境**：项目根目录 `.venv`
- **运行测试**：需设置 `PYTHONPATH=.`，例如：
  ```bash
  cd rag-mvp
  PYTHONPATH=. pytest tests/test_agent_models.py -v
  ```

### 1.4 本次接手任务（Day 2）

- **AG-003 风险拦截与转人工**  
  - 敏感词（如投诉、退款）命中 → `risk_flag=True`、`handoff=True`，不调用大模型。  
  - 先写 `tests/test_guardrail.py`，再实现 `src/agent/guardrail.py`。

- **AG-004 编排层基线**  
  - 统一路由：风险问题 → guardrail → 转人工响应；普通问题 → RAG pipeline → 组装 `AgentResponse`。  
  - 先写 `tests/test_orchestrator.py`（用 stub 隔离 pipeline），再实现 `src/agent/orchestrator.py`。

### 1.5 合并与验证标准（Exit Criteria）

- 以下命令全部通过：
  ```bash
  cd rag-mvp
  PYTHONPATH=. pytest tests/test_guardrail.py -v
  PYTHONPATH=. pytest tests/test_orchestrator.py -v
  PYTHONPATH=. pytest tests/test_cli.py -v
  PYTHONPATH=. pytest -v
  ```
- 业务约束：含敏感词的问题**不得**进入大模型自动回答；单轮链路在 Orchestrator 层可端到端跑通。

---

## 二、使用手册：如何与本 Agent 协作

本 Agent 在 Cursor 中运行，并遵循 **Skills（技能）** 与 **TDD** 等纪律。按下面方式协作，可以最大化效率和可维护性。

### 2.1 技能优先（Skill-First）

- **规则**：只要任务有可能适用某个技能（哪怕 1%），必须先调用该技能，再回复或动手写代码。
- **含义**：
  - 不要“先探索再决定”——技能会告诉你**如何**探索。
  - 不要“先写代码再补测试”——有 TDD 技能时必须先写失败测试。
- **技能类型举例**：
  - **流程类**（先执行）：brainstorming、systematic-debugging、test-driven-development、writing-plans、verification-before-completion 等。
  - **执行类**（后执行）：具体实现、前端、MCP 等。
- **示例**：“实现 AG-003” → 先走 TDD 技能（写失败测试），再实现； “先设计再实现” → 先 writing-plans 或 brainstorming。

### 2.2 测试驱动开发（TDD）纪律

- **铁律**：**没有先失败的测试，就不写生产代码。**
- **循环**：RED（写失败测试并确认失败原因）→ GREEN（最少代码通过）→ REFACTOR（仅整理，不新增行为）。
- **与本项目**：
  - 新建或修改 `src/agent` 前，必须先有对应 `tests/test_*.py` 中能复现期望行为的用例。
  - 每个新模块（如 `guardrail.py`、`orchestrator.py`）都先有测试文件，再实现。

### 2.3 如何给我下任务

- **推荐**：
  - 明确目标与验收标准（例如“AG-003：敏感词命中则 risk_flag=True, handoff=True”）。
  - 指出文档或规范（如“按 09-cursor-handover-day2 的步骤”）。
  - 需要设计时可以说“先写计划/先 brainstorm”。
- **我会**：
  - 按技能与 TDD 执行；
  - 同步更新 Docs / src / tests；
  - 在完成前按 Exit Criteria 跑一遍验证命令。

### 2.4 验证与完成标准

- 在声称“完成”前，我会运行 handover 中规定的 pytest 命令，并确保业务约束满足。
- 若你使用 **verification-before-completion** 技能，我会在完成前按该技能的检查清单执行。

### 2.5 文档与代码同步

- 每个文件/模块会兼顾：`Docs`、`src`、`tests` 的对应更新。
- 新增能力（如 guardrail 关键词列表、orchestrator 路由规则）如在设计文档中有说明，会在实现中保持一致并在文档中可追溯。

---

## 三、开发优势

在与本 Agent 协作并遵守上述手册时，会带来以下开发上的优势。

### 3.1 质量与可维护性

| 优势 | 说明 |
|------|------|
| **行为可证明** | TDD 要求“先见红再见绿”，测试真正覆盖需求行为，而不是事后补测。 |
| **回归保护** | 每次改动都有完整测试套件（如 `pytest -v`），回归可被自动发现。 |
| **契约清晰** | 使用 `AgentResponse`、`ValidationResult` 等机器可读结构，接口稳定、易于前后端与多 Agent 对接。 |

### 3.2 流程与一致性

| 优势 | 说明 |
|------|------|
| **技能驱动** | 流程类技能（TDD、debugging、writing-plans）在前，减少“想到哪写到哪”和漏步骤。 |
| **退出标准明确** | Handover 与本文档给出具体命令和业务约束，完成定义清晰，便于合并与验收。 |
| **文档与实现同步** | 要求 Docs/src/tests 一起更新，降低文档过期和实现漂移。 |

### 3.3 协作与接手

| 优势 | 说明 |
|------|------|
| **交接可复现** | 新 Agent 或人类开发者可通过 09-handover + 本文档快速理解“做到哪、接下来做什么、怎么验”。 |
| **环境与命令统一** | `PYTHONPATH=.`、`cd rag-mvp`、pytest 命令写死，减少环境差异。 |
| **纪律可审计** | TDD、技能优先、验证清单都可被检查和复盘，便于改进流程。 |

### 3.4 风险与安全

| 优势 | 说明 |
|------|------|
| **敏感问题不进入模型** | AG-003 与 AG-004 设计保证：含敏感词的问题只走 guardrail → handoff，不触发大模型自动回答。 |
| **单轮链路可端到端验证** | Orchestrator 层统一路由，便于在测试中 stub pipeline，验证分流与组装逻辑。 |

---

## 四、下一步行动

1. **立即**：按 TDD 启动 AG-003（先写 `tests/test_guardrail.py`，再实现 `src/agent/guardrail.py`）。
2. **随后**：AG-004（先写 `tests/test_orchestrator.py`，再实现 `src/agent/orchestrator.py`）。
3. **完成时**：执行全文“合并与验证标准”中的全部 pytest 命令，并确认业务约束。

如需我先执行 Day 2 的 TDD 与实现，直接说“按 10-cursor-manual 开始 Day 2”或“开始 AG-003”即可。
