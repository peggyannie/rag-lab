"""AG-002: 问答协议模型测试（TDD - 先写失败测试）。"""

from src.agent.models import AgentResponse


class TestAgentResponse:
    """AgentResponse 协议模型测试集。"""

    def test_default_values(self):
        """默认值：answer='', sources=[], risk_flag=False, handoff=False。"""
        resp = AgentResponse()
        assert resp.answer == ""
        assert resp.sources == []
        assert resp.risk_flag is False
        assert resp.handoff is False

    def test_custom_values(self):
        """传入自定义参数后正确赋值。"""
        resp = AgentResponse(
            answer="配送范围是 3 公里",
            sources=["merchant.md"],
            risk_flag=True,
            handoff=True,
        )
        assert resp.answer == "配送范围是 3 公里"
        assert resp.sources == ["merchant.md"]
        assert resp.risk_flag is True
        assert resp.handoff is True

    def test_to_dict_serialization(self):
        """to_dict() 返回正确 dict，包含全部 4 个协议字段。"""
        resp = AgentResponse(answer="ok", sources=["a.md"])
        d = resp.to_dict()
        assert d == {
            "answer": "ok",
            "sources": ["a.md"],
            "risk_flag": False,
            "handoff": False,
        }

    def test_from_dict_deserialization(self):
        """from_dict() 能从 dict 构造对象。"""
        data = {
            "answer": "已转人工",
            "sources": [],
            "risk_flag": True,
            "handoff": True,
        }
        resp = AgentResponse.from_dict(data)
        assert resp.answer == "已转人工"
        assert resp.risk_flag is True
        assert resp.handoff is True

    def test_roundtrip_serialization(self):
        """from_dict(to_dict()) 与原对象字段一致。"""
        original = AgentResponse(
            answer="测试回答",
            sources=["doc1.md", "doc2.md"],
            risk_flag=False,
            handoff=False,
        )
        restored = AgentResponse.from_dict(original.to_dict())
        assert restored.answer == original.answer
        assert restored.sources == original.sources
        assert restored.risk_flag == original.risk_flag
        assert restored.handoff == original.handoff

    def test_risk_flag_and_handoff_contract(self):
        """risk_flag=True 时可设 handoff=True，协议允许联动。"""
        resp = AgentResponse(risk_flag=True, handoff=True)
        assert resp.risk_flag is True
        assert resp.handoff is True
        d = resp.to_dict()
        assert d["risk_flag"] is True
        assert d["handoff"] is True
