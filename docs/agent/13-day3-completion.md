# Day 3 完成说明（AG-005 API 最小闭环）

## 完成项

| 任务 | 实现 | 测试 | 状态 |
|------|------|------|------|
| **AG-005** API 最小闭环 | `src/api.py` | `tests/test_api.py` | ✅ |

## 接口契约

- **GET /health**：200，`{"status": "ok"}`。
- **POST /chat**：请求体 `{"question": "..."}`，200 时返回 `answer`、`sources`、`risk_flag`、`handoff`；缺 `question` 时 422。
- **GET /handoff**：200，`{"handoff": true, "message": "..."}`。

编排层已接入：`/chat` 通过 `orchestrator.run(question, pipeline)` 路由，风险问题不调用大模型，直接返回转人工响应。

## 依赖与启动

- **依赖**：`pyproject.toml` 已增加 `fastapi`、`uvicorn[standard]`。
- **启动**：在 `rag-mvp` 目录下执行 `PYTHONPATH=. python -m src.api`，自动挂载本地 `RagPipeline`，监听 0.0.0.0:8000。

## 验证结果

```bash
cd rag-mvp
PYTHONPATH=. .venv/bin/python -m pytest tests/test_api.py tests/test_pipeline.py tests/test_cli.py -v   # 11 passed
PYTHONPATH=. .venv/bin/python -m pytest -v   # 46 passed
```

满足 Day 3 Exit Criteria：API 最小闭环可用、可测，请求/响应字段符合 Agent 契约。
