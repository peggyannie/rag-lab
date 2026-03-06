# Day 4 完成说明（加固与发布候选）

## 完成项

| 任务 | 说明 | 状态 |
|------|------|------|
| 边缘用例加固 | 未知问题/空来源：新增 `test_chat_unknown_question_returns_empty_sources_and_fallback_answer` 锁定契约 | ✅ |
| 全量测试 | `pytest -v` 47 passed | ✅ |
| CLI 冒烟 | `cli.py --ingest data`、`cli.py --query "配送范围是什么？" --debug` 已跑通 | ✅ |
| Runbook | 补充 API 启动流程与 Guardrail 触发条件/操作 | ✅ |
| 验证清单 | 增加 V1 状态说明与发布说明引用 | ✅ |
| V1 发布说明 | `14-v1-release-note.md`：In/Out 范围、验收命令、文档索引 | ✅ |

## 验收命令（与 Sprint 一致）

```bash
cd rag-mvp
PYTHONPATH=. .venv/bin/python -m pytest -v
PYTHONPATH=. python cli.py --ingest data
PYTHONPATH=. python cli.py --query "配送范围是什么？" --debug
```

Exit criteria 已满足：全部测试通过、功能冒烟通过、文档与已交付行为对齐。
