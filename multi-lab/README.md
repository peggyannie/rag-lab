# multi-lab

CrewAI true multi-agent RAG MVP with orchestrated stages:
- analyst
- builder
- reviewer

Prerequisites:
- Python 3.10+
- `OPENAI_API_KEY` available in environment or `.env`

## Run

```bash
cd multi-lab
python3 -m venv .venv
source .venv/bin/activate
pip install '.[dev]'
cp .env.example .env
python -m multi_lab.main --base-dir . --data data --question "RAG 是什么？"
```
