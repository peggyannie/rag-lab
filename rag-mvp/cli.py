from __future__ import annotations

import argparse
import json
from typing import List, Tuple

from src.pipeline import RagPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RAG MVP CLI")
    parser.add_argument("--base-dir", default=".")
    parser.add_argument("--provider", default=None)
    parser.add_argument("--ingest", default=None)
    parser.add_argument("--query", default=None)
    parser.add_argument("--stats", action="store_true")
    parser.add_argument("--chat", action="store_true")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--debug", action="store_true")
    return parser


def run_cli(argv: List[str]) -> Tuple[int, str]:
    args = build_parser().parse_args(argv)
    pipeline = RagPipeline(base_dir=args.base_dir, provider=args.provider)

    if args.ingest:
        result = pipeline.ingest(args.ingest)
        return 0, json.dumps(result, ensure_ascii=False)

    if args.query:
        result = pipeline.query(args.query, top_k=args.top_k, debug=args.debug)
        return 0, json.dumps(result, ensure_ascii=False)

    if args.stats:
        result = pipeline.stats()
        return 0, json.dumps(result, ensure_ascii=False)

    if args.chat:
        return 0, "chat mode is not implemented in this mvp"

    return 1, "No action specified. Use --ingest/--query/--stats/--chat"


def main() -> None:
    code, output = run_cli(__import__("sys").argv[1:])
    print(output)
    raise SystemExit(code)


if __name__ == "__main__":
    main()
