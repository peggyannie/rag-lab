"""AG-004: 编排层基线——统一路由风险与普通问答。"""

from typing import Any, Dict

from src.agent.guardrail import check_risk
from src.agent.models import AgentResponse


def run(question: str, pipeline: Any) -> AgentResponse:
    """
    单轮路由：风险问题走 guardrail 转人工；普通问题走 RAG pipeline 组装响应。

    Args:
        question: 用户输入问题。
        pipeline: 具备 query(question) -> Dict["answer", "sources", ...] 的 RAG 管道（如 RagPipeline）。

    Returns:
        AgentResponse: 转人工时含 risk_flag=True、handoff=True；否则为 RAG 回答与 sources。
    """
    guard = check_risk(question)
    if guard.handoff:
        return guard

    result: Dict[str, Any] = pipeline.query(question)
    answer = result.get("answer", "")
    sources = result.get("sources", [])
    if isinstance(sources, list):
        sources = list(sources)
    else:
        sources = []

    return AgentResponse(
        answer=answer,
        sources=sources,
        risk_flag=False,
        handoff=False,
    )
