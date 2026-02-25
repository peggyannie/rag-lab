from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from src.config import load_settings
from src.generator import NOT_FOUND_TEXT, build_prompt, local_generate
from src.loader import chunk_text, load_documents
from src.retriever import Retriever
from src.store import LocalVectorStore, make_chunk_id


class RagPipeline:
    def __init__(self, base_dir: str | Path | None = None, provider: str | None = None) -> None:
        self.settings = load_settings(base_dir=base_dir, provider=provider)
        self.provider = self.settings.provider
        self.store = LocalVectorStore(self.settings.db_path)
        self.retriever = Retriever(self.store)

    def ingest(self, input_path: str | Path, chunk_size: int = 700, chunk_overlap: int = 80) -> Dict[str, int]:
        docs = load_documents(input_path)
        prepared: List[Dict[str, object]] = []
        for doc in docs:
            chunks = chunk_text(doc["text"], chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            for chunk in chunks:
                chunk_id = make_chunk_id(doc["source"], int(chunk["chunk_index"]), chunk["text"])
                prepared.append(
                    {
                        "id": chunk_id,
                        "text": chunk["text"],
                        "source": doc["source"],
                        "chunk_index": chunk["chunk_index"],
                    }
                )
        added = self.store.add(prepared)
        return {"documents": len(docs), "chunks": len(prepared), "added": added}

    def query(self, question: str, top_k: int = 3, debug: bool = False) -> Dict[str, object]:
        hits = self.retriever.search(question, top_k=top_k)
        answer = local_generate(question, hits)
        prompt = build_prompt(question, hits)
        sources = sorted({str(hit["source"]) for hit in hits if float(hit["score"]) > 0})
        if answer == NOT_FOUND_TEXT:
            sources = []
        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "results": hits,
            "prompt": prompt if debug else "",
        }

    def stats(self) -> Dict[str, int]:
        return {"chunks": self.store.count()}
