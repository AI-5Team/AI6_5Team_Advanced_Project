from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from video_quality_gate import annotate_benchmark_summary, evaluate_hybrid_source_gate


def test_hybrid_source_gate_accepts_preserve_pass_motion_hold_candidate() -> None:
    result = {
        "provider": "sora2_current_best",
        "status": "completed",
        "mid_frame_metrics": {"mse": 2898.03},
        "motion_metrics": {"avg_rgb_diff": 7.91},
    }

    gate = evaluate_hybrid_source_gate(result)

    assert gate["preserveStatus"] == "pass"
    assert gate["motionStatus"] == "hold"
    assert gate["serviceFitStatus"] == "hold"
    assert gate["decision"] == "accept"
    assert gate["role"] == "hybrid_source_candidate"


def test_hybrid_source_gate_marks_identity_drift_as_manual_review() -> None:
    result = {
        "provider": "sora2_current_best",
        "status": "completed",
        "mid_frame_metrics": {"mse": 3545.57},
        "motion_metrics": {"avg_rgb_diff": 21.04},
    }

    gate = evaluate_hybrid_source_gate(result)

    assert gate["preserveStatus"] == "hold"
    assert gate["motionStatus"] == "pass"
    assert gate["decision"] == "manual_review"


def test_hybrid_source_gate_rejects_large_identity_drift() -> None:
    result = {
        "provider": "manual_veo",
        "status": "completed",
        "mid_frame_metrics": {"mse": 7091.33},
        "motion_metrics": {"avg_rgb_diff": 14.55},
    }

    gate = evaluate_hybrid_source_gate(result)

    assert gate["preserveStatus"] == "fail"
    assert gate["decision"] == "reject"
    assert gate["role"] == "reference_only"


def test_annotate_benchmark_summary_collects_gate_counts() -> None:
    summary = {
        "benchmark_id": "EXP-TEST",
        "images": [
            {
                "label": "맥주",
                "providers": {
                    "product_control_motion": {
                        "provider": "product_control_motion",
                        "status": "completed",
                        "mid_frame_metrics": {"mse": 2514.74},
                        "motion_metrics": {"avg_rgb_diff": 7.43},
                        "packaging_fit": "native_control_candidate",
                    },
                    "sora2_current_best": {
                        "provider": "sora2_current_best",
                        "status": "completed",
                        "mid_frame_metrics": {"mse": 2898.03},
                        "motion_metrics": {"avg_rgb_diff": 7.91},
                    },
                },
            }
        ],
    }

    annotated = annotate_benchmark_summary(summary)

    assert annotated["images"][0]["providers"]["product_control_motion"]["hybrid_source_gate"]["decision"] == "native_control"
    assert annotated["images"][0]["providers"]["sora2_current_best"]["hybrid_source_gate"]["decision"] == "accept"
    assert annotated["hybrid_source_gate_summary"]["decisionCounts"] == {"native_control": 1, "accept": 1}
