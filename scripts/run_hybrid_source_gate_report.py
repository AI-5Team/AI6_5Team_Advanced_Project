from __future__ import annotations

import argparse
import json
from pathlib import Path

from video_quality_gate import annotate_benchmark_summary


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-246-hybrid-source-gate-calibration"
DEFAULT_SUMMARIES = [
    REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-238-sora2-lane-reopen-beer-check" / "summary.json",
    REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-239-sora2-current-best-vs-control-two-sample-check" / "summary.json",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibrate hybrid source gate decisions from existing video benchmark summaries.")
    parser.add_argument("--experiment-id", default="EXP-246-hybrid-source-gate-calibration")
    parser.add_argument("--benchmark-summaries", nargs="+", type=Path, default=DEFAULT_SUMMARIES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    benchmarks: list[dict] = []
    aggregate_decision_counts: dict[str, int] = {}
    aggregate_provider_counts: dict[str, dict[str, int]] = {}

    for summary_path in args.benchmark_summaries:
        summary = read_json(summary_path)
        annotate_benchmark_summary(summary)
        gate_summary = summary.get("hybrid_source_gate_summary", {})
        for decision, count in gate_summary.get("decisionCounts", {}).items():
            aggregate_decision_counts[str(decision)] = aggregate_decision_counts.get(str(decision), 0) + int(count)
        for provider, counts in gate_summary.get("providerDecisionCounts", {}).items():
            provider_bucket = aggregate_provider_counts.setdefault(str(provider), {})
            for decision, count in dict(counts).items():
                provider_bucket[str(decision)] = provider_bucket.get(str(decision), 0) + int(count)
        benchmarks.append(
            {
                "summaryPath": str(summary_path),
                "benchmarkId": summary.get("benchmark_id"),
                "hybridSourceGateSummary": gate_summary,
                "images": summary.get("images"),
            }
        )

    report = {
        "experiment_id": args.experiment_id,
        "benchmarks": benchmarks,
        "aggregateDecisionCounts": aggregate_decision_counts,
        "aggregateProviderDecisionCounts": aggregate_provider_counts,
    }
    write_json(args.output_dir / "report.json", report)
    print(args.output_dir / "report.json")


if __name__ == "__main__":
    main()
