"""AG-003: 风险拦截与转人工测试（TDD - 先写失败测试）。"""

import pytest

from src.agent.models import AgentResponse
from src.agent.guardrail import check_risk


class TestGuardrail:
    """风险关键词检测与转人工响应测试集。"""

    def test_contains_complaint_keyword_returns_risk_and_handoff(self):
        """文本含「投诉」时返回 risk_flag=True、handoff=True。"""
        resp = check_risk("我要投诉你们配送太慢")
        assert isinstance(resp, AgentResponse)
        assert resp.risk_flag is True
        assert resp.handoff is True
        assert resp.answer != ""

    def test_contains_refund_keyword_returns_risk_and_handoff(self):
        """文本含「退款」时返回 risk_flag=True、handoff=True。"""
        resp = check_risk("申请退款")
        assert resp.risk_flag is True
        assert resp.handoff is True
        assert resp.answer != ""

    def test_contains_other_risk_keyword_returns_risk_and_handoff(self):
        """文本含其他约定风险词（如「举报」）时同样转人工。"""
        resp = check_risk("我要举报商家")
        assert resp.risk_flag is True
        assert resp.handoff is True

    def test_normal_question_returns_no_risk_no_handoff(self):
        """普通问题不含风险词时 risk_flag=False、handoff=False。"""
        resp = check_risk("你们的配送范围是多少？")
        assert resp.risk_flag is False
        assert resp.handoff is False
        assert resp.answer == ""
        assert resp.sources == []

    def test_empty_text_returns_no_risk(self):
        """空字符串不视为风险。"""
        resp = check_risk("")
        assert resp.risk_flag is False
        assert resp.handoff is False

    def test_partial_match_keyword_returns_risk(self):
        """子串命中风险词也视为风险（如「退款」在「我要退款」）。"""
        resp = check_risk("请问如何申请退款？")
        assert resp.risk_flag is True
        assert resp.handoff is True
