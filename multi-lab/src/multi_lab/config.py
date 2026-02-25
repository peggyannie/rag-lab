from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass
class Settings:
    base_dir: Path
    model: str = "gpt-4o-mini"

    def __post_init__(self) -> None:
        self.base_dir = Path(self.base_dir)
        self.db_path = self.base_dir / "storage" / "kb.json"
        self.agents_yaml = self.base_dir / "agents.yaml"
        self.tasks_yaml = self.base_dir / "tasks.yaml"


def load_settings(base_dir: str | Path, model: str | None = None) -> Settings:
    return Settings(base_dir=Path(base_dir), model=model or os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
