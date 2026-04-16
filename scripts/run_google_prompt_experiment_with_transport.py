from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict
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
    empty_korean_integrity_metrics,
    evaluate_copy_bundle,
    evaluate_korean_integrity,
    evaluate_scene_plan_preview,
    generate_copy_bundle_with_google_model_with_meta,
    get_experiment_definition,
    load_experiment_context,
    sanitize_error_message,
    serialize_scenario,
    slugify,
    summarize_results,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run google prompt lever experiments with explicit transport settings.")
    parser.add_argument("--experiment-id", default="EXP-146")
    parser.add_argument("--template-spec-root", type=Path, default=DEFAULT_TEMPLATE_SPEC_ROOT)
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    parser.add_argument("--api-key-env", default="GEMINI_API_KEY")
    parser.add_argument("--timeout-sec", type=int, default=90)
    parser.add_argument("--max-retries", type=int, default=1)
    parser.add_argument("--retry-backoff-sec", type=float, default=3.0)
    args = parser.parse_args()

    experiment = get_experiment_definition(args.experiment_id)
    if experiment.model.provider != "google":
        raise ValueError(f"{args.experiment_id} is not a google-model experiment")

    args.artifact_root.mkdir(parents=True, exist_ok=True)
    context = load_experiment_context(args.template_spec_root, experiment.scenario)
    deterministic_bundle = build_deterministic_reference_bundle(args.template_spec_root, experiment.scenario)
    deterministic_evaluation = evaluate_copy_bundle(
        deterministic_bundle,
        experiment.scenario,
        context["template"],
        context["copy_rule"],
    )

    results: list[dict[str, object]] = [
        {
            "variant_id": "deterministic_reference",
            "lever_id": "reference",
            "changed_field": None,
            "description": "현재 production deterministic baseline 참조 결과입니다.",
            "provider": "deterministic",
            "model_name": "rule_based_copy_builder",
            "latency_ms": 0,
            "prompt": None,
            "request_meta": None,
            "output": deterministic_bundle,
            "evaluation": deterministic_evaluation,
            "scene_plan": None,
            "scene_plan_metrics": evaluate_scene_plan_preview(args.template_spec_root, experiment.scenario, deterministic_bundle),
            "korean_integrity": evaluate_korean_integrity(deterministic_bundle),
            "error": None,
        }
    ]

    variants = (experiment.baseline_variant, *experiment.candidate_variants)
    for variant in variants:
        prompt_package = build_prompt_package(args.template_spec_root, experiment.scenario, variant)
        started = time.perf_counter()
        try:
            response = generate_copy_bundle_with_google_model_with_meta(
                model=experiment.model,
                prompt_package=prompt_package,
                asset_paths=experiment.scenario.asset_paths,
                api_key_env=args.api_key_env,
                request_timeout_sec=args.timeout_sec,
                max_retries=args.max_retries,
                retry_backoff_sec=args.retry_backoff_sec,
            )
            output = response["output"]
            latency_ms = int((time.perf_counter() - started) * 1000)
            results.append(
                {
                    "variant_id": variant.variant_id,
                    "lever_id": variant.lever_id,
                    "changed_field": variant.changed_field,
                    "description": variant.description,
                    "provider": experiment.model.provider,
                    "model_name": experiment.model.model_name,
                    "latency_ms": latency_ms,
                    "prompt": prompt_package,
                    "request_meta": response["requestMeta"],
                    "output": output,
                    "evaluation": evaluate_copy_bundle(
                        output,
                        experiment.scenario,
                        context["template"],
                        context["copy_rule"],
                    ),
                    "scene_plan": None,
                    "scene_plan_metrics": evaluate_scene_plan_preview(args.template_spec_root, experiment.scenario, output),
                    "korean_integrity": evaluate_korean_integrity(output),
                    "error": None,
                }
            )
        except Exception as exc:  # noqa: BLE001
            latency_ms = int((time.perf_counter() - started) * 1000)
            sanitized_error = sanitize_error_message(str(exc))
            results.append(
                {
                    "variant_id": variant.variant_id,
                    "lever_id": variant.lever_id,
                    "changed_field": variant.changed_field,
                    "description": variant.description,
                    "provider": experiment.model.provider,
                    "model_name": experiment.model.model_name,
                    "latency_ms": latency_ms,
                    "prompt": prompt_package,
                    "request_meta": {
                        "provider": experiment.model.provider,
                        "modelName": experiment.model.model_name,
                        "timeoutSec": args.timeout_sec,
                        "maxRetries": args.max_retries,
                        "retryBackoffSec": args.retry_backoff_sec,
                        "attemptCount": None,
                        "retriesUsed": None,
                    },
                    "output": {},
                    "evaluation": {
                        "required_roles": [],
                        "region_slot_hits": 0,
                        "region_repeat_count": 0,
                        "detail_location_policy_id": None,
                        "detail_location_policy_surfaces": [],
                        "detail_location_leak_count": 0,
                        "detail_location_leaks_by_surface": {},
                        "audience_cue_count": 0,
                        "caption_count": 0,
                        "hashtag_count": 0,
                        "distinct_scene_lines": 0,
                        "failed_checks": [f"request failed: {sanitized_error}"],
                        "passed_checks": 0,
                        "score": 0.0,
                    },
                    "scene_plan": None,
                    "scene_plan_metrics": {
                        "scene_count": 0,
                        "max_text_per_scene": 0,
                        "over_limit_scene_ids": [],
                        "repeated_copy_scene_ids": [],
                        "closing_cta_actionable": False,
                        "headline_lengths": {},
                    },
                    "korean_integrity": empty_korean_integrity_metrics(),
                    "error": sanitized_error,
                }
            )

    artifact = {
        "experiment_id": experiment.experiment_id,
        "experiment_title": experiment.experiment_title,
        "objective": experiment.objective,
        "scenario": serialize_scenario(experiment.scenario),
        "model": asdict(experiment.model),
        "request_config": {
            "timeoutSec": args.timeout_sec,
            "maxRetries": args.max_retries,
            "retryBackoffSec": args.retry_backoff_sec,
        },
        "results": results,
        "comparison": summarize_results(results),
    }
    artifact_name = slugify(f"{experiment.experiment_id}-{experiment.experiment_title}-google-transport")
    artifact_path = args.artifact_root / f"{artifact_name}.json"
    artifact_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(artifact["comparison"], ensure_ascii=False, indent=2))
    print(f"artifact_path={artifact_path}")


if __name__ == "__main__":
    main()
