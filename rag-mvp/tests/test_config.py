from pathlib import Path

from src.config import Settings


def test_settings_defaults(tmp_path: Path) -> None:
    settings = Settings(base_dir=tmp_path)
    assert settings.provider == "local"
    assert settings.data_dir == tmp_path / "data"
    assert settings.db_path == tmp_path / "chroma_db" / "store.json"
