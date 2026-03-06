# 运行与排障手册（Runbook）

## 1. 启动流程

### CLI + Streamlit
```bash
cd rag-mvp
source .venv/bin/activate   # 或 Windows: .venv\Scripts\activate
PYTHONPATH=. python cli.py --ingest data
PYTHONPATH=. python cli.py --query "测试问题" --debug
streamlit run app.py
```

### API 服务（Agent 最小闭环）
```bash
cd rag-mvp
PYTHONPATH=. python -m src.api
# 默认 0.0.0.0:8000；GET /health、POST /chat、GET /handoff
```

## 2. 常见问题

### 问题 A：查询无结果
- 检查是否 ingest 过数据。
- 检查 `RAG_SCORE_THRESHOLD` 是否过高。
- 用 `--debug` 查看检索结果和 prompt。

### 问题 B：OpenAI 模式报错
- 检查 `OPENAI_API_KEY`。
- 检查 `OPENAI_BASE_URL` 是否可访问。
- 检查 embedding/chat 模型名是否有效。

### 问题 C：回答与资料不一致
- 检查 source 是否命中正确文档。
- 降低阈值或提高 `top_k` 进行对比。
- 对关键条目补充结构化模板数据。

## 3. 人工接管应急（Guardrail）
- 触发条件：命中敏感词（投诉、退款、举报等，见 `src/agent/guardrail.py` 的 `RISK_KEYWORDS`）。
- 操作：编排层不调用大模型，直接返回 `handoff=true`、转人工提示文案。
- API：`POST /chat` 返回 `risk_flag`/`handoff`；前端可再调 `GET /handoff` 获取确认文案。
- 回放：从日志导出问题与上下文用于复盘。

## 4. 观测建议
- 最少记录：`session_id`、问题、耗时、是否转人工、来源。
- 每日看板：应答率、转人工率、空回答率、P95 响应时长。
