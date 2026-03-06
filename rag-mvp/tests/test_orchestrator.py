"""AG-004: 编排层基线测试（TDD - 先写失败测试，stub pipeline 隔离）。"""

from src.agent.models import AgentResponse
from src.agent.orchestrator import run as orchestrator_run


class StubPipeline:
    """Stub：仅返回预设 answer/sources，不访问真实 RAG。"""

    def __init__(self, answer: str = "默认回答", sources=None):
        self.answer = answer
        self.sources = sources if sources is not None else []

    def query(self, question: str, **_kwargs):
        return {"answer": self.answer, "sources": self.sources}


class TestOrchestrator:
    """编排层路由与组装 AgentResponse 测试集。"""

    def test_risky_question_returns_handoff_without_calling_pipeline(self):
        """风险问题走 guardrail，返回转人工响应，且不调用 pipeline。"""
        call_count = 0

        def track_query(question, **_):
            nonlocal call_count
            call_count += 1
            return {"answer": "不应被调用", "sources": []}

        stub = StubPipeline()
        stub.query = track_query
        resp = orchestrator_run("我要投诉", stub)
        assert resp.handoff is True
        assert resp.risk_flag is True
        assert resp.answer != ""
        assert call_count == 0, "风险问题不得调用 pipeline"

    def test_normal_question_calls_pipeline_and_returns_agent_response(self):
        """普通问题调用 pipeline，组装为标准 AgentResponse。"""
        stub = StubPipeline(answer="配送范围 3 公里", sources=["merchant.md"])
        resp = orchestrator_run("配送范围多少？", stub)
        assert resp.handoff is False
        assert resp.risk_flag is False
        assert resp.answer == "配送范围 3 公里"
        assert resp.sources == ["merchant.md"]

    def test_refund_keyword_routes_to_handoff(self):
        """「退款」类问题走转人工。"""
        stub = StubPipeline(answer="不应使用", sources=[])
        resp = orchestrator_run("怎么申请退款", stub)
        assert resp.handoff is True
        assert resp.risk_flag is True

    def test_single_round_e2e_normal(self):
        """单轮链路：普通问题 -> pipeline -> AgentResponse 字段完整。"""
        stub = StubPipeline(answer="营业时间 9-21 点", sources=["store.md"])
        resp = orchestrator_run("营业时间？", stub)
        assert isinstance(resp, AgentResponse)
        assert resp.answer == "营业时间 9-21 点"
        assert resp.sources == ["store.md"]
        assert resp.to_dict()["answer"] == resp.answer
        assert resp.to_dict()["handoff"] is False
