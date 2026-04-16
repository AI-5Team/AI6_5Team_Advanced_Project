from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT_ARTIFACT = ROOT_DIR / "docs" / "experiments" / "artifacts" / "exp-141-prompt-baseline-coverage-audit.json"
DEFAULT_OUTPUT_ROOT = ROOT_DIR / "docs" / "experiments" / "artifacts"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _priority_band(row: dict) -> tuple[str, int, str]:
    coverage_hint = row.get("coverageHint") if isinstance(row.get("coverageHint"), dict) else {}
    mismatch_dimensions = [item for item in coverage_hint.get("mismatchDimensions", []) if isinstance(item, str)]
    mismatch_count = len(mismatch_dimensions)
    includes_region = "quickOptions.emphasizeRegion" in mismatch_dimensions
    nearest_profile_id = str(coverage_hint.get("nearestProfileId") or "")
    nearest_profile_kind = str(coverage_hint.get("nearestProfileKind") or "")

    if nearest_profile_kind == "default" and nearest_profile_id == "main_baseline" and mismatch_count == 1 and not includes_region:
        return (
            "P1",
            100,
            "기본 baseline 인접 단일 quick option gap입니다. main baseline coverage를 가장 작게 넓히는 후보라서 먼저 검토할 가치가 높습니다.",
        )
    if mismatch_count == 1 and not includes_region:
        return (
            "P2",
            80,
            "기존 option profile 인접 단일 quick option gap입니다. 새 scenario를 열지 않고 coverage를 넓힐 수 있는 다음 후보입니다.",
        )
    if mismatch_count == 1 and includes_region:
        return (
            "P3",
            60,
            "단일 토글이지만 region emphasis가 포함된 gap입니다. location policy 리스크 때문에 비지역 토글보다 뒤에서 검토하는 편이 맞습니다.",
        )
    return (
        "P4",
        40,
        "다중 quick option 조합 gap입니다. 인접 단일 토글 후보를 먼저 정리한 뒤에 보는 편이 맞습니다.",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Prioritize quick option gap candidates from the prompt baseline coverage audit.")
    parser.add_argument("--audit-artifact", type=Path, default=DEFAULT_AUDIT_ARTIFACT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--experiment-id", default="EXP-142")
    parser.add_argument("--experiment-title", default="Prompt Baseline Quick Option Gap Priority")
    parser.add_argument("--artifact-name", default="exp-142-prompt-baseline-quick-option-gap-priority.json")
    args = parser.parse_args()

    audit = _load_json(args.audit_artifact)
    rows = [row for row in audit.get("auditRows", []) if isinstance(row, dict)]

    candidates: list[dict] = []
    for row in rows:
        coverage_hint = row.get("coverageHint")
        if not isinstance(coverage_hint, dict):
            continue
        if coverage_hint.get("gapClass") != "quick_option_gap":
            continue

        band, score, rationale = _priority_band(row)
        candidates.append(
            {
                "priorityBand": band,
                "priorityScore": score,
                "rationale": rationale,
                "sourceProfileId": row.get("sourceProfileId"),
                "sourceProfileKind": row.get("sourceProfileKind"),
                "sourceScenarioId": row.get("sourceScenarioId"),
                "nearestProfileId": coverage_hint.get("nearestProfileId"),
                "nearestProfileKind": coverage_hint.get("nearestProfileKind"),
                "context": row.get("context"),
                "mismatchDimensions": coverage_hint.get("mismatchDimensions", []),
                "recommendedAction": coverage_hint.get("recommendedAction"),
            }
        )

    band_order = {"P1": 0, "P2": 1, "P3": 2, "P4": 3}
    candidates.sort(
        key=lambda item: (
            band_order.get(str(item.get("priorityBand") or "P9"), 9),
            -int(item.get("priorityScore") or 0),
            str(((item.get("context") or {}).get("purpose") if isinstance(item.get("context"), dict) else "") or ""),
            str(((item.get("context") or {}).get("templateId") if isinstance(item.get("context"), dict) else "") or ""),
            str(item.get("sourceProfileId") or ""),
        )
    )

    aggregates = {"totalQuickOptionGaps": len(candidates), "bandCounts": {}}
    for item in candidates:
        band = str(item.get("priorityBand") or "unknown")
        aggregates["bandCounts"][band] = aggregates["bandCounts"].get(band, 0) + 1

    artifact = {
        "experiment_id": args.experiment_id,
        "experiment_title": args.experiment_title,
        "source_audit_artifact": str(args.audit_artifact),
        "aggregates": aggregates,
        "priorityRules": {
            "P1": "main baseline 인접 단일 quick option gap, region 미포함",
            "P2": "option profile 인접 단일 quick option gap, region 미포함",
            "P3": "단일 quick option gap이지만 region emphasis 포함",
            "P4": "다중 quick option 조합 gap",
        },
        "candidates": candidates,
        "topCandidates": candidates[:8],
    }

    args.output_root.mkdir(parents=True, exist_ok=True)
    artifact_path = args.output_root / args.artifact_name
    artifact_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(aggregates, ensure_ascii=False, indent=2))
    print(f"artifact_path={artifact_path}")


if __name__ == "__main__":
    main()
