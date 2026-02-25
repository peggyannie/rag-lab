from pathlib import Path

from multi_lab.rag_tools import RagToolkit


def test_ingest_and_dedup(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "a.md").write_text("RAG 通过检索增强回答", encoding="utf-8")

    toolkit = RagToolkit(base_dir=tmp_path)
    first = toolkit.ingest(str(data_dir))
    second = toolkit.ingest(str(data_dir))

    assert first["added"] >= 1
    assert second["added"] == 0


def test_answer_contains_source_or_not_found(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "a.md").write_text("RAG 是检索增强生成", encoding="utf-8")

    toolkit = RagToolkit(base_dir=tmp_path)
    toolkit.ingest(str(data_dir))

    found = toolkit.answer("RAG 是什么？")
    not_found = toolkit.answer("量子场论是什么？")

    assert "a.md" in found
    assert "知识库中未找到相关内容" in not_found
