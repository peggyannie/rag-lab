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


def test_store_query_handles_chinese_wording_variation(tmp_path: Path) -> None:
    store = LocalVectorStore(tmp_path / "store.json")
    store.add(
        [
            {
                "id": "cn-1",
                "text": "如何中断情绪反刍并恢复专注",
                "source": "emotion.md",
                "chunk_index": 0,
            },
            {
                "id": "cn-2",
                "text": "MongoDB 聚合管道用于数据统计分析",
                "source": "mongo.md",
                "chunk_index": 0,
            },
        ]
    )

    results = store.query("情绪反刍怎么中断", top_k=1)

    assert results[0]["id"] == "cn-1"
    assert float(results[0]["score"]) > 0


def test_store_query_boosts_source_name_match(tmp_path: Path) -> None:
    store = LocalVectorStore(tmp_path / "store.json")
    store.add(
        [
            {
                "id": "generic",
                "text": "这是一段通用说明内容",
                "source": "通用笔记.md",
                "chunk_index": 0,
            },
            {
                "id": "target",
                "text": "这是一段通用说明内容",
                "source": "嵌入引用说明.md",
                "chunk_index": 0,
            },
        ]
    )

    results = store.query("嵌入和引用的区别", top_k=1)

    assert results[0]["id"] == "target"
