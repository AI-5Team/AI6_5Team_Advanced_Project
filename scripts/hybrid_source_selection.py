from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from manual_review_decision import build_candidate_key
from manual_review_registry import load_promoted_manual_review_registry
from video_quality_gate import annotate_benchmark_summary


REPO_ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_repo_path(path_value: str | Path | None) -> Path | None:
    if path_value is None:
        return None
    path = Path(path_value)
    return path if path.is_absolute() else (REPO_ROOT / path)


def _as_float(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def collect_hybrid_source_candidates(summary: dict[str, Any], *, label: str | None = None) -> list[dict[str, Any]]:
    annotate_benchmark_summary(summary)
    benchmark_id = str(summary.get("benchmark_id") or "")
    candidates: list[dict[str, Any]] = []

    for image_row in summary.get("images", []):
        if not isinstance(image_row, dict):
            continue
        image_label = str(image_row.get("label") or "")
        if label and image_label != label:
            continue
        providers = image_row.get("providers")
        if not isinstance(providers, dict):
            continue
        for provider_name, result in providers.items():
            if not isinstance(result, dict):
                continue
            gate = result.get("hybrid_source_gate")
            if not isinstance(gate, dict):
                continue
            output_video_path = resolve_repo_path(result.get("output_video"))
            if output_video_path is None:
                continue
            candidate = {
                "benchmarkId": benchmark_id,
                "label": image_label,
                "imagePath": resolve_repo_path(image_row.get("image")),
                "provider": str(provider_name),
                "decision": str(gate.get("decision") or ""),
                "gateReason": str(gate.get("reason") or ""),
                "role": str(gate.get("role") or ""),
                "sourceVideoPath": output_video_path,
                "contactSheetPath": resolve_repo_path(result.get("contact_sheet")),
                "summaryPath": resolve_repo_path(result.get("summary_path")),
                "midFrameMse": _as_float((result.get("mid_frame_metrics") or {}).get("mse")),
                "motionAvgRgbDiff": _as_float((result.get("motion_metrics") or {}).get("avg_rgb_diff")),
            }
            candidate["candidateKey"] = build_candidate_key(candidate)
            candidates.append(candidate)
    return candidates


def _sort_key(candidate: dict[str, Any]) -> tuple[int, float, float, str]:
    decision = str(candidate["decision"])
    decision_rank = 0 if decision == "accept" else 1
    return (
        decision_rank,
        -float(candidate["motionAvgRgbDiff"]),
        float(candidate["midFrameMse"]),
        str(candidate["provider"]),
    )


def select_hybrid_source_candidate(
    summary: dict[str, Any],
    *,
    label: str,
    provider: str | None = None,
    allow_manual_review: bool = False,
    manual_review_decisions_dir: Path | None = None,
) -> dict[str, Any]:
    candidates = collect_hybrid_source_candidates(summary, label=label)
    if provider:
        candidates = [candidate for candidate in candidates if candidate["provider"] == provider]
    candidates = [candidate for candidate in candidates if not str(candidate["provider"]).startswith("product_control")]
    if not candidates:
        raise ValueError(f"no hybrid source candidate found for label={label!r} provider={provider!r}")

    accepted = [candidate for candidate in candidates if candidate["decision"] == "accept"]
    manual_review = [candidate for candidate in candidates if candidate["decision"] == "manual_review"]
    promoted_registry = load_promoted_manual_review_registry(manual_review_decisions_dir) if manual_review_decisions_dir else {}
    promoted_manual_review = []
    for candidate in manual_review:
        promotion = promoted_registry.get(str(candidate["candidateKey"]))
        if promotion is None:
            continue
        promoted_manual_review.append(
            {
                **candidate,
                "reviewFinalDecision": promotion["finalDecision"],
                "reviewDecisionPath": promotion["decisionPath"],
                "reviewer": promotion["reviewer"],
                "reviewDecidedAt": promotion["decidedAt"],
            }
        )

    if accepted:
        return sorted(accepted, key=_sort_key)[0]
    if promoted_manual_review:
        return sorted(promoted_manual_review, key=_sort_key)[0]
    if allow_manual_review and manual_review:
        return sorted(manual_review, key=_sort_key)[0]

    decisions = sorted({str(candidate["decision"]) for candidate in candidates})
    raise ValueError(
        f"no accepted hybrid source candidate found for label={label!r} provider={provider!r}; available decisions={decisions}"
    )


def build_hybrid_source_selection_snapshot(candidate: dict[str, Any]) -> dict[str, Any]:
    selection_mode = "benchmark_gate"
    if candidate.get("reviewFinalDecision") == "promote":
        selection_mode = "promoted_manual_review"
    return {
        "selectionMode": selection_mode,
        "candidateKey": candidate.get("candidateKey"),
        "benchmarkId": candidate["benchmarkId"],
        "label": candidate["label"],
        "provider": candidate["provider"],
        "gateDecision": candidate["decision"],
        "gateReason": candidate["gateReason"],
        "role": candidate["role"],
        "reviewFinalDecision": candidate.get("reviewFinalDecision"),
        "reviewDecisionPath": candidate.get("reviewDecisionPath"),
        "reviewer": candidate.get("reviewer"),
        "reviewDecidedAt": candidate.get("reviewDecidedAt"),
        "imagePath": str(candidate["imagePath"]),
        "sourceVideoPath": str(candidate["sourceVideoPath"]),
        "contactSheetPath": str(candidate["contactSheetPath"]) if candidate["contactSheetPath"] else None,
        "summaryPath": str(candidate["summaryPath"]) if candidate["summaryPath"] else None,
        "midFrameMse": candidate["midFrameMse"],
        "motionAvgRgbDiff": candidate["motionAvgRgbDiff"],
    }
