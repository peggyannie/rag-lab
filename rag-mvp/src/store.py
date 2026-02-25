from __future__ import annotations

from pathlib import Path
import hashlib
import json
import math
import re
from typing import Dict, List


TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def _tokenize(text: str) -> List[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def _vectorize(text: str) -> Dict[str, float]:
    vec: Dict[str, float] = {}
    for token in _tokenize(text):
        vec[token] = vec.get(token, 0.0) + 1.0
    return vec


def _cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(v * b.get(k, 0.0) for k, v in a.items())
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def make_chunk_id(source: str, chunk_index: int, text: str) -> str:
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]
    return f"{source}#{chunk_index}#{digest}"


class LocalVectorStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.rows: Dict[str, Dict[str, object]] = {}
        if self.db_path.exists():
            raw = json.loads(self.db_path.read_text(encoding="utf-8"))
            self.rows = {row["id"]: row for row in raw}

    def _persist(self) -> None:
        self.db_path.write_text(
            json.dumps(list(self.rows.values()), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add(self, chunks: List[Dict[str, object]]) -> int:
        added = 0
        for chunk in chunks:
            chunk_id = str(chunk["id"])
            if chunk_id in self.rows:
                continue
            text = str(chunk["text"])
            self.rows[chunk_id] = {
                "id": chunk_id,
                "text": text,
                "source": str(chunk["source"]),
                "chunk_index": int(chunk["chunk_index"]),
                "vector": _vectorize(text),
            }
            added += 1
        self._persist()
        return added

    def count(self) -> int:
        return len(self.rows)

    def query(self, question: str, top_k: int = 3) -> List[Dict[str, object]]:
        qvec = _vectorize(question)
        scored: List[Dict[str, object]] = []
        for row in self.rows.values():
            score = _cosine(qvec, row["vector"])
            scored.append(
                {
                    "id": row["id"],
                    "text": row["text"],
                    "source": row["source"],
                    "chunk_index": row["chunk_index"],
                    "score": score,
                }
            )
        scored.sort(key=lambda item: float(item["score"]), reverse=True)
        return scored[:top_k]
