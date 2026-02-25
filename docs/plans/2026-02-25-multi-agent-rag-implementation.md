# Multi-Agent RAG MVP (CrewAI) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a true multi-agent orchestrated RAG MVP under `multi-lab/` using CrewAI with `analyst -> builder -> reviewer` flow.

**Architecture:** Use CrewAI sequential process with three agents loaded from YAML. Builder receives RAG tools for ingest/retrieve/answer. Local JSON-backed lexical retrieval keeps MVP deterministic while OpenAI powers agent reasoning. CLI triggers orchestrator and prints stage outputs.

**Tech Stack:** Python 3.10+, CrewAI, OpenAI, PyYAML, pytest.

---

### Task 1: Scaffold project and config contracts

**Files:**
- Create: `multi-lab/pyproject.toml`
- Create: `multi-lab/.env.example`
- Create: `multi-lab/README.md`
- Create: `multi-lab/src/multi_lab/__init__.py`
- Create: `multi-lab/src/multi_lab/config.py`
- Test: `multi-lab/tests/test_config.py`

**Step 1: Write the failing test**
- Assert env/config defaults and path resolution.

**Step 2: Run test to verify it fails**
- `python3 -m pytest multi-lab/tests/test_config.py -q`

**Step 3: Write minimal implementation**
- Implement settings loader and path helpers.

**Step 4: Run test to verify it passes**
- Same test command.

### Task 2: Build RAG tool layer

**Files:**
- Create: `multi-lab/src/multi_lab/rag_store.py`
- Create: `multi-lab/src/multi_lab/rag_tools.py`
- Test: `multi-lab/tests/test_rag_tools.py`

**Step 1: Write failing tests**
- Ingest adds chunks and dedup works.
- Query returns sourced answer or not-found fallback.

**Step 2: Verify RED**
- `python3 -m pytest multi-lab/tests/test_rag_tools.py -q`

**Step 3: Minimal implementation**
- Add chunking, lexical similarity, source tracing.

**Step 4: Verify GREEN**
- Re-run tests.

### Task 3: Implement CrewAI orchestrator

**Files:**
- Create: `multi-lab/agents.yaml`
- Create: `multi-lab/tasks.yaml`
- Create: `multi-lab/src/multi_lab/orchestrator.py`
- Create: `multi-lab/src/multi_lab/main.py`
- Test: `multi-lab/tests/test_orchestrator.py`

**Step 1: Write failing tests**
- Validate orchestrator builds three agents and runs in sequence (using stubs/mocks).

**Step 2: Verify RED**
- `python3 -m pytest multi-lab/tests/test_orchestrator.py -q`

**Step 3: Minimal implementation**
- Load YAML, instantiate Agent/Task/Crew, kickoff with inputs.

**Step 4: Verify GREEN**
- Re-run orchestrator tests.

### Task 4: CLI and end-to-end verification

**Files:**
- Create: `multi-lab/tests/test_cli.py`
- Modify: `multi-lab/src/multi_lab/main.py`

**Step 1: Write failing tests**
- CLI runs and emits analyst/builder/reviewer blocks.

**Step 2: Verify RED**
- `python3 -m pytest multi-lab/tests/test_cli.py -q`

**Step 3: Minimal implementation**
- Add argparse entrypoint and JSON/text output.

**Step 4: Verify GREEN**
- Re-run CLI tests.

### Task 5: Final verification

**Step 1: Run full tests**
- `python3 -m pytest multi-lab/tests -q`

**Step 2: Smoke run**
- `python3 -m multi_lab.main --data multi-lab/data --question "RAG 是什么？" --base-dir multi-lab`

**Step 3: Update docs**
- Finalize `multi-lab/README.md` run instructions.
