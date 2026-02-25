from pathlib import Path

import src.pipeline as pipeline_module
from src.pipeline import RagPipeline


class _FakeOpenAIProvider:
    def __init__(self, *args, **kwargs) -> None:
        self.embed_text_calls = []
        self.embed_query_calls = []
        self.generate_calls = []

    def embed_texts(self, texts):
        self.embed_text_calls.append(texts)
        return [[0.1, 0.2] for _ in texts]

    def embed_query(self, question):
        self.embed_query_calls.append(question)
        return [0.7, 0.3]

    def generate_answer(self, question, contexts):
        self.generate_calls.append((question, contexts))
        return "openai generated answer"


class _FakeOpenAIChromaStore:
    def __init__(self, *args, **kwargs) -> None:
        self.rows = []
        self.cleared = False

    def add(self, chunks, embeddings):
        for chunk, embedding in zip(chunks, embeddings):
            self.rows.append(
                {
                    "id": chunk["id"],
                    "text": chunk["text"],
                    "source": chunk["source"],
                    "chunk_index": chunk["chunk_index"],
                    "score": 0.91,
                    "embedding": embedding,
                }
            )
        return len(chunks)

    def clear(self):
        self.cleared = True
        self.rows = []

    def count(self):
        return len(self.rows)

    def query_by_embedding(self, query_embedding, top_k=3):
        _ = query_embedding
        return self.rows[:top_k]


def test_openai_pipeline_ingest_and_query(monkeypatch, tmp_path: Path) -> None:
    fake_provider = _FakeOpenAIProvider()

    monkeypatch.setattr(pipeline_module, "OpenAIProvider", lambda *args, **kwargs: fake_provider)
    monkeypatch.setattr(pipeline_module, "OpenAIChromaStore", _FakeOpenAIChromaStore)

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "note.md").write_text("RAG 是检索增强生成。", encoding="utf-8")

    pipeline = RagPipeline(base_dir=tmp_path, provider="openai")
    ingest_result = pipeline.ingest(data_dir)
    query_result = pipeline.query("RAG 是什么？", top_k=2, debug=True)

    assert ingest_result["added"] >= 1
    assert fake_provider.embed_text_calls
    assert fake_provider.embed_query_calls == ["RAG 是什么？"]
    assert fake_provider.generate_calls
    assert query_result["answer"] == "openai generated answer"
    assert "note.md" in query_result["sources"]
    assert query_result["prompt"]
    assert pipeline.store.cleared is True


def test_openai_pipeline_filters_low_score_and_reranks_hits(monkeypatch, tmp_path: Path) -> None:
    class _PresetStore:
        def __init__(self, *args, **kwargs) -> None:
            self.cleared = False

        def clear(self):
            self.cleared = True

        def add(self, chunks, embeddings):
            _ = (chunks, embeddings)
            return 0

        def count(self):
            return 3

        def query_by_embedding(self, query_embedding, top_k=3):
            _ = (query_embedding, top_k)
            return [
                {"id": "a", "text": "今天 心情 不好", "source": "mood.md", "chunk_index": 0, "score": 0.95},
                {"id": "b", "text": "MongoDB 聚合管道 是 数据处理流水线", "source": "tech.md", "chunk_index": 0, "score": 0.55},
                {"id": "c", "text": "聚合 统计 示例", "source": "low.md", "chunk_index": 0, "score": 0.20},
            ]

    fake_provider = _FakeOpenAIProvider()
    monkeypatch.setattr(pipeline_module, "OpenAIProvider", lambda *args, **kwargs: fake_provider)
    monkeypatch.setattr(pipeline_module, "OpenAIChromaStore", _PresetStore)
    monkeypatch.setenv("RAG_SCORE_THRESHOLD", "0.42")
    monkeypatch.setenv("RAG_RERANK_LIMIT", "2")

    pipeline = RagPipeline(base_dir=tmp_path, provider="openai")
    result = pipeline.query("聚合管道是什么", top_k=5, debug=True)

    assert result["answer"] == "openai generated answer"
    assert "low.md" not in result["sources"]
    _, contexts = fake_provider.generate_calls[0]
    assert contexts[0]["source"] == "tech.md"
