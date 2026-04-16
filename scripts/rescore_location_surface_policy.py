from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from services.worker.experiments.prompt_harness import (  # noqa: E402
    DEFAULT_ARTIFACT_ROOT,
    count_detail_location_leaks_by_surface,
    get_experiment_definition,
    get_model_comparison_definition,
)


POLICIES: dict[str, tuple[str, ...]] = {
    "strict_all_surfaces": ("hookText", "ctaText", "captions", "hashtags", "sceneText", "subText"),
    "public_copy_surfaces": ("hookText", "ctaText", "captions", "hashtags", "sceneText"),
    "distribution_surfaces": ("captions", "hashtags"),
}


def resolve_scenario(source_experiment_id: str):
    try:
        return get_model_comparison_definition(source_experiment_id).scenario
    except ValueError:
        return get_experiment_definition(source_experiment_id).scenario


def summarize_policy(rows: list[dict[str, object]], policy_id: str, allowed_surfaces: tuple[str, ...]) -> list[dict[str, object]]:
    summary: list[dict[str, object]] = []
    model_names = []
    for row in rows:
        model_name = str(row.get("model_name"))
        if model_name not in model_names:
            model_names.append(model_name)

    for model_name in model_names:
        model_rows = [row for row in rows if str(row.get("model_name")) == model_name]
        pass_rows = 0
        leak_totals: list[int] = []
        leaked_runs: list[int] = []
        for row in model_rows:
            leaks_by_surface = row.get("policy_eval", {}).get(policy_id, {}).get("leaks_by_surface", {})
            leak_total = sum(int(leaks_by_surface.get(surface, 0)) for surface in allowed_surfaces)
            leak_totals.append(leak_total)
            if leak_total == 0:
                pass_rows += 1
            else:
                leaked_runs.append(int(row.get("run_index", 0)))

        summary.append(
            {
                "policy_id": policy_id,
                "model_name": model_name,
                "run_count": len(model_rows),
                "pass_count": pass_rows,
                "pass_rate": round(pass_rows / max(1, len(model_rows)), 2),
                "avg_leak_count": round(sum(leak_totals) / max(1, len(leak_totals)), 2),
                "leaked_runs": leaked_runs,
            }
        )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Rescore nearby-location leakage by surface policy on existing artifacts.")
    parser.add_argument(
        "--artifact-path",
        type=Path,
        default=DEFAULT_ARTIFACT_ROOT / "exp-108-repeatability.json",
    )
    parser.add_argument("--source-experiment-id", default="EXP-108")
    args = parser.parse_args()

    artifact = json.loads(args.artifact_path.read_text(encoding="utf-8"))
    scenario = resolve_scenario(args.source_experiment_id)
    results = artifact.get("results", [])

    rescored_results: list[dict[str, object]] = []
    for row in results:
        output = row.get("output", {})
        if not isinstance(output, dict):
            output = {}
        leaks_by_surface = count_detail_location_leaks_by_surface(output, scenario)
        policy_eval = {}
        for policy_id, surfaces in POLICIES.items():
            leak_count = sum(int(leaks_by_surface.get(surface, 0)) for surface in surfaces)
            policy_eval[policy_id] = {
                "surfaces": list(surfaces),
                "leaks_by_surface": leaks_by_surface,
                "leak_count": leak_count,
                "passed": leak_count == 0,
            }

        row_copy = dict(row)
        row_copy["policy_eval"] = policy_eval
        rescored_results.append(row_copy)

    summary: list[dict[str, object]] = []
    for policy_id, surfaces in POLICIES.items():
        summary.extend(summarize_policy(rescored_results, policy_id, surfaces))

    output_artifact = {
        "source_artifact_path": str(args.artifact_path),
        "source_experiment_id": args.source_experiment_id,
        "policies": {policy_id: list(surfaces) for policy_id, surfaces in POLICIES.items()},
        "summary": summary,
        "results": rescored_results,
    }

    output_path = args.artifact_path.with_name(f"{args.artifact_path.stem}-location-policy-matrix.json")
    output_path.write_text(json.dumps(output_artifact, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"artifact_path={output_path}")


if __name__ == "__main__":
    main()
