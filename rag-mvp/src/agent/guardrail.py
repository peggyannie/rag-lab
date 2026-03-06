"""AG-003: 风险拦截与转人工。"""

from src.agent.models import AgentResponse


# 敏感词：命中任一则转人工，不交大模型回答
RISK_KEYWORDS = ["投诉", "退款", "举报"]

HANDOFF_MESSAGE = "您的问题需要人工客服处理，正在为您转接。"


def check_risk(text: str) -> AgentResponse:
    """
    判断文本是否含风险关键词；若有则返回转人工响应，否则返回无风险响应。

    Args:
        text: 用户输入文本（如单轮问题）

    Returns:
        AgentResponse: 命中风险词时 risk_flag=True、handoff=True、answer 为转人工提示；
                       否则 risk_flag=False、handoff=False、answer 为空。
    """
    if not text or not text.strip():
        return AgentResponse(risk_flag=False, handoff=False, answer="", sources=[])

    for keyword in RISK_KEYWORDS:
        if keyword in text:
            return AgentResponse(
                answer=HANDOFF_MESSAGE,
                sources=[],
                risk_flag=True,
                handoff=True,
            )

    return AgentResponse(risk_flag=False, handoff=False, answer="", sources=[])
