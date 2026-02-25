from __future__ import annotations

import os
from pathlib import Path
import re
from typing import Dict, List

from src.config import load_settings
from src.generator import NOT_FOUND_TEXT, build_prompt, local_generate
from src.loader import chunk_text, load_documents
from src.openai_provider import OpenAIProvider
from src.openai_store import OpenAIChromaStore
from src.retriever import Retriever
from src.store import LocalVectorStore, make_chunk_id


class RagPipeline:
    def __init__(self, base_dir: str | Path | None = None, provider: str | None = None) -> None:
        self.settings = load_settings(base_dir=base_dir, provider=provider)
        self.provider = self.settings.provider
        self.score_threshold = float(os.getenv("RAG_SCORE_THRESHOLD", "0.42"))
        self.rerank_limit = max(1, int(os.getenv("RAG_RERANK_LIMIT", "4")))
        self.openai_provider: OpenAIProvider | None = None

        if self.provider == "openai":
            self.store = OpenAIChromaStore(self.settings.chroma_dir)
            self.retriever = None
            self.openai_provider = OpenAIProvider()
        else:
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
        self.store.clear()
        if self.provider == "openai":
            assert self.openai_provider is not None
            embeddings = self.openai_provider.embed_texts([str(row["text"]) for row in prepared])
            added = self.store.add(prepared, embeddings)
        else:
            added = self.store.add(prepared)
        return {"documents": len(docs), "chunks": len(prepared), "added": added}

    def query(self, question: str, top_k: int = 3, debug: bool = False) -> Dict[str, object]:
        if self.provider == "openai":
            assert self.openai_provider is not None
            qvec = self.openai_provider.embed_query(question)
            hits = self.store.query_by_embedding(qvec, top_k=max(top_k, self.rerank_limit))
            hits = self._filter_and_rerank_hits(question, hits, top_k=top_k)
            if not hits or all(float(hit["score"]) <= 0 for hit in hits):
                answer = NOT_FOUND_TEXT
            else:
                answer = self.openai_provider.generate_answer(question, hits)
                if not answer.strip():
                    answer = NOT_FOUND_TEXT
        else:
            assert self.retriever is not None
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

    @staticmethod
    def _tokenize_for_rerank(text: str) -> set[str]:
        lowered = text.lower()
        latin = set(re.findall(r"[a-z0-9_]+", lowered))
        cjk_grams: set[str] = set()
        for span in re.findall(r"[\u4e00-\u9fff]+", lowered):
            if len(span) == 1:
                cjk_grams.add(span)
                continue
            for n in (2, 3):
                if len(span) < n:
                    continue
                for i in range(len(span) - n + 1):
                    cjk_grams.add(span[i : i + n])
        return latin | cjk_grams

    def _filter_and_rerank_hits(self, question: str, hits: List[Dict[str, object]], top_k: int) -> List[Dict[str, object]]:
        filtered = [hit for hit in hits if float(hit.get("score", 0.0)) >= self.score_threshold]
        if not filtered:
            return []

        q_tokens = self._tokenize_for_rerank(question)

        def sort_key(hit: Dict[str, object]):
            text_tokens = self._tokenize_for_rerank(str(hit.get("text", "")))
            overlap = len(q_tokens & text_tokens)
            return (overlap, float(hit.get("score", 0.0)))

        reranked = sorted(filtered, key=sort_key, reverse=True)
        return reranked[: min(top_k, self.rerank_limit)]
