from src.ui_utils import format_results_for_display


def test_format_results_for_display_basic() -> None:
    rows = format_results_for_display(
        [
            {"source": "a.md", "score": 0.123456, "text": "line1\nline2"},
            {"source": "b.md", "score": 0.9, "text": "x" * 200},
        ],
        preview_chars=20,
    )

    assert rows[0]["rank"] == 1
    assert rows[0]["source"] == "a.md"
    assert rows[0]["score"] == 0.1235
    assert rows[0]["preview"] == "line1 line2"
    assert rows[1]["preview"].endswith("...")
