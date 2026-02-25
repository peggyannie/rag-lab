from __future__ import annotations

import os
from typing import Dict, List, Sequence

from openai import OpenAI

from src.generator import build_prompt


class OpenAIProvider:
    MAX_EMBED_BATCH_SIZE = 64

    def __init__(
        self,
        *,
        client: OpenAI | None = None,
        embedding_model: str | None = None,
        chat_model: str | None = None,
    ) -> None:
        self.embedding_model = embedding_model or os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
        self.chat_model = chat_model or os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

        if client is not None:
            self.client = client
            return

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when provider=openai")

        base_url = os.getenv("OPENAI_BASE_URL")
        kwargs: Dict[str, str] = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = OpenAI(**kwargs)

    def embed_texts(self, texts: Sequence[str]) -> List[List[float]]:
        if not texts:
            return []
        vectors: List[List[float]] = []
        payload = list(texts)
        for i in range(0, len(payload), self.MAX_EMBED_BATCH_SIZE):
            batch = payload[i : i + self.MAX_EMBED_BATCH_SIZE]
            response = self.client.embeddings.create(model=self.embedding_model, input=batch)
            vectors.extend([list(item.embedding) for item in response.data])
        return vectors

    def embed_query(self, question: str) -> List[float]:
        vectors = self.embed_texts([question])
        return vectors[0] if vectors else []

    def generate_answer(self, question: str, contexts: List[Dict[str, object]]) -> str:
        prompt = build_prompt(question, contexts)
        response = self.client.chat.completions.create(
            model=self.chat_model,
            messages=[
                {"role": "system", "content": "你是一个知识库助手，请严格依据参考资料作答。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
        return response.choices[0].message.content or ""
