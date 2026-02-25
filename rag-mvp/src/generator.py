from __future__ import annotations

from typing import Dict, List


NOT_FOUND_TEXT = "知识库中未找到相关内容"


def build_prompt(question: str, contexts: List[Dict[str, object]]) -> str:
    if not contexts:
        return f"用户问题: {question}\n\n参考资料为空。"

    lines = []
    for idx, ctx in enumerate(contexts, start=1):
        lines.append(f"[{idx}] ({ctx['source']}) {ctx['text']}")

    return (
        "你是一个知识库助手，请依据参考资料作答。\n"
        + "\n".join(lines)
        + f"\n\n用户问题: {question}\n回答:"
    )


def local_generate(question: str, contexts: List[Dict[str, object]]) -> str:
    if not contexts or all(float(c["score"]) <= 0 for c in contexts):
        return NOT_FOUND_TEXT
    best = contexts[0]
    return f"根据 {best['source']}：{best['text']}"
