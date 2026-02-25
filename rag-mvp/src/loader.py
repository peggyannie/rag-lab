from __future__ import annotations

from pathlib import Path
from typing import Dict, List


def load_documents(path: str | Path) -> List[Dict[str, str]]:
    source_path = Path(path)
    files = [source_path] if source_path.is_file() else sorted(source_path.rglob("*"))
    docs: List[Dict[str, str]] = []

    for file_path in files:
        if not file_path.is_file() or file_path.suffix.lower() not in {".md", ".txt"}:
            continue
        docs.append({"source": file_path.name, "text": file_path.read_text(encoding="utf-8")})
    return docs


def chunk_text(text: str, chunk_size: int = 700, chunk_overlap: int = 80) -> List[Dict[str, str]]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be in [0, chunk_size)")

    chunks: List[Dict[str, str]] = []
    step = chunk_size - chunk_overlap
    for idx, start in enumerate(range(0, len(text), step)):
        chunk = text[start : start + chunk_size]
        if not chunk:
            continue
        chunks.append({"chunk_index": idx, "text": chunk})
    return chunks
