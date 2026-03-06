"""AG-005: API 最小闭环契约与错误路径测试（TDD）。"""

import pytest
from fastapi.testclient import TestClient

from src.api import create_app


class StubPipeline:
    """Stub pipeline 供 API 测试隔离。"""

    def __init__(self, answer: str = "默认回答", sources=None):
        self.answer = answer
        self.sources = sources if sources is not None else []

    def query(self, question: str, **_kwargs):
        return {"answer": self.answer, "sources": self.sources}


@pytest.fixture
def client():
    """使用 stub pipeline 的 TestClient。"""
    app = create_app()
    app.state.pipeline = StubPipeline(answer="配送范围 3 公里", sources=["merchant.md"])
    return TestClient(app)


def test_health_returns_200_and_ok(client: TestClient):
    """GET /health 返回 200，body 含 status=ok。"""
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json().get("status") == "ok"


def test_chat_returns_agent_contract_fields(client: TestClient):
    """POST /chat 返回 200，body 含协议四字段 answer/sources/risk_flag/handoff。"""
    res = client.post("/chat", json={"question": "配送范围多少？"})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "sources" in data
    assert "risk_flag" in data
    assert "handoff" in data
    assert data["answer"] == "配送范围 3 公里"
    assert data["sources"] == ["merchant.md"]
    assert data["risk_flag"] is False
    assert data["handoff"] is False


def test_chat_risk_question_returns_handoff_true(client: TestClient):
    """风险问题 POST /chat 返回 handoff=true、risk_flag=true。"""
    res = client.post("/chat", json={"question": "我要投诉"})
    assert res.status_code == 200
    data = res.json()
    assert data["handoff"] is True
    assert data["risk_flag"] is True
    assert data["answer"] != ""


def test_handoff_returns_200(client: TestClient):
    """GET /handoff 返回 200，body 含 handoff 相关字段。"""
    res = client.get("/handoff")
    assert res.status_code == 200
    data = res.json()
    assert "handoff" in data


def test_chat_missing_question_returns_422(client: TestClient):
    """POST /chat 缺少 question 时返回 422。"""
    res = client.post("/chat", json={})
    assert res.status_code == 422


def test_chat_unknown_question_returns_empty_sources_and_fallback_answer():
    """未知问题：pipeline 返回无来源时，响应仍含四字段、sources 为空。"""
    from src.generator import NOT_FOUND_TEXT
    app = create_app()
    app.state.pipeline = StubPipeline(answer=NOT_FOUND_TEXT, sources=[])
    client = TestClient(app)
    res = client.post("/chat", json={"question": "量子物理是什么？"})
    assert res.status_code == 200
    data = res.json()
    assert data["sources"] == []
    assert data["handoff"] is False
    assert NOT_FOUND_TEXT in data["answer"]
