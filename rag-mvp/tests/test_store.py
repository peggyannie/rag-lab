from pathlib import Path

from src.store import LocalVectorStore


def test_store_deduplicates_chunks(tmp_path: Path) -> None:
    store = LocalVectorStore(tmp_path / "store.json")
    chunks = [
        {"id": "a#0", "text": "python rag basics", "source": "a.md", "chunk_index": 0},
        {"id": "a#1", "text": "vector search with chunks", "source": "a.md", "chunk_index": 1},
    ]

    added_once = store.add(chunks)
    added_twice = store.add(chunks)

    assert added_once == 2
    assert added_twice == 0
    assert store.count() == 2


def test_store_query_ranks_relevant_first(tmp_path: Path) -> None:
    store = LocalVectorStore(tmp_path / "store.json")
    store.add(
        [
            {"id": "1", "text": "python language", "source": "a.md", "chunk_index": 0},
            {"id": "2", "text": "cooking recipe", "source": "b.md", "chunk_index": 0},
        ]
    )
    results = store.query("python question", top_k=1)
    assert results[0]["id"] == "1"
