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
    generate_copy_bundle_with_google_model_with_meta,
    get_model_comparison_definition,
    load_experiment_context,
    sanitize_error_message,
    slugify,
)


TRANSPORT_PROFILES = (
    {
        "profile_id": "default_60s_no_retry",
        "label": "기본 60초 / retry 없음",
        "timeout_sec": 60,
        "max_retries": 0,
        "retry_backoff_sec": 0.0,
    },
    {
        "profile_id": "timeout_90s_retry1",
        "label": "90초 / retry 1회",
        "timeout_sec": 90,
        "max_retries": 1,
        "retry_backoff_sec": 3.0,
    },
    {
        "profile_id": "timeout_120s_retry1",
        "label": "120초 / retry 1회",
        "timeout_sec": 120,
        "max_retries": 1,
        "retry_backoff_sec": 5.0,
    },
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare Gemma transport timeout/retry profiles on a fixed model comparison prompt."
    )
    parser.add_argument("--experiment-id", default="EXP-144")
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--template-spec-root", type=Path, default=DEFAULT_TEMPLATE_SPEC_ROOT)
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    parser.add_argument("--api-key-env", default="GEMINI_API_KEY")
    args = parser.parse_args()

    experiment = get_model_comparison_definition(args.experiment_id)
    google_models = [model for model in experiment.models if model.provider == "google"]
    if not google_models:
        raise ValueError(f"{args.experiment_id} has no google model to check")
    if len(google_models) > 1:
        raise ValueError(f"{args.experiment_id} has multiple google models; expected exactly one")
    model = google_models[0]

    context = load_experiment_context(args.template_spec_root, experiment.scenario)
    prompt_package = build_prompt_package(args.template_spec_root, experiment.scenario, experiment.prompt_variant)

    deterministic_bundle = build_deterministic_reference_bundle(args.template_spec_root, experiment.scenario)
    deterministic_eval = evaluate_copy_bundle(
        deterministic_bundle,
        experiment.scenario,
        context["template"],
        context["copy_rule"],
    )

    results: list[dict[str, object]] = [
        {
            "transport_profile_id": "deterministic_reference",
            "run_index": 0,
            "provider": "deterministic",
            "model_name": "rule_based_copy_builder",
            "latency_ms": 0,
            "transport": None,
            "output": deterministic_bundle,
            "evaluation": deterministic_eval,
            "scene_plan_metrics": evaluate_scene_plan_preview(args.template_spec_root, experiment.scenario, deterministic_bundle),
            "korean_integrity": evaluate_korean_integrity(deterministic_bundle),
            "error": None,
        }
    ]

    for profile in TRANSPORT_PROFILES:
        for run_index in range(1, args.repeat + 1):
            started = time.perf_counter()
            try:
                response = generate_copy_bundle_with_google_model_with_meta(
                    model=model,
                    prompt_package=prompt_package,
                    asset_paths=experiment.scenario.asset_paths,
                    api_key_env=args.api_key_env,
                    request_timeout_sec=profile["timeout_sec"],
                    max_retries=profile["max_retries"],
                    retry_backoff_sec=profile["retry_backoff_sec"],
                )
                output = response["output"]
                latency_ms = int((time.perf_counter() - started) * 1000)
                results.append(
                    {
                        "transport_profile_id": profile["profile_id"],
                        "run_index": run_index,
                        "provider": model.provider,
                        "model_name": model.model_name,
                        "latency_ms": latency_ms,
                        "transport": response["requestMeta"],
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
                        "transport_profile_id": profile["profile_id"],
                        "run_index": run_index,
                        "provider": model.provider,
                        "model_name": model.model_name,
                        "latency_ms": latency_ms,
                        "transport": {
                            "provider": model.provider,
                            "modelName": model.model_name,
                            "timeoutSec": profile["timeout_sec"],
                            "maxRetries": profile["max_retries"],
                            "retryBackoffSec": profile["retry_backoff_sec"],
                            "attemptCount": None,
                            "retriesUsed": None,
                        },
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

    summary: list[dict[str, object]] = []
    for profile in TRANSPORT_PROFILES:
        rows = [row for row in results if row["transport_profile_id"] == profile["profile_id"]]
        success_rows = [row for row in rows if not row["error"]]
        avg_score = round(sum(float(row["evaluation"]["score"]) for row in rows) / max(1, len(rows)), 1)
        avg_attempt_count = None
        if success_rows:
            avg_attempt_count = round(
                sum(int((row["transport"] or {}).get("attemptCount") or 0) for row in success_rows) / len(success_rows),
                2,
            )
        timeout_fail_count = sum(1 for row in rows if row["error"] and "timed out" in str(row["error"]).lower())
        summary.append(
            {
                "transport_profile_id": profile["profile_id"],
                "label": profile["label"],
                "timeout_sec": profile["timeout_sec"],
                "max_retries": profile["max_retries"],
                "run_count": len(rows),
                "success_count": len(success_rows),
                "timeout_fail_count": timeout_fail_count,
                "avg_score": avg_score,
                "avg_attempt_count": avg_attempt_count,
                "all_runs_passed": len(success_rows) == len(rows)
                and all(not row["evaluation"]["failed_checks"] for row in success_rows),
                "sample_hooks": [row["output"].get("hookText") for row in success_rows],
            }
        )

    artifact = {
        "experiment_id": "EXP-145",
        "experiment_title": "Gemma Promotion Strict Anchor Transport Profile Check",
        "source_experiment_id": args.experiment_id,
        "repeat": args.repeat,
        "scenario": {
            "scenario_id": experiment.scenario.scenario_id,
            "template_id": experiment.scenario.template_id,
            "style_id": experiment.scenario.style_id,
            "purpose": experiment.scenario.purpose,
        },
        "prompt_variant": {
            "variant_id": experiment.prompt_variant.variant_id,
            "description": experiment.prompt_variant.description,
        },
        "model": {
            "provider": model.provider,
            "model_name": model.model_name,
        },
        "transport_profiles": TRANSPORT_PROFILES,
        "summary": summary,
        "results": results,
    }

    args.artifact_root.mkdir(parents=True, exist_ok=True)
    artifact_path = args.artifact_root / f"{slugify('EXP-145-gemma-promotion-strict-anchor-transport-profile-check')}.json"
    artifact["artifact_path"] = str(artifact_path)
    artifact_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"artifact_path={artifact_path}")


if __name__ == "__main__":
    main()
