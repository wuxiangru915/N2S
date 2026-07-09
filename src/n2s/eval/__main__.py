"""CLI entry point: ``python -m n2s.eval``."""

from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path

from n2s.core.evaluation.dataset import EvaluationDataset
from n2s.demo.data import init_demo_db
from n2s.eval.runner import N2SEvaluationRunner, print_report


def _default_dataset_path() -> str:
    return str(Path(__file__).resolve().parent / "datasets" / "n2s_sql.yaml")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the N2S Text2SQL benchmark")
    parser.add_argument(
        "--dataset",
        default=_default_dataset_path(),
        help="Path to the evaluation dataset YAML file",
    )
    parser.add_argument(
        "--providers",
        nargs="+",
        default=["mock"],
        help="LLM providers to evaluate (mock, openai, anthropic, ollama)",
    )
    parser.add_argument(
        "--db",
        default=None,
        help="Path to the SQLite database. Defaults to the demo database.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional path to write a JSON report",
    )
    args = parser.parse_args()

    db_path = args.db or str(init_demo_db())
    dataset = EvaluationDataset.from_yaml(args.dataset)

    print(f"Dataset: {dataset.name} ({len(dataset.test_cases)} test cases)")
    print(f"Database: {db_path}")
    print(f"Providers: {', '.join(args.providers)}")

    runner = N2SEvaluationRunner(database_path=db_path)
    reports = asyncio.run(runner.run_comparison(dataset, args.providers))

    for report in reports.values():
        print_report(report)

    if args.output:
        import json

        summary = {
            provider: {
                "passed": report.passed_count(),
                "total": report.total_count(),
                "accuracy": report.accuracy(),
            }
            for provider, report in reports.items()
        }
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"\nSummary written to {args.output}")


if __name__ == "__main__":
    main()
