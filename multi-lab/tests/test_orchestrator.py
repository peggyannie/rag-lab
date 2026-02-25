from pathlib import Path
import os

from multi_lab.orchestrator import run_orchestration


def test_orchestration_returns_three_stages(tmp_path: Path, monkeypatch) -> None:
    # Provide a fake CrewAI module to avoid external dependency in unit test.
    class FakeAgent:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class FakeTask:
        def __init__(self, description, expected_output, agent):
            self.description = description
            self.expected_output = expected_output
            self.agent = agent

    class FakeProcess:
        sequential = "sequential"

    class FakeCrewResult:
        raw = "analyst: ok\nbuilder: ok\nreviewer: ok"

    class FakeCrew:
        def __init__(self, agents, tasks, process, verbose):
            self.agents = agents
            self.tasks = tasks
            self.process = process
            self.verbose = verbose

        def kickoff(self, inputs):
            return FakeCrewResult()

    fake_mod = type("FakeCrewAIModule", (), {
        "Agent": FakeAgent,
        "Task": FakeTask,
        "Crew": FakeCrew,
        "Process": FakeProcess,
    })

    monkeypatch.setattr("multi_lab.orchestrator._preflight_checks", lambda: None)
    monkeypatch.setattr("multi_lab.orchestrator._import_crewai", lambda: fake_mod)
    monkeypatch.setattr("multi_lab.orchestrator._build_llm", lambda model: object())

    (tmp_path / "agents.yaml").write_text(
        """
analyst:
  role: Analyst
  goal: Analyze task
  backstory: You analyze constraints.
builder:
  role: Builder
  goal: Build solution
  backstory: You implement.
reviewer:
  role: Reviewer
  goal: Review quality
  backstory: You verify.
""",
        encoding="utf-8",
    )
    (tmp_path / "tasks.yaml").write_text(
        """
analyst:
  description: Analyze {question}
  expected_output: Plan
builder:
  description: Build for {question}
  expected_output: Build output
reviewer:
  description: Review for {question}
  expected_output: Review output
""",
        encoding="utf-8",
    )

    out = run_orchestration(base_dir=tmp_path, question="RAG 是什么？", data_path=str(tmp_path))
    assert "analyst" in out.lower()
    assert "builder" in out.lower()
    assert "reviewer" in out.lower()


def test_orchestration_loads_dotenv(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    (tmp_path / ".env").write_text("OPENAI_API_KEY=test-key\n", encoding="utf-8")
    # No YAMLs needed because preflight should pass before any file parse is required in this assertion path.
    from multi_lab.orchestrator import _load_dotenv

    _load_dotenv(tmp_path)
    assert os.getenv("OPENAI_API_KEY") == "test-key"
