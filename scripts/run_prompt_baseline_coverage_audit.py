from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from services.worker.pipelines.generation import _build_prompt_baseline_summary  # noqa: E402


DEFAULT_MANIFEST_PATH = ROOT_DIR / "packages" / "template-spec" / "manifests" / "prompt-baseline-v1.json"
DEFAULT_TEMPLATE_SPEC_ROOT = ROOT_DIR / "packages" / "template-spec"
DEFAULT_ARTIFACT_ROOT = ROOT_DIR / "docs" / "experiments" / "artifacts"


def _load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_quick_options(quick_options: dict | None) -> dict[str, bool]:
    quick_options = quick_options if isinstance(quick_options, dict) else {}
    return {
        "highlightPrice": bool(quick_options.get("highlightPrice")),
        "shorterCopy": bool(quick_options.get("shorterCopy")),
        "emphasizeRegion": bool(quick_options.get("emphasizeRegion")),
    }


def _iter_quick_option_combinations() -> list[dict[str, bool]]:
    keys = ["highlightPrice", "shorterCopy", "emphasizeRegion"]
    combinations: list[dict[str, bool]] = []
    for values in itertools.product([False, True], repeat=len(keys)):
        combinations.append({key: value for key, value in zip(keys, values, strict=True)})
    return combinations


def _collect_audit_scenarios(manifest: dict) -> list[dict]:
    scenarios: list[dict] = []

    selected_scenario = manifest.get("selectedScenario")
    if isinstance(selected_scenario, dict):
        scenarios.append(
            {
                "sourceProfileId": "main_baseline",
                "sourceProfileKind": "default",
                "purpose": str(selected_scenario.get("purpose") or ""),
                "templateId": str(selected_scenario.get("templateId") or ""),
                "styleId": str(selected_scenario.get("styleId") or ""),
                "scenarioId": str(selected_scenario.get("scenarioId") or "") or None,
                "selectedQuickOptions": _normalize_quick_options(selected_scenario.get("quickOptions")),
            }
        )

    for option in manifest.get("baselineOptions", []):
        if not isinstance(option, dict):
            continue
        scenario = option.get("selectedScenario")
        if not isinstance(scenario, dict):
            continue
        scenarios.append(
            {
                "sourceProfileId": str(option.get("profileId") or option.get("label") or "candidate_profile"),
                "sourceProfileKind": "option",
                "purpose": str(scenario.get("purpose") or ""),
                "templateId": str(scenario.get("templateId") or ""),
                "styleId": str(scenario.get("styleId") or ""),
                "scenarioId": str(scenario.get("scenarioId") or "") or None,
                "selectedQuickOptions": _normalize_quick_options(scenario.get("quickOptions")),
            }
        )

    deduped: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    for scenario in scenarios:
        key = (scenario["purpose"], scenario["templateId"], scenario["styleId"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(scenario)
    return deduped


def _collect_candidate_clusters(rows: list[dict]) -> list[dict]:
    clusters: dict[tuple[str | None, tuple[str, ...]], dict] = {}
    for row in rows:
        coverage_hint = row.get("coverageHint")
        if not isinstance(coverage_hint, dict):
            continue
        if coverage_hint.get("gapClass") != "quick_option_gap":
            continue
        key = (
            coverage_hint.get("nearestProfileId"),
            tuple(item for item in coverage_hint.get("mismatchDimensions", []) if isinstance(item, str)),
        )
        cluster = clusters.setdefault(
            key,
            {
                "nearestProfileId": coverage_hint.get("nearestProfileId"),
                "mismatchDimensions": list(key[1]),
                "contexts": [],
            },
        )
        cluster["contexts"].append(
            {
                "purpose": row["context"]["purpose"],
                "templateId": row["context"]["templateId"],
                "styleId": row["context"]["styleId"],
                "quickOptions": row["context"]["quickOptions"],
                "sourceScenarioId": row["sourceScenarioId"],
            }
        )

    result = list(clusters.values())
    result.sort(key=lambda item: (str(item.get("nearestProfileId") or ""), len(item.get("contexts", []))))
    for item in result:
        item["occurrenceCount"] = len(item.get("contexts", []))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit prompt baseline coverage across known scenario contexts and quick option combinations.")
    parser.add_argument("--baseline-manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--template-spec-root", type=Path, default=DEFAULT_TEMPLATE_SPEC_ROOT)
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    parser.add_argument("--experiment-id", default="EXP-141")
    parser.add_argument("--experiment-title", default="Prompt Baseline Coverage Audit")
    parser.add_argument("--artifact-name", default="exp-141-prompt-baseline-coverage-audit.json")
    args = parser.parse_args()

    manifest = _load_manifest(args.baseline_manifest)
    scenarios = _collect_audit_scenarios(manifest)
    quick_option_combinations = _iter_quick_option_combinations()

    rows: list[dict] = []
    for scenario in scenarios:
        for quick_options in quick_option_combinations:
            summary = _build_prompt_baseline_summary(
                args.template_spec_root,
                purpose=scenario["purpose"],
                template_id=scenario["templateId"],
                style_id=scenario["styleId"],
                quick_options=quick_options,
                input_snapshot={},
            )
            rows.append(
                {
                    "sourceProfileId": scenario["sourceProfileId"],
                    "sourceProfileKind": scenario["sourceProfileKind"],
                    "sourceScenarioId": scenario["scenarioId"],
                    "context": {
                        "purpose": scenario["purpose"],
                        "templateId": scenario["templateId"],
                        "styleId": scenario["styleId"],
                        "quickOptions": quick_options,
                    },
                    "matchesSourceSelectedQuickOptions": quick_options == scenario["selectedQuickOptions"],
                    "recommendedProfileId": (summary or {}).get("recommendedProfile", {}).get("profileId") if isinstance(summary, dict) and isinstance(summary.get("recommendedProfile"), dict) else None,
                    "executionStatus": (summary or {}).get("executionHint", {}).get("status") if isinstance(summary, dict) and isinstance(summary.get("executionHint"), dict) else None,
                    "coverageHint": summary.get("coverageHint") if isinstance(summary, dict) else None,
                    "policyHint": summary.get("policyHint") if isinstance(summary, dict) else None,
                }
            )

    aggregates = {
        "totalContexts": len(rows),
        "executionStatusCounts": {},
        "gapClassCounts": {},
        "recommendedActionCounts": {},
    }
    for row in rows:
        execution_status = row.get("executionStatus") or "unknown"
        aggregates["executionStatusCounts"][execution_status] = aggregates["executionStatusCounts"].get(execution_status, 0) + 1
        coverage_hint = row.get("coverageHint")
        if isinstance(coverage_hint, dict):
            gap_class = coverage_hint.get("gapClass") or "unknown"
            recommended_action = coverage_hint.get("recommendedAction") or "unknown"
        else:
            gap_class = "exact_match"
            recommended_action = "none"
        aggregates["gapClassCounts"][gap_class] = aggregates["gapClassCounts"].get(gap_class, 0) + 1
        aggregates["recommendedActionCounts"][recommended_action] = aggregates["recommendedActionCounts"].get(recommended_action, 0) + 1

    artifact = {
        "experiment_id": args.experiment_id,
        "experiment_title": args.experiment_title,
        "baseline_manifest_path": str(args.baseline_manifest),
        "scenarios": scenarios,
        "auditRows": rows,
        "aggregates": aggregates,
        "quickOptionGapClusters": _collect_candidate_clusters(rows),
    }

    args.artifact_root.mkdir(parents=True, exist_ok=True)
    artifact_path = args.artifact_root / args.artifact_name
    artifact_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(aggregates, ensure_ascii=False, indent=2))
    print(f"artifact_path={artifact_path}")


if __name__ == "__main__":
    main()
