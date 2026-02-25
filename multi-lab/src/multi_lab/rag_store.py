from __future__ import annotations

from pathlib import Path
import hashlib
import json
import math
import re
from typing import Dict, List


TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in TOKEN_RE.findall(text)]


def vectorize(text: str) -> Dict[str, float]:
    vec: Dict[str, float] = {}
    for token in tokenize(text):
        vec[token] = vec.get(token, 0.0) + 1.0
    return vec


def cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(v * b.get(k, 0.0) for k, v in a.items())
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def make_id(source: str, chunk_index: int, text: str) -> str:
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]
    return f"{source}#{chunk_index}#{digest}"


class JsonVectorStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.rows: Dict[str, Dict[str, object]] = {}
        if self.db_path.exists():
            loaded = json.loads(self.db_path.read_text(encoding="utf-8"))
            self.rows = {row["id"]: row for row in loaded}

    def _save(self) -> None:
        self.db_path.write_text(json.dumps(list(self.rows.values()), ensure_ascii=False, indent=2), encoding="utf-8")

    def add(self, chunks: List[Dict[str, object]]) -> int:
        added = 0
        for chunk in chunks:
            cid = str(chunk["id"])
            if cid in self.rows:
                continue
            text = str(chunk["text"])
            self.rows[cid] = {
                "id": cid,
                "text": text,
                "source": str(chunk["source"]),
                "chunk_index": int(chunk["chunk_index"]),
                "vector": vectorize(text),
            }
            added += 1
        self._save()
        return added

    def query(self, question: str, top_k: int = 3) -> List[Dict[str, object]]:
        qv = vectorize(question)
        out: List[Dict[str, object]] = []
        for row in self.rows.values():
            out.append(
                {
                    "id": row["id"],
                    "text": row["text"],
                    "source": row["source"],
                    "chunk_index": row["chunk_index"],
                    "score": cosine(qv, row["vector"]),
                }
            )
        out.sort(key=lambda r: float(r["score"]), reverse=True)
        return out[:top_k]

    def count(self) -> int:
        return len(self.rows)
