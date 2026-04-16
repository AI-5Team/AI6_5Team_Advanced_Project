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
    generate_copy_bundle_with_google_model_with_meta,
    get_experiment_definition,
    get_model_comparison_definition,
    load_experiment_context,
    resolve_api_key_env,
    serialize_scenario,
)


def _load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _select_model(definition, provider: str, model_name: str):
    for model in definition.models:
        if model.provider == provider and model.model_name == model_name:
            return model
    raise ValueError(f"model not found in source experiment: {provider}:{model_name}")


def _select_prompt_variant(definition, variant_id: str):
    variants = (definition.baseline_variant, *definition.candidate_variants)
    for variant in variants:
        if variant.variant_id == variant_id:
            return variant
    raise ValueError(f"prompt variant not found in source experiment: {variant_id}")


def _resolve_profile(manifest: dict, profile_id: str | None) -> dict:
    if not profile_id:
        return {
            "profileId": "main",
            "label": "main_prompt_baseline",
            "sourceType": "model_comparison",
            "sourceExperimentId": manifest["sourceEvidence"]["comparisonExperimentId"],
            "selectedScenario": manifest["selectedScenario"],
            "selectedModel": manifest["selectedModel"],
            "evaluationPolicy": manifest["evaluationPolicy"],
            "snapshotExperimentId": "EXP-127",
            "snapshotExperimentTitle": "Prompt Baseline Freeze Snapshot",
            "snapshotArtifactName": "exp-127-prompt-baseline-freeze-snapshot.json",
            "usageGuidance": manifest.get("usageGuidance", []),
        }

    for option in manifest.get("baselineOptions", []):
        if option.get("profileId") == profile_id:
            return option
    raise ValueError(f"baseline option not found: {profile_id}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the current frozen prompt baseline as a single-model snapshot.")
    parser.add_argument(
        "--baseline-manifest",
        type=Path,
        default=ROOT_DIR / "packages" / "template-spec" / "manifests" / "prompt-baseline-v1.json",
    )
    parser.add_argument("--profile-id", default=None, help="Optional baseline option profile id defined in the manifest.")
    parser.add_argument("--template-spec-root", type=Path, default=DEFAULT_TEMPLATE_SPEC_ROOT)
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    parser.add_argument("--timeout-sec", type=int, default=None)
    parser.add_argument("--max-retries", type=int, default=0)
    parser.add_argument("--retry-backoff-sec", type=float, default=0.0)
    args = parser.parse_args()

    manifest = _load_manifest(args.baseline_manifest)
    profile = _resolve_profile(manifest, args.profile_id)
    source_experiment_id = profile["sourceExperimentId"]
    source_type = profile.get("sourceType", "model_comparison")

    if source_type == "model_comparison":
        definition = get_model_comparison_definition(source_experiment_id)
        prompt_variant = definition.prompt_variant
        selected_model = _select_model(
            definition,
            provider=profile["selectedModel"]["provider"],
            model_name=profile["selectedModel"]["modelName"],
        )
    elif source_type == "prompt_experiment":
        definition = get_experiment_definition(source_experiment_id)
        prompt_variant = _select_prompt_variant(definition, profile["promptVariantId"])
        selected_model = definition.model
        selected_model_name = profile["selectedModel"]["modelName"]
        selected_provider = profile["selectedModel"]["provider"]
        if selected_model.provider != selected_provider or selected_model.model_name != selected_model_name:
            raise ValueError(
                f"profile selectedModel does not match source prompt experiment model: "
                f"{selected_provider}:{selected_model_name}"
            )
    else:
        raise ValueError(f"unsupported sourceType: {source_type}")

    context = load_experiment_context(args.template_spec_root, definition.scenario)
    prompt_package = build_prompt_package(args.template_spec_root, definition.scenario, prompt_variant)
    deterministic_bundle = build_deterministic_reference_bundle(args.template_spec_root, definition.scenario)
    deterministic_evaluation = evaluate_copy_bundle(
        deterministic_bundle,
        definition.scenario,
        context["template"],
        context["copy_rule"],
    )

    started = time.perf_counter()
    request_meta = None
    if selected_model.provider == "google" and args.timeout_sec is not None:
        response = generate_copy_bundle_with_google_model_with_meta(
            model=selected_model,
            prompt_package=prompt_package,
            asset_paths=definition.scenario.asset_paths,
            api_key_env=resolve_api_key_env(selected_model.provider),
            request_timeout_sec=args.timeout_sec,
            max_retries=args.max_retries,
            retry_backoff_sec=args.retry_backoff_sec,
        )
        output = response["output"]
        request_meta = response["requestMeta"]
    else:
        output = generate_copy_bundle_with_model(
            model=selected_model,
            prompt_package=prompt_package,
            asset_paths=definition.scenario.asset_paths,
            api_key_env=resolve_api_key_env(selected_model.provider),
        )
    latency_ms = int((time.perf_counter() - started) * 1000)
    evaluation = evaluate_copy_bundle(output, definition.scenario, context["template"], context["copy_rule"])
    scene_plan_metrics = evaluate_scene_plan_preview(args.template_spec_root, definition.scenario, output)
    korean_integrity = evaluate_korean_integrity(output)

    required_score = float(profile["evaluationPolicy"]["requiredScore"])
    required_leaks = int(profile["evaluationPolicy"]["requiredDetailLocationLeakCount"])
    allow_over_limit = int(profile["evaluationPolicy"]["allowOverLimitSceneCount"])
    accepted = (
        float(evaluation["score"]) >= required_score
        and int(evaluation["detail_location_leak_count"]) <= required_leaks
        and len(scene_plan_metrics["over_limit_scene_ids"]) <= allow_over_limit
        and not evaluation["failed_checks"]
    )

    artifact = {
        "experiment_id": profile.get("snapshotExperimentId", "EXP-127"),
        "experiment_title": profile.get("snapshotExperimentTitle", "Prompt Baseline Freeze Snapshot"),
        "baseline_manifest_path": str(args.baseline_manifest),
        "baseline_manifest": manifest,
        "baseline_profile": profile,
        "source_experiment_id": source_experiment_id,
        "scenario": serialize_scenario(definition.scenario),
        "prompt_variant": {
            "variant_id": prompt_variant.variant_id,
            "lever_id": prompt_variant.lever_id,
            "changed_field": prompt_variant.changed_field,
            "description": prompt_variant.description,
        },
        "selected_model": {
            "provider": selected_model.provider,
            "model_name": selected_model.model_name,
        },
        "deterministic_reference": {
            "provider": "deterministic",
            "model_name": "rule_based_copy_builder",
            "evaluation": deterministic_evaluation,
        },
        "result": {
            "provider": selected_model.provider,
            "model_name": selected_model.model_name,
            "latency_ms": latency_ms,
            "request_meta": request_meta,
            "prompt": prompt_package,
            "output": output,
            "evaluation": evaluation,
            "scene_plan_metrics": scene_plan_metrics,
            "korean_integrity": korean_integrity,
        },
        "baseline_acceptance": {
            "accepted": accepted,
            "required_score": required_score,
            "required_detail_location_leak_count": required_leaks,
            "allow_over_limit_scene_count": allow_over_limit,
        },
    }

    artifact_root = args.artifact_root
    artifact_root.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_root / profile.get("snapshotArtifactName", "exp-127-prompt-baseline-freeze-snapshot.json")
    artifact_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(artifact["baseline_acceptance"], ensure_ascii=False, indent=2))
    print(f"artifact_path={artifact_path}")


if __name__ == "__main__":
    main()
