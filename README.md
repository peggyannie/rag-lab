# rag-lab

`rag-lab` 是一个用于学习和实践 RAG（Retrieval-Augmented Generation，检索增强生成）的工作区仓库。
当前核心子项目是 `rag-mvp`，提供可运行的 CLI + Web UI MVP。

## 项目结构

```text
rag-lab/
├── docs/                 # 设计文档、方案记录
│   ├── plans/
│   └── v1/
├── rag-mvp/              # 当前可运行的 RAG MVP 子项目
└── README.md             # 当前文件（工作区总览）
```

## 当前子项目

### rag-mvp

定位：
- CLI 优先的 RAG MVP
- 双 Provider 模式：
  - `local`：离线词法检索 + 确定性回答生成
  - `openai`：OpenAI Embedding + Chroma 检索 + OpenAI 对话生成

详细说明请查看：`rag-mvp/README.md`

## 快速开始（以 rag-mvp 为例）

```bash
cd rag-mvp
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 环境变量

可复制 `rag-mvp/.env.example` 到 `rag-mvp/.env` 后按需修改，例如：

```bash
RAG_PROVIDER=openai
OPENAI_API_KEY=your_key
# 可选
OPENAI_BASE_URL=
OPENAI_EMBED_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o-mini
RAG_SCORE_THRESHOLD=0.42
RAG_RERANK_LIMIT=4
```

## 常用命令

在 `rag-mvp/` 目录执行：

```bash
# 构建/更新知识库
python cli.py --ingest data

# 查询
python cli.py --query "RAG 是什么？"

# 查看索引统计
python cli.py --stats

# 调试模式查询
python cli.py --query "RAG 是什么？" --debug

# 启动 Web UI
streamlit run app.py
```

## 测试

在 `rag-mvp/` 目录执行：

```bash
pytest
```

## 文档导航

- `docs/plans/`：阶段性设计与规划文档
- `docs/v1/`：早期部署与版本文档
- `rag-mvp/RAG知识库项目文档.md`：MVP 详细项目文档（中文）
