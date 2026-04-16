from __future__ import annotations

import argparse
import json
from pathlib import Path

from manual_review_registry import build_manual_review_registry_report


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECISIONS_ROOT = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-249-manual-review-decision-log"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-250-manual-review-registry"


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a registry report from manual review decision logs.")
    parser.add_argument("--experiment-id", default="EXP-250-manual-review-registry")
    parser.add_argument("--decisions-root", type=Path, default=DEFAULT_DECISIONS_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "experiment_id": args.experiment_id,
        "decisionsRoot": str(args.decisions_root),
        **build_manual_review_registry_report(args.decisions_root),
    }
    write_json(args.output_dir / "report.json", report)
    print(args.output_dir / "report.json")


if __name__ == "__main__":
    main()
