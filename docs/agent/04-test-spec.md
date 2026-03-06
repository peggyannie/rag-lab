# 测试规范（AI Agent 执行版）

## 1. 测试分层
- 单元测试：函数/类行为与边界。
- 集成测试：编排层与 pipeline 交互。
- 回归测试：现有 `pipeline/cli` 关键路径。

## 2. 必跑测试（每次 PR）
```bash
cd rag-mvp
pytest tests/test_pipeline.py -v
pytest tests/test_cli.py -v
pytest -v
```

## 3. 新增模块对应测试
- `src/agent/models.py` -> `tests/test_agent_models.py`
- `src/agent/guardrail.py` -> `tests/test_guardrail.py`
- `src/agent/orchestrator.py` -> `tests/test_orchestrator.py`
- `src/agent/conversation_store.py` -> `tests/test_conversation_store.py`
- `api.py` -> `tests/test_api.py`

## 4. 覆盖重点
- 风险词触发逻辑与误判场景。
- 无检索结果时的兜底输出。
- 来源字段一致性。
- session 维度消息读取顺序。

## 5. 失败处理规则
- 先复现后修复，不允许盲改。
- 每次只修一个失败根因，修后立刻复跑。
- 若是 flaky test，必须记录重现条件和临时规避方案。
