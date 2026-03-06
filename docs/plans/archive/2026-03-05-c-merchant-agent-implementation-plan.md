# C-Merchant Native Agent Implementation Plan

> Archived on 2026-03-05.
> This file is kept for reference only.
> For current AI-agent execution, use `docs/agent/` as source of truth.

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a production-leaning customer-service-and-conversion agent on top of `rag-mvp` within 30 days, starting with a P0 single-channel closed loop.

**Architecture:** Keep retrieval/generation in `src/pipeline.py`, add a thin `agent` orchestration layer for routing and guardrails, and expose a minimal FastAPI surface for external channel adapters. Persist conversation logs and basic metrics in SQLite for traceability and operations.

**Tech Stack:** Python 3.10+, FastAPI, Uvicorn, Pydantic, pytest, existing `rag-mvp` local/openai providers.

---

### Task 1: Define chat contract and domain models

**Files:**
- Create: `rag-mvp/src/agent/models.py`
- Create: `rag-mvp/tests/test_agent_models.py`

**Step 1: Write the failing test**

```python
from src.agent.models import ChatRequest, ChatResponse


def test_chat_response_defaults():
    req = ChatRequest(session_id="s1", question="配送范围是哪里？")
    rsp = ChatResponse(answer="支持三公里配送", sources=["delivery.md"])
    assert req.session_id == "s1"
    assert rsp.risk_flag is False
    assert rsp.handoff is False
```

**Step 2: Run test to verify it fails**

Run: `cd rag-mvp && pytest tests/test_agent_models.py::test_chat_response_defaults -v`  
Expected: FAIL with `ModuleNotFoundError` for `src.agent`.

**Step 3: Write minimal implementation**

```python
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    risk_flag: bool = False
    handoff: bool = False
```

**Step 4: Run test to verify it passes**

Run: `cd rag-mvp && pytest tests/test_agent_models.py::test_chat_response_defaults -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git -C rag-mvp add src/agent/models.py tests/test_agent_models.py
git -C rag-mvp commit -m "feat(agent): add chat request and response models"
```

### Task 2: Add guardrail rules for risk/handoff routing

**Files:**
- Create: `rag-mvp/src/agent/guardrail.py`
- Create: `rag-mvp/tests/test_guardrail.py`

**Step 1: Write the failing test**

```python
from src.agent.guardrail import evaluate_risk


def test_refund_complaint_requires_handoff():
    result = evaluate_risk("我要投诉并且退款，快点处理")
    assert result["risk_flag"] is True
    assert result["handoff"] is True
```

**Step 2: Run test to verify it fails**

Run: `cd rag-mvp && pytest tests/test_guardrail.py::test_refund_complaint_requires_handoff -v`  
Expected: FAIL with missing `evaluate_risk`.

**Step 3: Write minimal implementation**

```python
RISK_KEYWORDS = {"投诉", "退款", "赔偿", "法律", "举报"}


def evaluate_risk(question: str) -> dict[str, bool]:
    text = question.strip()
    risky = any(word in text for word in RISK_KEYWORDS)
    return {"risk_flag": risky, "handoff": risky}
```

**Step 4: Run test to verify it passes**

Run: `cd rag-mvp && pytest tests/test_guardrail.py::test_refund_complaint_requires_handoff -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git -C rag-mvp add src/agent/guardrail.py tests/test_guardrail.py
git -C rag-mvp commit -m "feat(agent): add risk guardrail routing"
```

### Task 3: Implement conversation log store

**Files:**
- Create: `rag-mvp/src/agent/conversation_store.py`
- Create: `rag-mvp/tests/test_conversation_store.py`

**Step 1: Write the failing test**

```python
from src.agent.conversation_store import ConversationStore


def test_append_and_fetch_latest_messages(tmp_path):
    db = tmp_path / "chat.db"
    store = ConversationStore(db)
    store.append("s1", "q", "配送吗？", {"sources": []})
    rows = store.latest("s1", limit=5)
    assert len(rows) == 1
    assert rows[0]["role"] == "q"
```

**Step 2: Run test to verify it fails**

Run: `cd rag-mvp && pytest tests/test_conversation_store.py::test_append_and_fetch_latest_messages -v`  
Expected: FAIL with missing store class.

**Step 3: Write minimal implementation**

```python
import json
import sqlite3
from pathlib import Path


class ConversationStore:
    def __init__(self, db_path: Path):
        self.conn = sqlite3.connect(str(db_path))
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS messages (session_id TEXT, role TEXT, content TEXT, meta TEXT)"
        )

    def append(self, session_id: str, role: str, content: str, meta: dict):
        self.conn.execute(
            "INSERT INTO messages(session_id, role, content, meta) VALUES (?, ?, ?, ?)",
            (session_id, role, content, json.dumps(meta, ensure_ascii=False)),
        )
        self.conn.commit()

    def latest(self, session_id: str, limit: int = 6):
        cur = self.conn.execute(
            "SELECT role, content, meta FROM messages WHERE session_id=? ORDER BY rowid DESC LIMIT ?",
            (session_id, limit),
        )
        return [{"role": r[0], "content": r[1], "meta": json.loads(r[2])} for r in cur.fetchall()]
```

**Step 4: Run test to verify it passes**

Run: `cd rag-mvp && pytest tests/test_conversation_store.py::test_append_and_fetch_latest_messages -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git -C rag-mvp add src/agent/conversation_store.py tests/test_conversation_store.py
git -C rag-mvp commit -m "feat(agent): add sqlite conversation log store"
```

### Task 4: Build agent orchestrator on top of RagPipeline

**Files:**
- Create: `rag-mvp/src/agent/orchestrator.py`
- Create: `rag-mvp/tests/test_orchestrator.py`

**Step 1: Write the failing test**

```python
from src.agent.orchestrator import AgentOrchestrator


class StubPipeline:
    def query(self, question: str, top_k: int = 3, debug: bool = False):
        return {"answer": "支持同城配送", "sources": ["delivery.md"], "results": []}


def test_risky_question_handoff():
    agent = AgentOrchestrator(pipeline=StubPipeline(), store=None)
    rsp = agent.chat(session_id="s1", question="我要投诉退款")
    assert rsp.handoff is True
    assert rsp.risk_flag is True
```

**Step 2: Run test to verify it fails**

Run: `cd rag-mvp && pytest tests/test_orchestrator.py::test_risky_question_handoff -v`  
Expected: FAIL because `AgentOrchestrator` is missing.

**Step 3: Write minimal implementation**

```python
from src.agent.guardrail import evaluate_risk
from src.agent.models import ChatResponse


class AgentOrchestrator:
    def __init__(self, pipeline, store):
        self.pipeline = pipeline
        self.store = store

    def chat(self, session_id: str, question: str) -> ChatResponse:
        risk = evaluate_risk(question)
        if risk["handoff"]:
            return ChatResponse(answer="该问题已转人工处理，请稍候。", risk_flag=True, handoff=True)
        result = self.pipeline.query(question, top_k=3, debug=False)
        return ChatResponse(answer=result["answer"], sources=result.get("sources", []), risk_flag=False, handoff=False)
```

**Step 4: Run test to verify it passes**

Run: `cd rag-mvp && pytest tests/test_orchestrator.py::test_risky_question_handoff -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git -C rag-mvp add src/agent/orchestrator.py tests/test_orchestrator.py
git -C rag-mvp commit -m "feat(agent): add chat orchestration with guardrail"
```

### Task 5: Expose API endpoints for chat/handoff/health

**Files:**
- Create: `rag-mvp/api.py`
- Create: `rag-mvp/tests/test_api.py`
- Modify: `rag-mvp/pyproject.toml`

**Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient
from api import app


def test_health_ok():
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
```

**Step 2: Run test to verify it fails**

Run: `cd rag-mvp && pytest tests/test_api.py::test_health_ok -v`  
Expected: FAIL due to missing `api.py` or FastAPI dependency.

**Step 3: Write minimal implementation**

```python
from fastapi import FastAPI

app = FastAPI(title="RAG Merchant Agent API")


@app.get("/health")
def health():
    return {"status": "ok"}
```

**Step 4: Run test to verify it passes**

Run: `cd rag-mvp && pytest tests/test_api.py::test_health_ok -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git -C rag-mvp add api.py tests/test_api.py pyproject.toml
git -C rag-mvp commit -m "feat(api): add fastapi health endpoint"
```

### Task 6: Add merchant KB template and ingestion validation

**Files:**
- Create: `rag-mvp/src/agent/template_validator.py`
- Create: `rag-mvp/data/templates/merchant_profile.md`
- Create: `rag-mvp/tests/test_template_validator.py`

**Step 1: Write the failing test**

```python
from src.agent.template_validator import validate_sections


def test_missing_required_sections():
    text = "# 商品信息\n- 名称: A"
    errors = validate_sections(text)
    assert "售后政策" in errors
```

**Step 2: Run test to verify it fails**

Run: `cd rag-mvp && pytest tests/test_template_validator.py::test_missing_required_sections -v`  
Expected: FAIL with missing validator.

**Step 3: Write minimal implementation**

```python
REQUIRED = ["商品信息", "门店信息", "配送规则", "售后政策"]


def validate_sections(text: str) -> list[str]:
    missing = [name for name in REQUIRED if name not in text]
    return missing
```

**Step 4: Run test to verify it passes**

Run: `cd rag-mvp && pytest tests/test_template_validator.py::test_missing_required_sections -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git -C rag-mvp add src/agent/template_validator.py data/templates/merchant_profile.md tests/test_template_validator.py
git -C rag-mvp commit -m "feat(agent): add merchant kb template validation"
```

### Task 7: Add week-3 short memory injection

**Files:**
- Modify: `rag-mvp/src/agent/orchestrator.py`
- Modify: `rag-mvp/src/agent/conversation_store.py`
- Create: `rag-mvp/tests/test_orchestrator_memory.py`

**Step 1: Write the failing test**

```python
from src.agent.orchestrator import AgentOrchestrator


class CapturePipeline:
    def __init__(self):
        self.last_question = ""

    def query(self, question: str, top_k: int = 3, debug: bool = False):
        self.last_question = question
        return {"answer": "ok", "sources": ["s.md"], "results": []}


class StubStore:
    def latest(self, session_id: str, limit: int = 6):
        return [
            {"role": "user", "content": "有优惠吗？", "meta": {}},
            {"role": "assistant", "content": "满50减5", "meta": {}},
        ]


def test_recent_context_included_in_prompt():
    pipeline = CapturePipeline()
    agent = AgentOrchestrator(pipeline=pipeline, store=StubStore())
    agent.chat(session_id="s1", question="那今天还能用吗？")
    assert "有优惠吗" in pipeline.last_question
    assert "那今天还能用吗" in pipeline.last_question
```

**Step 2: Run test to verify it fails**

Run: `cd rag-mvp && pytest tests/test_orchestrator_memory.py -v`  
Expected: FAIL because orchestrator does not inject recent context yet.

**Step 3: Write minimal implementation**

```python
def _build_context(messages):
    return "\\n".join(f"{m['role']}: {m['content']}" for m in reversed(messages))


# In orchestrator.chat():
# history = store.latest(session_id, limit=6)
# enriched_question = f"{_build_context(history)}\\nuser: {question}" if history else question
# pipeline.query(enriched_question, top_k=3, debug=False)
```

**Step 4: Run test to verify it passes**

Run: `cd rag-mvp && pytest tests/test_orchestrator_memory.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git -C rag-mvp add src/agent/orchestrator.py src/agent/conversation_store.py tests/test_orchestrator_memory.py
git -C rag-mvp commit -m "feat(agent): add short session memory support"
```

### Task 8: Add minimal analytics metrics endpoint

**Files:**
- Create: `rag-mvp/src/agent/metrics.py`
- Modify: `rag-mvp/api.py`
- Create: `rag-mvp/tests/test_metrics.py`

**Step 1: Write the failing test**

```python
from src.agent.metrics import aggregate_metrics


def test_metrics_aggregate():
    rows = [
        {"latency_ms": 1000, "handoff": False, "answered": True},
        {"latency_ms": 2000, "handoff": True, "answered": True},
        {"latency_ms": 3000, "handoff": False, "answered": False},
        {"latency_ms": 4000, "handoff": False, "answered": True},
    ]
    m = aggregate_metrics(rows)
    assert m["response_time_p95"] == 4000
    assert m["handoff_rate"] == 0.25
    assert m["answered_rate"] == 0.75
```

**Step 2: Run test to verify it fails**

Run: `cd rag-mvp && pytest tests/test_metrics.py -v`  
Expected: FAIL because `aggregate_metrics` is missing.

**Step 3: Write minimal implementation**

```python
def aggregate_metrics(rows):
    if not rows:
        return {"response_time_p95": 0, "handoff_rate": 0.0, "answered_rate": 0.0}
    latencies = sorted(int(r["latency_ms"]) for r in rows)
    p95_idx = min(len(latencies) - 1, int(len(latencies) * 0.95))
    handoff_rate = sum(1 for r in rows if r["handoff"]) / len(rows)
    answered_rate = sum(1 for r in rows if r["answered"]) / len(rows)
    return {
        "response_time_p95": latencies[p95_idx],
        "handoff_rate": round(handoff_rate, 2),
        "answered_rate": round(answered_rate, 2),
    }
```

**Step 4: Run test to verify it passes**

Run: `cd rag-mvp && pytest tests/test_metrics.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git -C rag-mvp add src/agent/metrics.py api.py tests/test_metrics.py
git -C rag-mvp commit -m "feat(agent): add basic metrics aggregation endpoint"
```

### Task 9: Full verification and docs update

**Files:**
- Modify: `rag-mvp/README.md`

**Step 1: Run full test suite**

Run: `cd rag-mvp && pytest -v`  
Expected: PASS for all old and new tests.

**Step 2: Run API smoke tests**

Run:

```bash
cd rag-mvp
uvicorn api:app --reload
curl http://127.0.0.1:8000/health
```

Expected: `{"status":"ok"}`.

**Step 3: Update docs**

Add API quickstart and sample payload for `/chat` and `/handoff`.

**Step 4: Commit**

```bash
git -C rag-mvp add README.md
git -C rag-mvp commit -m "docs: add merchant agent api usage and verification notes"
```
