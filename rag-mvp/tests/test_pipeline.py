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


def test_low_score_results_return_not_found(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "note.md").write_text("这是一段普通说明文字。", encoding="utf-8")

    pipeline = RagPipeline(base_dir=tmp_path, provider="local")
    pipeline.ingest(data_dir)
    query_result = pipeline.query("量子场论是什么？")

    assert "知识库中未找到相关内容" in query_result["answer"]


def test_openai_pipeline_init_reads_api_key_from_dotenv(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    (tmp_path / ".env").write_text("OPENAI_API_KEY=test-key\n", encoding="utf-8")

    pipeline = RagPipeline(base_dir=tmp_path, provider="openai")

    assert pipeline.provider == "openai"


def test_reingest_rebuilds_local_index_after_file_deleted(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    kept = data_dir / "keep.md"
    removed = data_dir / "remove.md"
    kept.write_text("数据库 索引 优化", encoding="utf-8")
    removed.write_text("聚合管道 入门", encoding="utf-8")

    pipeline = RagPipeline(base_dir=tmp_path, provider="local")
    pipeline.ingest(data_dir)
    assert pipeline.stats()["chunks"] >= 2

    removed.unlink()
    pipeline.ingest(data_dir)

    result = pipeline.query("聚合管道 是什么")
    assert "remove.md" not in result["sources"]
