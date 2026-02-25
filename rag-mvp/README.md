# RAG Knowledge Base MVP

CLI-first RAG MVP with a dual-provider architecture:
- `local`: offline lexical retrieval + deterministic answer generation
- `openai`: reserved interface for remote embeddings + LLM completion

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```bash
python cli.py --ingest data
python cli.py --query "RAG 是什么？"
python cli.py --stats
```

## Debug query

```bash
python cli.py --query "RAG 是什么？" --debug
```

## Environment

Copy `.env.example` to `.env` and configure `RAG_PROVIDER`.
