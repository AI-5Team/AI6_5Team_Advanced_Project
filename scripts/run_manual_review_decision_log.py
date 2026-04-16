from __future__ import annotations

import argparse
import json
from pathlib import Path

from manual_review_decision import (
    apply_manual_review_decision,
    build_manual_review_packet_report,
    render_manual_review_decision_markdown,
)
from manual_review_queue import read_json


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE_REPORT = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-248-manual-review-queue" / "report.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-249-manual-review-decision-log"


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_key_value_pairs(pairs: list[str] | None) -> dict[str, str]:
    result: dict[str, str] = {}
    for pair in pairs or []:
        key, separator, value = pair.partition("=")
        if not separator:
            raise ValueError(f"expected KEY=VALUE format, got {pair!r}")
        result[key] = value
    return result


def sanitize_candidate_key(candidate_key: str) -> str:
    return candidate_key.replace("::", "__").replace("/", "_").replace("\\", "_")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a manual review decision artifact from a queue report.")
    parser.add_argument("--experiment-id", default="EXP-249-manual-review-decision-log")
    parser.add_argument("--queue-report", type=Path, default=DEFAULT_QUEUE_REPORT)
    parser.add_argument("--candidate-key")
    parser.add_argument("--reviewer", default="codex")
    parser.add_argument("--final-decision", default="hold")
    parser.add_argument("--summary-note", required=True)
    parser.add_argument("--check", action="append")
    parser.add_argument("--check-note", action="append")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    queue_report = read_json(args.queue_report)
    packet_report = build_manual_review_packet_report(queue_report)
    packets = packet_report["packets"]
    if not packets:
        raise ValueError("queue report contains no review packets")

    packet = None
    if args.candidate_key:
        for candidate in packets:
            if candidate["candidateKey"] == args.candidate_key:
                packet = candidate
                break
        if packet is None:
            raise ValueError(f"candidate not found: {args.candidate_key!r}")
    elif len(packets) == 1:
        packet = packets[0]
    else:
        raise ValueError("candidate-key is required when queue report contains multiple entries")

    checklist_statuses = parse_key_value_pairs(args.check)
    checklist_notes = parse_key_value_pairs(args.check_note)
    decision = apply_manual_review_decision(
        packet,
        reviewer=args.reviewer,
        final_decision=args.final_decision,
        summary_note=args.summary_note,
        checklist_statuses=checklist_statuses,
        checklist_notes=checklist_notes,
    )

    candidate_dir = args.output_dir / sanitize_candidate_key(decision["candidateKey"])
    candidate_dir.mkdir(parents=True, exist_ok=True)
    write_json(candidate_dir / "review_packet.json", packet)
    write_json(candidate_dir / "decision.json", decision)
    (candidate_dir / "decision.md").write_text(
        render_manual_review_decision_markdown(decision, experiment_id=args.experiment_id),
        encoding="utf-8",
    )
    print(candidate_dir / "decision.json")


if __name__ == "__main__":
    main()
