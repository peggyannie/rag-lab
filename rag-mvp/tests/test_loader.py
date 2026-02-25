from pathlib import Path

from src.loader import chunk_text, load_documents


def test_load_documents_filters_md_txt(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("hello markdown", encoding="utf-8")
    (tmp_path / "b.txt").write_text("hello text", encoding="utf-8")
    (tmp_path / "c.csv").write_text("skip", encoding="utf-8")

    docs = load_documents(tmp_path)
    assert len(docs) == 2
    assert {doc["source"] for doc in docs} == {"a.md", "b.txt"}


def test_chunk_text_overlap() -> None:
    text = "0123456789" * 40
    chunks = chunk_text(text, chunk_size=100, chunk_overlap=20)
    assert len(chunks) > 1
    assert chunks[1]["text"].startswith(chunks[0]["text"][-20:])
