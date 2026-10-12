import argparse
import json
import sys
from pathlib import Path

import psycopg
import requests

from app.services.evaluation import (
    ALL_METRIC_FIELDS,
    compare_baseline,
    evaluate_thresholds,
    load_evaluation_dataset,
    load_report,
    parse_thresholds,
    run_evaluation,
)


def report_progress(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate RAG retrieval and answer quality against a labeled dataset."
    )
    parser.add_argument("--dataset", required=True, help="Path to the evaluation JSON file")
    parser.add_argument("--output", required=True, help="Path to save the JSON report")
    parser.add_argument("--baseline", help="Optional previous report for regression checks")
    parser.add_argument("--k", type=int, default=5, help="Top-k retrieval/source cutoff")
    parser.add_argument(
        "--max-relevant-distance",
        type=float,
        default=0.6,
        help="Distance cutoff used by the RAG pipeline",
    )
    parser.add_argument("--judge-model", help="Ollama model used as the LLM judge")
    parser.add_argument(
        "--max-regression",
        type=float,
        default=0.05,
        help="Allowed absolute metric drop versus baseline (0 to 1)",
    )
    parser.add_argument(
        "--min",
        dest="thresholds",
        action="append",
        default=[],
        metavar="METRIC=VALUE",
        help=f"Minimum score; may be repeated. Metrics: {', '.join(ALL_METRIC_FIELDS)}",
    )
    args = parser.parse_args()

    try:
        if args.k < 1:
            raise ValueError("--k must be at least 1")
        if not 0 <= args.max_relevant_distance <= 2:
            raise ValueError("--max-relevant-distance must be between 0 and 2")
        if not 0 <= args.max_regression <= 1:
            raise ValueError("--max-regression must be between 0 and 1")

        cases = load_evaluation_dataset(args.dataset)
        report = run_evaluation(
            cases,
            k=args.k,
            max_relevant_distance=args.max_relevant_distance,
            judge_model=args.judge_model,
            progress_callback=report_progress,
        )
        failures = evaluate_thresholds(report["summary"], parse_thresholds(args.thresholds))
        if args.baseline:
            regressions = compare_baseline(
                report, load_report(args.baseline), args.max_regression
            )
            failures.extend(
                f"{item['case_id'] + ': ' if item['case_id'] else ''}"
                f"{item['metric']} regressed by {item['drop']:.3f}: "
                f"{item['baseline']:.3f} -> {item['current']:.3f}"
                for item in regressions
            )

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Evaluation report: {output_path}")
        for metric, score in report["summary"].items():
            rendered_score = "n/a" if score is None else f"{score:.3f}"
            print(f"{metric}: {rendered_score}")
        if failures:
            print("\nEvaluation gates failed:", file=sys.stderr)
            for failure in failures:
                print(f"- {failure}", file=sys.stderr)
            return 1
        print("\nEvaluation gates passed.")
        return 0
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        psycopg.Error,
        requests.RequestException,
    ) as exc:
        print(f"Evaluation failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
