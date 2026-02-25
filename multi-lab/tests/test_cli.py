from multi_lab.main import run_cli


def test_cli_runs(tmp_path, monkeypatch):
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
        raw = "analyst\nbuilder\nreviewer"

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

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "doc.md").write_text("RAG 通过检索增强", encoding="utf-8")

    code, output = run_cli([
        "--base-dir", str(tmp_path),
        "--data", str(data_dir),
        "--question", "RAG 是什么？",
    ])

    assert code == 0
    assert "analyst" in output
    assert "builder" in output
    assert "reviewer" in output
