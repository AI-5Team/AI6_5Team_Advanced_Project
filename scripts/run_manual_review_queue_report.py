from __future__ import annotations

import argparse
import json
from pathlib import Path

from manual_review_queue import build_manual_review_queue_report, read_json, render_manual_review_queue_markdown


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-248-manual-review-queue"
DEFAULT_SUMMARIES = [
    REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-238-sora2-lane-reopen-beer-check" / "summary.json",
    REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-239-sora2-current-best-vs-control-two-sample-check" / "summary.json",
]


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a manual review queue artifact from benchmark summaries.")
    parser.add_argument("--experiment-id", default="EXP-248-manual-review-queue")
    parser.add_argument("--benchmark-summaries", nargs="+", type=Path, default=DEFAULT_SUMMARIES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--label")
    parser.add_argument("--provider")
    parser.add_argument("--include-reference-only", action="store_true")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summaries = [read_json(path) for path in args.benchmark_summaries]
    queue_report = build_manual_review_queue_report(
        summaries,
        label=args.label,
        provider=args.provider,
        include_reference_only=args.include_reference_only,
    )
    report = {
        "experiment_id": args.experiment_id,
        "benchmarkSummaries": [str(path) for path in args.benchmark_summaries],
        **queue_report,
    }
    write_json(args.output_dir / "report.json", report)
    (args.output_dir / "queue.md").write_text(
        render_manual_review_queue_markdown(report, experiment_id=args.experiment_id),
        encoding="utf-8",
    )
    print(args.output_dir / "report.json")


if __name__ == "__main__":
    main()
