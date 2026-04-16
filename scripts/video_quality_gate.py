from __future__ import annotations

from typing import Any


PRESERVE_PASS_MAX_MSE = 3000.0
PRESERVE_HOLD_MAX_MSE = 6500.0
MOTION_HOLD_MIN_AVG_RGB_DIFF = 6.5
MOTION_PASS_MIN_AVG_RGB_DIFF = 10.0


def _get_float(source: dict[str, Any], key: str) -> float | None:
    value = source.get(key)
    if isinstance(value, (int, float)):
        return float(value)
    return None


def evaluate_hybrid_source_gate(result: dict[str, Any]) -> dict[str, Any]:
    status = str(result.get("status") or "")
    provider = str(result.get("provider") or "")
    packaging_fit = str(result.get("packaging_fit") or "")
    mid_frame_metrics = result.get("mid_frame_metrics") if isinstance(result.get("mid_frame_metrics"), dict) else {}
    motion_metrics = result.get("motion_metrics") if isinstance(result.get("motion_metrics"), dict) else {}
    mse = _get_float(mid_frame_metrics, "mse")
    avg_rgb_diff = _get_float(motion_metrics, "avg_rgb_diff")

    if status != "completed":
        return {
            "decision": "reject",
            "reason": "generation_not_completed",
            "preserveStatus": "fail",
            "motionStatus": "fail",
            "serviceFitStatus": "fail",
            "role": "not_usable",
            "metrics": {"mse": mse, "avgRgbDiff": avg_rgb_diff},
            "thresholds": {
                "preservePassMaxMse": PRESERVE_PASS_MAX_MSE,
                "preserveHoldMaxMse": PRESERVE_HOLD_MAX_MSE,
                "motionHoldMinAvgRgbDiff": MOTION_HOLD_MIN_AVG_RGB_DIFF,
                "motionPassMinAvgRgbDiff": MOTION_PASS_MIN_AVG_RGB_DIFF,
            },
        }

    if mse is None:
        preserve_status = "hold"
        preserve_reason = "missing_mid_frame_mse"
    elif mse <= PRESERVE_PASS_MAX_MSE:
        preserve_status = "pass"
        preserve_reason = "identity_drift_within_pass_band"
    elif mse <= PRESERVE_HOLD_MAX_MSE:
        preserve_status = "hold"
        preserve_reason = "identity_drift_requires_manual_review"
    else:
        preserve_status = "fail"
        preserve_reason = "identity_drift_exceeds_gate"

    if avg_rgb_diff is None:
        motion_status = "hold"
        motion_reason = "missing_motion_metric"
    elif avg_rgb_diff < MOTION_HOLD_MIN_AVG_RGB_DIFF:
        motion_status = "fail"
        motion_reason = "motion_too_close_to_static"
    elif avg_rgb_diff < MOTION_PASS_MIN_AVG_RGB_DIFF:
        motion_status = "hold"
        motion_reason = "motion_visible_but_not_strong"
    else:
        motion_status = "pass"
        motion_reason = "motion_strong_enough_for_shortform"

    if packaging_fit.startswith("native_control") or provider.startswith("product_control"):
        service_fit_status = "pass"
        decision = "native_control"
        role = "fallback_baseline"
        decision_reason = "already_packaged_in_native_control_lane"
    elif preserve_status == "fail" or motion_status == "fail":
        service_fit_status = "fail"
        decision = "reject"
        role = "reference_only" if provider.startswith("manual_") else "not_promoted"
        decision_reason = "failed_preserve_or_motion_minimum"
    else:
        service_fit_status = "hold"
        if preserve_status == "pass":
            decision = "accept"
            role = "hybrid_source_candidate"
            decision_reason = "eligible_for_hybrid_packaging_lane"
        else:
            decision = "manual_review"
            role = "reference_only" if provider.startswith("manual_") else "hybrid_source_candidate"
            decision_reason = "motion_is_usable_but_identity_review_is_needed"

    return {
        "decision": decision,
        "reason": decision_reason,
        "preserveStatus": preserve_status,
        "preserveReason": preserve_reason,
        "motionStatus": motion_status,
        "motionReason": motion_reason,
        "serviceFitStatus": service_fit_status,
        "role": role,
        "metrics": {"mse": mse, "avgRgbDiff": avg_rgb_diff},
        "thresholds": {
            "preservePassMaxMse": PRESERVE_PASS_MAX_MSE,
            "preserveHoldMaxMse": PRESERVE_HOLD_MAX_MSE,
            "motionHoldMinAvgRgbDiff": MOTION_HOLD_MIN_AVG_RGB_DIFF,
            "motionPassMinAvgRgbDiff": MOTION_PASS_MIN_AVG_RGB_DIFF,
        },
    }


def annotate_benchmark_summary(summary: dict[str, Any]) -> dict[str, Any]:
    images = summary.get("images")
    if not isinstance(images, list):
        return summary

    decision_counts: dict[str, int] = {}
    provider_decision_counts: dict[str, dict[str, int]] = {}

    for row in images:
        if not isinstance(row, dict):
            continue
        providers = row.get("providers")
        if not isinstance(providers, dict):
            continue
        for provider_name, result in providers.items():
            if not isinstance(result, dict):
                continue
            gate = evaluate_hybrid_source_gate(result)
            result["hybrid_source_gate"] = gate
            decision = str(gate["decision"])
            decision_counts[decision] = decision_counts.get(decision, 0) + 1
            provider_counts = provider_decision_counts.setdefault(str(provider_name), {})
            provider_counts[decision] = provider_counts.get(decision, 0) + 1

    summary["hybrid_source_gate_summary"] = {
        "decisionCounts": decision_counts,
        "providerDecisionCounts": provider_decision_counts,
    }
    return summary
