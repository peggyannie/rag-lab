# 系统上下文（供 AI Agent 快速上手）

## 1. 仓库概览
- 工作区：`rag-lab`
- 核心项目：`rag-mvp`
- 设计文档：`docs/plans/`

## 2. 关键目录
- `rag-mvp/src/`：核心实现（loader/store/retriever/generator/pipeline）
- `rag-mvp/tests/`：测试
- `rag-mvp/data/`：知识库数据
- `rag-mvp/app.py`：Streamlit 页面
- `rag-mvp/cli.py`：CLI 入口

## 3. 当前能力边界
- 支持 `.md/.txt` 导入。
- 支持 `local` 与 `openai` 双 Provider。
- 支持问答、来源展示和 debug prompt。
- 尚未内置完整 API 服务层与会话管理层。

## 4. 常用命令
```bash
cd rag-mvp
python cli.py --ingest data
python cli.py --query "配送范围是什么？" --debug
python cli.py --stats
pytest -v
streamlit run app.py
```

## 5. 核心链路
1. `loader` 读取文档并切块。
2. `pipeline.ingest` 写入向量存储。
3. `pipeline.query` 检索、重排、生成答案。
4. UI/CLI 展示回答与来源。

## 6. 本期扩展点（客服成交 Agent）
- 新增 `src/agent/`：模型、编排、风控、会话存储、指标聚合。
- 新增 `api.py`：`/chat`、`/handoff`、`/health`。
