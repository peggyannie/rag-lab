from pathlib import Path

from cli import run_cli


def test_cli_ingest_query_stats(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "doc.md").write_text("RAG 使用检索结果增强回答质量", encoding="utf-8")

    code_ingest, out_ingest = run_cli(["--base-dir", str(tmp_path), "--ingest", str(data_dir)])
    assert code_ingest == 0
    assert "added" in out_ingest

    code_query, out_query = run_cli(["--base-dir", str(tmp_path), "--query", "RAG 是什么"]) 
    assert code_query == 0
    assert "answer" in out_query

    code_stats, out_stats = run_cli(["--base-dir", str(tmp_path), "--stats"])
    assert code_stats == 0
    assert "chunks" in out_stats
