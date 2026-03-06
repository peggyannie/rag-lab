# C-Merchant Agent Week 1 Checklist (Day 1-7)

> Archived on 2026-03-05.
> Deprecated as primary execution checklist.
> Use `docs/agent/` for current AI-agent task execution and verification.

> 周目标：完成 P0 基础搭建（知识模板、导入校验、FAQ 基线、回答协议）。

## 1. 每日任务清单

### Day 1
- [ ] 明确知识模板字段：`商品信息`、`门店信息`、`配送规则`、`售后政策`
- [ ] 创建模板文件：`rag-mvp/data/templates/merchant_profile.md`
- [ ] 在 README 增加模板填写说明（草稿）

### Day 2
- [ ] 新增校验器：`rag-mvp/src/agent/template_validator.py`
- [ ] 新增测试：`rag-mvp/tests/test_template_validator.py`
- [ ] 跑通模板校验失败提示（缺字段时输出缺失项）

### Day 3
- [ ] 准备 FAQ 样本 30-50 条（真实商户问题优先）
- [ ] 组织数据文件到 `rag-mvp/data/merchant-faq/`
- [ ] 重新 ingest 并完成一次离线检索抽样

### Day 4
- [ ] 定义回答协议：`answer`、`sources`、`risk_flag`、`handoff`
- [ ] 新增协议模型：`rag-mvp/src/agent/models.py`
- [ ] 新增模型测试：`rag-mvp/tests/test_agent_models.py`

### Day 5
- [ ] 新增风险规则：`rag-mvp/src/agent/guardrail.py`
- [ ] 新增风险测试：`rag-mvp/tests/test_guardrail.py`
- [ ] 规则覆盖投诉/退款/赔偿/举报等敏感场景

### Day 6
- [ ] 新增编排层：`rag-mvp/src/agent/orchestrator.py`
- [ ] 打通“正常问答 / 风险转人工”分流
- [ ] 新增编排测试：`rag-mvp/tests/test_orchestrator.py`

### Day 7
- [ ] 输出周报：命中率基线、风险误答样本、待修复问题
- [ ] 更新实施文档（已完成项 + 下周计划）
- [ ] 准备第 2 周 API 接口任务拆解

## 2. 第 1 周测试清单

### 单测（必须通过）
- [ ] `cd rag-mvp && pytest tests/test_template_validator.py -v`
- [ ] `cd rag-mvp && pytest tests/test_agent_models.py -v`
- [ ] `cd rag-mvp && pytest tests/test_guardrail.py -v`
- [ ] `cd rag-mvp && pytest tests/test_orchestrator.py -v`

### 回归测试（至少执行一次）
- [ ] `cd rag-mvp && pytest tests/test_pipeline.py -v`
- [ ] `cd rag-mvp && pytest tests/test_cli.py -v`

### 手工验证（必须记录结果）
- [ ] ingest 成功：`cd rag-mvp && python cli.py --ingest data`
- [ ] 常见问答命中：`cd rag-mvp && python cli.py --query "今天配送范围？" --debug`
- [ ] 风险问题转人工：`cd rag-mvp && python cli.py --query "我要投诉退款" --debug`

## 3. 周验收标准（Week 1 Exit Criteria）

- [ ] 可稳定 ingest 商户模板数据，且缺字段能被校验器识别。
- [ ] FAQ 基线集（30-50 条）已建并可复测。
- [ ] 回答协议已在代码层落地并可序列化输出。
- [ ] 风险问题不走自动生成，返回 `handoff=true`。
- [ ] 单测与关键回归测试均通过。

## 4. 周末交付物

- [ ] 代码 PR（模板 + 校验 + 模型 + guardrail + orchestrator）。
- [ ] 测试报告（通过率、失败样本、修复结论）。
- [ ] 《Week1 复盘》1 页（问题、决策、Week2 风险）。
