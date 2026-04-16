from __future__ import annotations

import argparse
import json
from pathlib import Path

from approved_hybrid_inventory import build_approved_hybrid_inventory_report


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BENCHMARK_SUMMARIES = [
    REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-238-sora2-lane-reopen-beer-check" / "summary.json",
    REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-239-sora2-current-best-vs-control-two-sample-check" / "summary.json",
]
DEFAULT_DECISIONS_ROOT = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-249-manual-review-decision-log"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-254-approved-hybrid-candidate-inventory"


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_markdown(path: Path, report: dict) -> None:
    lines = [
        "# Approved Hybrid Candidate Inventory",
        "",
        f"- itemCount: `{report['itemCount']}`",
        f"- laneCounts: `{json.dumps(report['laneCounts'], ensure_ascii=False)}`",
        f"- approvalSourceCounts: `{json.dumps(report['approvalSourceCounts'], ensure_ascii=False)}`",
        "",
        "## Recommended By Lane",
        "",
    ]
    for lane, item in sorted(report["recommendedByLane"].items()):
        lines.extend(
            [
                f"### {lane}",
                "",
                f"- label: `{item['label']}`",
                f"- provider: `{item['provider']}`",
                f"- approvalSource: `{item['approvalSource']}`",
                f"- candidateKey: `{item['candidateKey']}`",
                f"- motionAvgRgbDiff: `{item['motionAvgRgbDiff']}`",
                f"- midFrameMse: `{item['midFrameMse']}`",
                "",
            ]
        )

    lines.extend(["## All Approved Items", ""])
    for item in report["items"]:
        lines.extend(
            [
                f"- `{item['serviceLane']}` / `{item['label']}` / `{item['provider']}` / `{item['approvalSource']}` / `{item['candidateKey']}`",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build approved hybrid candidate inventory from benchmark and manual review artifacts.")
    parser.add_argument("--experiment-id", default="EXP-254-approved-hybrid-candidate-inventory")
    parser.add_argument("--benchmark-summary", action="append", type=Path, dest="benchmark_summaries")
    parser.add_argument("--decisions-root", type=Path, default=DEFAULT_DECISIONS_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    benchmark_summaries = args.benchmark_summaries or DEFAULT_BENCHMARK_SUMMARIES
    args.output_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "experimentId": args.experiment_id,
        **build_approved_hybrid_inventory_report(benchmark_summaries, decisions_root=args.decisions_root),
    }
    write_json(args.output_dir / "report.json", report)
    write_markdown(args.output_dir / "inventory.md", report)
    print(args.output_dir / "report.json")


if __name__ == "__main__":
    main()
