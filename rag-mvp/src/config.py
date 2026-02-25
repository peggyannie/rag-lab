from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


@dataclass
class Settings:
    base_dir: Path
    provider: str = "local"

    def __post_init__(self) -> None:
        self.base_dir = Path(self.base_dir)
        self.data_dir = self.base_dir / "data"
        self.chroma_dir = self.base_dir / "chroma_db"
        self.db_path = self.chroma_dir / "store.json"


def load_settings(base_dir: str | Path | None = None, provider: str | None = None) -> Settings:
    resolved_base = Path(base_dir) if base_dir else Path.cwd()
    load_dotenv(dotenv_path=resolved_base / ".env", override=False)
    resolved_provider = provider or os.getenv("RAG_PROVIDER", "local")
    return Settings(base_dir=resolved_base, provider=resolved_provider)
