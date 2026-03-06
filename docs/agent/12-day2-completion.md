# Day 2 完成说明（AG-003 / AG-004）

## 完成项

| 任务 | 实现 | 测试 | 状态 |
|------|------|------|------|
| **AG-003** 风险拦截与转人工 | `src/agent/guardrail.py` | `tests/test_guardrail.py` | ✅ |
| **AG-004** 编排层基线 | `src/agent/orchestrator.py` | `tests/test_orchestrator.py` | ✅ |

## 行为摘要

- **AG-003**：`check_risk(text)` 检测风险关键词（投诉、退款、举报），命中则返回 `AgentResponse(risk_flag=True, handoff=True, answer=转人工提示)`，否则返回无风险响应。敏感问题**不调用大模型**。
- **AG-004**：`run(question, pipeline)` 先走 guardrail；若 `handoff` 则直接返回转人工响应；否则调用 `pipeline.query(question)` 并组装 `AgentResponse`。单轮链路在编排层端到端跑通。

## 验证结果

```bash
cd rag-mvp
PYTHONPATH=. .venv/bin/python -m pytest tests/test_guardrail.py tests/test_orchestrator.py tests/test_cli.py -v   # 11 passed
PYTHONPATH=. .venv/bin/python -m pytest -v   # 41 passed, 4 warnings (Pydantic/ChromaDB，可忽略)
```

满足 handover 合并与验证标准，可继续 AG-005（API 最小闭环）。
