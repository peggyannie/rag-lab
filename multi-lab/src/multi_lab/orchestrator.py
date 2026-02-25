from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import os
import sys

from multi_lab.config import load_settings
from multi_lab.rag_tools import RagToolkit


def _import_yaml():
    import yaml

    return yaml


def _import_crewai():
    from crewai import Agent, Crew, Process, Task

    return type("CrewAIModule", (), {"Agent": Agent, "Crew": Crew, "Process": Process, "Task": Task})


def _build_llm(model: str):
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(model=model, temperature=0)


def _load_yaml(path: Path) -> Dict[str, Any]:
    yaml = _import_yaml()
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_dotenv(base_dir: str | Path) -> None:
    env_path = Path(base_dir) / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value


def _preflight_checks() -> None:
    if sys.version_info < (3, 10):
        raise RuntimeError("CrewAI requires Python 3.10+. Please run this project with python3.10 or newer.")
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Missing OPENAI_API_KEY. Set it in environment or .env before running orchestration.")
    os.environ.setdefault("OTEL_SDK_DISABLED", "true")
    os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")


def _render_template(template: str, values: Dict[str, Any]) -> str:
    try:
        return template.format(**values)
    except Exception:
        return template


def run_orchestration(base_dir: str | Path, question: str, data_path: str) -> str:
    _load_dotenv(base_dir)
    _preflight_checks()
    settings = load_settings(base_dir=base_dir)
    toolkit = RagToolkit(base_dir=base_dir)
    ingest_info = toolkit.ingest(data_path)
    retrieval = toolkit.retrieve(question, top_k=3)
    draft_answer = toolkit.answer(question, top_k=3)

    crewai = _import_crewai()
    agents_cfg = _load_yaml(settings.agents_yaml)
    tasks_cfg = _load_yaml(settings.tasks_yaml)

    model = settings.model
    llm = _build_llm(model)
    analyst = crewai.Agent(**agents_cfg["analyst"], llm=llm)
    builder = crewai.Agent(**agents_cfg["builder"], llm=llm)
    reviewer = crewai.Agent(**agents_cfg["reviewer"], llm=llm)

    inputs = {
        "question": question,
        "ingest_info": ingest_info,
        "retrieval": retrieval,
        "draft_answer": draft_answer,
        "model": model,
    }

    tasks = [
        crewai.Task(
            description=_render_template(tasks_cfg["analyst"]["description"], inputs),
            expected_output=_render_template(tasks_cfg["analyst"]["expected_output"], inputs),
            agent=analyst,
        ),
        crewai.Task(
            description=_render_template(tasks_cfg["builder"]["description"], inputs),
            expected_output=_render_template(tasks_cfg["builder"]["expected_output"], inputs),
            agent=builder,
        ),
        crewai.Task(
            description=_render_template(tasks_cfg["reviewer"]["description"], inputs),
            expected_output=_render_template(tasks_cfg["reviewer"]["expected_output"], inputs),
            agent=reviewer,
        ),
    ]

    crew = crewai.Crew(
        agents=[analyst, builder, reviewer],
        tasks=tasks,
        process=crewai.Process.sequential,
        verbose=bool(int(os.getenv("CREW_VERBOSE", "0"))),
    )
    try:
        result = crew.kickoff(inputs=inputs)
    except TypeError:
        result = crew.kickoff()
    return getattr(result, "raw", str(result))
