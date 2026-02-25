from __future__ import annotations

from src.store import LocalVectorStore


class Retriever:
    def __init__(self, store: LocalVectorStore) -> None:
        self.store = store

    def search(self, question: str, top_k: int = 3):
        return self.store.query(question, top_k=top_k)
