from __future__ import annotations

from typing import Dict, List


def format_results_for_display(results: List[Dict[str, object]], preview_chars: int = 140) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for idx, item in enumerate(results, start=1):
        text = str(item.get("text", "")).replace("\n", " ").strip()
        if len(text) > preview_chars:
            text = text[:preview_chars].rstrip() + "..."
        rows.append(
            {
                "rank": idx,
                "source": str(item.get("source", "")),
                "score": round(float(item.get("score", 0.0)), 4),
                "preview": text,
            }
        )
    return rows
