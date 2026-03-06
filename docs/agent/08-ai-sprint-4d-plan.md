# AI Sprint Plan (4 Days, P0 First Version)

## 1. Scope
- Target: P0 first version for merchant customer-service agent.
- Backlog in scope: `AG-001` to `AG-005`.
- Out of scope: `AG-101+` (memory, growth strategy, metrics enhancement).

## 2. Team Model
- Agent A (Core): domain model, guardrail, orchestrator.
- Agent B (Infra): template validation, API, test harness, docs sync.
- Human owner: acceptance decisions, risk policy confirmation, merge gate.

## 3. Global Rules
- TDD first for every task.
- One PR per task or tightly-coupled pair of tasks.
- Every merge requires:
  - Target tests pass
  - `pytest -v` pass
  - verification checklist updated

## 4. Day-by-Day Plan

### Day 1 (Foundation)
- Agent A:
  - Implement `AG-002` chat protocol model.
  - Add tests for default fields and serialization.
- Agent B:
  - Implement `AG-001` merchant template + validator.
  - Add tests for missing required sections.
- Merge checkpoint:
  - Merge only when both task tests pass and no regression in `test_pipeline.py`.
- Required commands:
```bash
cd rag-mvp
pytest tests/test_agent_models.py -v
pytest tests/test_template_validator.py -v
pytest tests/test_pipeline.py -v
```
- Exit criteria:
  - `answer/sources/risk_flag/handoff` contract finalized.
  - Template validation errors are deterministic and machine-readable.

### Day 2 (Safety + Routing)
- Agent A:
  - Implement `AG-003` risk detection and handoff routing rules.
  - Add keyword-driven tests, including negative cases.
- Agent B:
  - Implement `AG-004` orchestrator baseline:
    - risky question -> handoff
    - normal question -> pipeline query
  - Add tests with pipeline stub.
- Merge checkpoint:
  - Human checks risk policy examples before merge.
- Required commands:
```bash
cd rag-mvp
pytest tests/test_guardrail.py -v
pytest tests/test_orchestrator.py -v
pytest tests/test_cli.py -v
pytest -v
```
- Exit criteria:
  - Sensitive questions never auto-answer.
  - Single-turn chat chain runs end-to-end.

### Day 3 (API Closure)
- Agent A:
  - Build `api.py` endpoints: `/health`, `/chat`, `/handoff`.
  - Wire orchestrator dependency into API layer.
- Agent B:
  - Add API contract tests and error-path tests.
  - Update dependency config (`fastapi`, `uvicorn`) and README API section.
- Merge checkpoint:
  - API schema and status code contract reviewed by human.
- Required commands:
```bash
cd rag-mvp
pytest tests/test_api.py -v
pytest tests/test_pipeline.py -v
pytest tests/test_cli.py -v
pytest -v
```
- Exit criteria:
  - API minimal closure is available and testable.
  - Request/response fields match agent contract.

### Day 4 (Hardening + Release Candidate)
- Agent A:
  - Stabilize edge cases: empty sources, unknown question fallback, handoff message consistency.
  - Fix any failing regression tests.
- Agent B:
  - Run full verification checklist.
  - Finalize runbook and prompt-pack alignment.
  - Prepare release note (what is in/out for V1).
- Merge checkpoint:
  - Only one release branch merge at end of day.
- Required commands:
```bash
cd rag-mvp
pytest -v
python cli.py --ingest data
python cli.py --query "配送范围是什么？" --debug
```
- Exit criteria:
  - All tests pass.
  - Functional smoke checks pass.
  - Docs (`docs/agent` + README) are aligned with shipped behavior.

## 5. Risk Buffer (Built-in)
- Reserve 20% daily capacity for:
  - flaky tests
  - dependency mismatch
  - API contract adjustment

## 6. Definition of “V1 Done”
- `AG-001` to `AG-005` completed and merged.
- Verification checklist passes.
- Can run one full flow:
  - ingest -> chat API query -> risk handoff path -> source-backed response.

## 7. If Delayed (Fallback Cuts)
- Keep: `AG-001`, `AG-002`, `AG-003`, `/health`, `/chat`.
- Defer: `/handoff` endpoint richness and non-critical API error formatting.
- Never cut: risk handoff behavior and test gates.
