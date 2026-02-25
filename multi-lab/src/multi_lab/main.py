from __future__ import annotations

import argparse
from typing import List, Tuple

from multi_lab.orchestrator import run_orchestration


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Multi-agent RAG orchestrator")
    p.add_argument("--base-dir", required=True)
    p.add_argument("--data", required=True)
    p.add_argument("--question", required=True)
    return p


def run_cli(argv: List[str]) -> Tuple[int, str]:
    args = _parser().parse_args(argv)
    try:
        output = run_orchestration(base_dir=args.base_dir, question=args.question, data_path=args.data)
        return 0, output
    except Exception as exc:
        return 2, str(exc)


def main() -> None:
    code, output = run_cli(__import__("sys").argv[1:])
    print(output)
    raise SystemExit(code)


if __name__ == "__main__":
    main()
