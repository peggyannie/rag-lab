from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from multi_lab.config import load_settings
from multi_lab.rag_store import JsonVectorStore, make_id


NOT_FOUND = "知识库中未找到相关内容"


def _chunks(text: str, chunk_size: int = 700, overlap: int = 80) -> List[str]:
    if not text:
        return []
    step = max(1, chunk_size - overlap)
    out = []
    for start in range(0, len(text), step):
        chunk = text[start : start + chunk_size]
        if chunk:
            out.append(chunk)
    return out


class RagToolkit:
    def __init__(self, base_dir: str | Path) -> None:
        self.settings = load_settings(base_dir=base_dir)
        self.store = JsonVectorStore(self.settings.db_path)

    def ingest(self, data_path: str) -> Dict[str, int]:
        root = Path(data_path)
        files = [root] if root.is_file() else sorted(root.rglob("*"))
        prepared: List[Dict[str, object]] = []
        docs = 0
        for file in files:
            if not file.is_file() or file.suffix.lower() not in {".md", ".txt"}:
                continue
            docs += 1
            text = file.read_text(encoding="utf-8")
            for idx, chunk in enumerate(_chunks(text)):
                prepared.append(
                    {
                        "id": make_id(file.name, idx, chunk),
                        "source": file.name,
                        "chunk_index": idx,
                        "text": chunk,
                    }
                )
        added = self.store.add(prepared)
        return {"documents": docs, "chunks": len(prepared), "added": added}

    def retrieve(self, question: str, top_k: int = 3) -> List[Dict[str, object]]:
        return self.store.query(question, top_k=top_k)

    def answer(self, question: str, top_k: int = 3) -> str:
        hits = self.retrieve(question, top_k=top_k)
        if not hits or all(float(h["score"]) <= 0 for h in hits):
            return NOT_FOUND
        best = hits[0]
        return f"根据 {best['source']}：{best['text']}"

    def stats(self) -> Dict[str, int]:
        return {"chunks": self.store.count()}
