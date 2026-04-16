from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from services.worker.experiments.prompt_harness import (  # noqa: E402
    DEFAULT_ARTIFACT_ROOT,
    DEFAULT_TEMPLATE_SPEC_ROOT,
    build_deterministic_reference_bundle,
    build_prompt_package,
    evaluate_copy_bundle,
    evaluate_korean_integrity,
    evaluate_scene_plan_preview,
    generate_copy_bundle_with_model,
    get_experiment_definition,
    load_experiment_context,
    resolve_api_key_env,
    sanitize_error_message,
    slugify,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run repeatability spot checks for prompt variants under a fixed model.")
    parser.add_argument("--experiment-id", default="EXP-128")
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--template-spec-root", type=Path, default=DEFAULT_TEMPLATE_SPEC_ROOT)
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    parser.add_argument("--api-key-env", default=None, help="Optional env var override. Defaults to provider-specific key.")
    args = parser.parse_args()

    experiment = get_experiment_definition(args.experiment_id)
    api_key_env = args.api_key_env or resolve_api_key_env(experiment.model.provider)
    context = load_experiment_context(args.template_spec_root, experiment.scenario)

    deterministic_bundle = build_deterministic_reference_bundle(args.template_spec_root, experiment.scenario)
    deterministic_eval = evaluate_copy_bundle(
        deterministic_bundle,
        experiment.scenario,
        context["template"],
        context["copy_rule"],
    )

    results: list[dict[str, object]] = [
        {
            "variant_id": "deterministic_reference",
            "lever_id": "reference",
            "run_index": 0,
            "provider": "deterministic",
            "model_name": "rule_based_copy_builder",
            "latency_ms": 0,
            "output": deterministic_bundle,
            "evaluation": deterministic_eval,
            "scene_plan_metrics": evaluate_scene_plan_preview(args.template_spec_root, experiment.scenario, deterministic_bundle),
            "korean_integrity": evaluate_korean_integrity(deterministic_bundle),
            "error": None,
        }
    ]

    variants = (experiment.baseline_variant, *experiment.candidate_variants)
    for variant in variants:
        prompt_package = build_prompt_package(args.template_spec_root, experiment.scenario, variant)
        for run_index in range(1, args.repeat + 1):
            started = time.perf_counter()
            try:
                output = generate_copy_bundle_with_model(
                    model=experiment.model,
                    prompt_package=prompt_package,
                    asset_paths=experiment.scenario.asset_paths,
                    api_key_env=api_key_env,
                )
                latency_ms = int((time.perf_counter() - started) * 1000)
                results.append(
                    {
                        "variant_id": variant.variant_id,
                        "lever_id": variant.lever_id,
                        "run_index": run_index,
                        "provider": experiment.model.provider,
                        "model_name": experiment.model.model_name,
                        "latency_ms": latency_ms,
                        "output": output,
                        "evaluation": evaluate_copy_bundle(
                            output,
                            experiment.scenario,
                            context["template"],
                            context["copy_rule"],
                        ),
                        "scene_plan_metrics": evaluate_scene_plan_preview(args.template_spec_root, experiment.scenario, output),
                        "korean_integrity": evaluate_korean_integrity(output),
                        "error": None,
                    }
                )
            except Exception as exc:  # noqa: BLE001
                latency_ms = int((time.perf_counter() - started) * 1000)
                results.append(
                    {
                        "variant_id": variant.variant_id,
                        "lever_id": variant.lever_id,
                        "run_index": run_index,
                        "provider": experiment.model.provider,
                        "model_name": experiment.model.model_name,
                        "latency_ms": latency_ms,
                        "output": {},
                        "evaluation": {
                            "score": 0.0,
                            "failed_checks": [f"request failed: {sanitize_error_message(str(exc))}"],
                            "region_repeat_count": 0,
                        },
                        "scene_plan_metrics": {
                            "over_limit_scene_ids": [],
                            "headline_lengths": {},
                            "closing_cta_actionable": False,
                        },
                        "korean_integrity": {},
                        "error": sanitize_error_message(str(exc)),
                    }
                )

    summary_rows: list[dict[str, object]] = []
    for variant in variants:
        variant_rows = [row for row in results if row["variant_id"] == variant.variant_id]
        success_rows = [row for row in variant_rows if not row["error"]]
        hook_lengths = [len(str(row["output"].get("hookText", ""))) for row in success_rows]
        cta_lengths = [len(str(row["output"].get("ctaText", ""))) for row in success_rows]
        over_limit_counts = [len(row["scene_plan_metrics"].get("over_limit_scene_ids", [])) for row in success_rows]
        summary_rows.append(
            {
                "variant_id": variant.variant_id,
                "lever_id": variant.lever_id,
                "run_count": len(variant_rows),
                "success_count": len(success_rows),
                "avg_score": round(sum(float(row["evaluation"]["score"]) for row in variant_rows) / max(1, len(variant_rows)), 1),
                "avg_hook_length": round(sum(hook_lengths) / max(1, len(hook_lengths)), 1) if hook_lengths else None,
                "avg_cta_length": round(sum(cta_lengths) / max(1, len(cta_lengths)), 1) if cta_lengths else None,
                "avg_over_limit_scene_count": round(sum(over_limit_counts) / max(1, len(over_limit_counts)), 2) if over_limit_counts else None,
                "all_runs_passed": all(not row["evaluation"]["failed_checks"] for row in success_rows) and len(success_rows) == len(variant_rows),
                "sample_hooks": [row["output"].get("hookText") for row in success_rows],
            }
        )

    repeatability_id = f"{experiment.experiment_id}-variant-repeatability"
    artifact = {
        "experiment_id": repeatability_id,
        "experiment_title": f"{experiment.experiment_title} Variant Repeatability Spot Check",
        "source_experiment_id": experiment.experiment_id,
        "repeat": args.repeat,
        "scenario": {
            "scenario_id": experiment.scenario.scenario_id,
            "template_id": experiment.scenario.template_id,
            "style_id": experiment.scenario.style_id,
            "purpose": experiment.scenario.purpose,
        },
        "model": {
            "provider": experiment.model.provider,
            "model_name": experiment.model.model_name,
        },
        "summary": summary_rows,
        "results": results,
    }

    args.artifact_root.mkdir(parents=True, exist_ok=True)
    artifact_path = args.artifact_root / f"{slugify(repeatability_id)}.json"
    artifact_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(artifact["summary"], ensure_ascii=False, indent=2))
    print(f"artifact_path={artifact_path}")


if __name__ == "__main__":
    main()
