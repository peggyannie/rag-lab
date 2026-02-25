from pathlib import Path

from multi_lab.config import Settings


def test_settings_defaults(tmp_path: Path) -> None:
    settings = Settings(base_dir=tmp_path)
    assert settings.model == "gpt-4o-mini"
    assert settings.db_path == tmp_path / "storage" / "kb.json"
    assert settings.agents_yaml == tmp_path / "agents.yaml"
    assert settings.tasks_yaml == tmp_path / "tasks.yaml"
