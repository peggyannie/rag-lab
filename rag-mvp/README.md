# RAG 知识库 MVP

这是一个优先支持命行交互 (CLI-first) 的 RAG（检索增强生成）MVP 项目，采用双模型提服务架构：
- `local`: 离线词汇检索 + 确定性答案生成（不依赖大模型）
- `openai`: OpenAI Embedding 模型 + ChromaDB 向量检索 + OpenAI 聊天完成模型

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 环境配置

复制 `.env.example` 文件重命名为 `.env`，并进行如下配置：

```bash
RAG_PROVIDER=openai
OPENAI_API_KEY=你的_api_key
# 可选项
OPENAI_BASE_URL=
OPENAI_EMBED_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o-mini
RAG_SCORE_THRESHOLD=0.42
RAG_RERANK_LIMIT=4
```

## 命令行使用

```bash
# 导入并处理数据
python cli.py --ingest data
# 提问查询
python cli.py --query "RAG 是什么？"
# 查看知识库统计信息
python cli.py --stats
```

## Web 界面 (Streamlit)

```bash
streamlit run app.py
```

Web 界面包含以下功能：
- 数据导入控制区（配置 `文档路径`、`chunk_size`(分块大小)、`chunk_overlap`(分块重叠数)）
- 查询控制区（配置 `Top-K`(召回数量)、`Debug`(调试模式)）
- 展示生成的回答、信息来源、检索结果数据表以及最终的 Prompt 视图

## 调试查询

使用 `--debug` 标志可以查看查询的详细中间过程：

```bash
python cli.py --query "RAG 是什么？" --debug
```

## API 服务（AG-005）

提供 `/health`、`/chat`、`/handoff` 最小闭环接口，请求/响应符合 Agent 协议（answer、sources、risk_flag、handoff）。

```bash
# 在项目根目录 rag-mvp 下启动（自动挂载本地 RAG pipeline）
PYTHONPATH=. python -m src.api
# 或指定端口
PYTHONPATH=. python -m src.api  # 默认 0.0.0.0:8000
```

- `GET /health`：返回 `{"status": "ok"}`，用于存活探测。
- `POST /chat`：请求体 `{"question": "..."}`，返回协议四字段；风险问题自动 `handoff=true`。
- `GET /handoff`：返回转人工确认信息。
