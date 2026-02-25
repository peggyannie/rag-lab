# RAG Knowledge Base MVP

CLI-first RAG MVP with a dual-provider architecture:
- `local`: offline lexical retrieval + deterministic answer generation
- `openai`: OpenAI embeddings + Chroma retrieval + OpenAI chat completion

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Environment

Copy `.env.example` to `.env` and configure:

```bash
RAG_PROVIDER=openai
OPENAI_API_KEY=your_key
# Optional
OPENAI_BASE_URL=
OPENAI_EMBED_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o-mini
RAG_SCORE_THRESHOLD=0.42
RAG_RERANK_LIMIT=4
```

## Usage

```bash
python cli.py --ingest data
python cli.py --query "RAG 是什么？"
python cli.py --stats
```

## Web UI (Streamlit)

```bash
streamlit run app.py
```

UI includes:
- data ingest controls (`Data Path`, `chunk_size`, `chunk_overlap`)
- query controls (`Top-K`, `Debug`)
- answer, sources, retrieval result table, and prompt view

## Debug query

```bash
python cli.py --query "RAG 是什么？" --debug
```
