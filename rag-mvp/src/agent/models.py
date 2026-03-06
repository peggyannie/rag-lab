"""AG-002: 问答协议模型"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class AgentResponse:
    """
    统一问答协议模型，处理 answer/sources/risk_flag/handoff 契约。
    """
    answer: str = ""
    sources: List[str] = field(default_factory=list)
    risk_flag: bool = False
    handoff: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典。"""
        return {
            "answer": self.answer,
            "sources": self.sources,
            "risk_flag": self.risk_flag,
            "handoff": self.handoff
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentResponse":
        """从字典反序列化生成协议对象。"""
        return cls(
            answer=data.get("answer", ""),
            sources=data.get("sources", []),
            risk_flag=data.get("risk_flag", False),
            handoff=data.get("handoff", False)
        )
