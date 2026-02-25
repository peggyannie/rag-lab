from pathlib import Path

from src.config import Settings, load_settings


def test_settings_defaults(tmp_path: Path) -> None:
    settings = Settings(base_dir=tmp_path)
    assert settings.provider == "local"
    assert settings.data_dir == tmp_path / "data"
    assert settings.db_path == tmp_path / "chroma_db" / "store.json"


def test_load_settings_reads_provider_from_dotenv(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("RAG_PROVIDER", raising=False)
    (tmp_path / ".env").write_text("RAG_PROVIDER=openai\n", encoding="utf-8")

    settings = load_settings(base_dir=tmp_path)

    assert settings.provider == "openai"
