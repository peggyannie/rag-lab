# V1 发布说明（Merchant Agent P0 首版）

## 范围

本版本对应 AI Sprint Plan 的 **AG-001～AG-005** 及 Day4 加固，实现商户客服代理的 P0 最小闭环。

## 已包含（In Scope）

| 模块 | 说明 |
|------|------|
| **AG-001** | 商户知识模板校验：必备 section（商品信息/门店信息/配送规则/售后政策），机器可读 `ValidationResult` |
| **AG-002** | 问答协议模型 `AgentResponse`：answer、sources、risk_flag、handoff，可序列化 |
| **AG-003** | 风险拦截：敏感词（投诉、退款、举报）命中即转人工，不调用大模型 |
| **AG-004** | 编排层：风险走 guardrail，普通走 RAG pipeline，单轮链路端到端 |
| **AG-005** | API：`GET /health`、`POST /chat`、`GET /handoff`，请求/响应符合协议契约 |
| **Day4** | 边缘用例（空来源/未知问题 fallback）加固，Runbook/验证清单/发布说明对齐 |

## 不包含（Out of Scope for V1）

- 短会话记忆（AG-101）、成交引导（AG-102）、指标聚合（AG-103）
- 混合检索（AG-201）、自动评测（AG-202）、多渠道接入（AG-203）
- `/handoff` 的工单/排队等增强

## 验收与运行

- **测试**：`cd rag-mvp && PYTHONPATH=. .venv/bin/python -m pytest -v` → 47 passed
- **CLI 冒烟**：`PYTHONPATH=. python cli.py --ingest data`，`PYTHONPATH=. python cli.py --query "配送范围是什么？" --debug`
- **API**：`PYTHONPATH=. python -m src.api`，访问 `/health`、`/chat`、`/handoff`

## 文档

- 使用与交接：`10-cursor-manual-and-day2-handover.md`
- Day2/3 完成：`12-day2-completion.md`、`13-day3-completion.md`
- 运行与排障：`06-runbook.md`
- 验证清单：`05-verification-checklist.md`
