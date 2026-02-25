# RAG MVP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a runnable CLI-first RAG knowledge base MVP with dual providers (`local` and `openai`) and debuggable retrieval/generation flow.

**Architecture:** Implement a thin modular pipeline in `src/` (`loader`, `store`, `retriever`, `generator`, `pipeline`) and expose commands in `cli.py`. `local` mode works offline using deterministic lexical retrieval and rule-based generation; `openai` mode uses OpenAI embeddings/chat while reusing the same pipeline contract.

**Tech Stack:** Python 3.10+, uv, chromadb, openai, pytest, python-dotenv.

---

### Task 1: Project scaffolding and dependency baseline

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `.env.example`
- Create: `src/__init__.py`
- Create: `src/config.py`

**Step 1: Write the failing test**
- Add a config test expecting default provider to be `local` and required directories to resolve.

**Step 2: Run test to verify it fails**
- Run: `pytest tests/test_config.py -v`
- Expected: FAIL (missing module).

**Step 3: Write minimal implementation**
- Add config dataclass and env loading helper.

**Step 4: Run test to verify it passes**
- Run same test; expected PASS.

### Task 2: Loader and chunking with overlap

**Files:**
- Create: `src/loader.py`
- Create: `tests/test_loader.py`

**Step 1: Write failing tests**
- Test markdown/txt loading by directory.
- Test chunk splitting with overlap and metadata.

**Step 2: Verify RED**
- `pytest tests/test_loader.py -v`

**Step 3: Minimal implementation**
- Implement `load_documents` and `chunk_text`.

**Step 4: Verify GREEN**
- Re-run same tests.

### Task 3: Vector storage and dedup

**Files:**
- Create: `src/store.py`
- Create: `tests/test_store.py`

**Step 1: Write failing tests**
- Add chunks once, re-add same chunks, assert count unchanged.
- Assert similarity query returns expected top item.

**Step 2: Verify RED**
- `pytest tests/test_store.py -v`

**Step 3: Minimal implementation**
- Implement persistent JSON-backed local store with cosine similarity and stable IDs.

**Step 4: Verify GREEN**
- Re-run tests.

### Task 4: Retriever, generator, and pipeline orchestration

**Files:**
- Create: `src/retriever.py`
- Create: `src/generator.py`
- Create: `src/pipeline.py`
- Create: `tests/test_pipeline.py`

**Step 1: Write failing tests**
- Empty KB should return "知识库中未找到相关内容".
- Ingest + ask should include source info and use retrieved context.

**Step 2: Verify RED**
- `pytest tests/test_pipeline.py -v`

**Step 3: Minimal implementation**
- Implement local retrieval and local answer generation contracts.

**Step 4: Verify GREEN**
- Re-run pipeline tests.

### Task 5: CLI integration

**Files:**
- Create: `cli.py`
- Create: `tests/test_cli.py`

**Step 1: Write failing tests**
- `--ingest`, `--query`, `--stats` basic execution paths.

**Step 2: Verify RED**
- `pytest tests/test_cli.py -v`

**Step 3: Minimal implementation**
- Wire argparse into pipeline methods and debug printing.

**Step 4: Verify GREEN**
- Re-run CLI tests.

### Task 6: Final verification and docs

**Files:**
- Modify: `README.md`

**Step 1: Full verification**
- `pytest -v`

**Step 2: Runtime smoke checks**
- `python cli.py --ingest data`
- `python cli.py --query "..."`

**Step 3: Document usage and env config**
- Update README quickstart and commands.
