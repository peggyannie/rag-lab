from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import chromadb


class OpenAIChromaStore:
    def __init__(self, db_dir: str | Path, collection_name: str = "rag_chunks") -> None:
        self.db_dir = Path(db_dir)
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.db_dir))
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add(self, chunks: List[Dict[str, object]], embeddings: List[List[float]]) -> int:
        if not chunks:
            return 0

        ids = [str(chunk["id"]) for chunk in chunks]
        existing = self.collection.get(ids=ids)
        existing_ids = set(existing.get("ids", []))

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=[str(chunk["text"]) for chunk in chunks],
            metadatas=[
                {
                    "source": str(chunk["source"]),
                    "chunk_index": int(chunk["chunk_index"]),
                }
                for chunk in chunks
            ],
        )
        return sum(1 for chunk_id in ids if chunk_id not in existing_ids)

    def count(self) -> int:
        return int(self.collection.count())

    def clear(self) -> None:
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(name=self.collection.name)

    def query_by_embedding(self, query_embedding: List[float], top_k: int = 3) -> List[Dict[str, object]]:
        if not query_embedding:
            return []

        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        ids = result.get("ids", [[]])[0]
        docs = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        rows: List[Dict[str, object]] = []
        for idx, chunk_id in enumerate(ids):
            metadata = metadatas[idx] or {}
            distance = float(distances[idx]) if idx < len(distances) else 1.0
            rows.append(
                {
                    "id": chunk_id,
                    "text": docs[idx] if idx < len(docs) else "",
                    "source": metadata.get("source", ""),
                    "chunk_index": int(metadata.get("chunk_index", idx)),
                    "score": 1.0 / (1.0 + max(distance, 0.0)),
                }
            )
        return rows
