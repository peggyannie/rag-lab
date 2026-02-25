from pathlib import Path

from src.pipeline import RagPipeline


def test_answer_without_knowledge_returns_not_found(tmp_path: Path) -> None:
    pipeline = RagPipeline(base_dir=tmp_path, provider="local")
    result = pipeline.query("什么是RAG？")
    assert "知识库中未找到相关内容" in result["answer"]


def test_ingest_then_query_returns_source(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "note.md").write_text("RAG 是检索增强生成，通过检索上下文再回答问题。", encoding="utf-8")

    pipeline = RagPipeline(base_dir=tmp_path, provider="local")
    ingest_result = pipeline.ingest(data_dir)
    query_result = pipeline.query("RAG 是什么？")

    assert ingest_result["added"] >= 1
    assert query_result["sources"]
    assert "note.md" in query_result["sources"]
