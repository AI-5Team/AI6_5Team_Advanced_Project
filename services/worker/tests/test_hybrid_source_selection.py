from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from manual_review_decision import apply_manual_review_decision, build_manual_review_packet
from hybrid_source_selection import build_hybrid_source_selection_snapshot, collect_hybrid_source_candidates, select_hybrid_source_candidate
from video_quality_gate import annotate_benchmark_summary


def build_summary(tmp_path: Path) -> dict:
    accepted_video = tmp_path / "accepted.mp4"
    accepted_video.write_bytes(b"accept")
    review_video = tmp_path / "review.mp4"
    review_video.write_bytes(b"review")

    summary = {
        "benchmark_id": "EXP-239",
        "images": [
            {
                "image": str(tmp_path / "beer.jpg"),
                "label": "맥주",
                "providers": {
                    "product_control_motion": {
                        "provider": "product_control_motion",
                        "status": "completed",
                        "output_video": str(tmp_path / "control.mp4"),
                        "packaging_fit": "native_control_candidate",
                        "mid_frame_metrics": {"mse": 2514.74},
                        "motion_metrics": {"avg_rgb_diff": 7.43},
                    },
                    "sora2_current_best": {
                        "provider": "sora2_current_best",
                        "status": "completed",
                        "output_video": str(accepted_video),
                        "contact_sheet": str(tmp_path / "accepted.png"),
                        "summary_path": str(tmp_path / "accepted-summary.json"),
                        "mid_frame_metrics": {"mse": 2898.03},
                        "motion_metrics": {"avg_rgb_diff": 7.91},
                    },
                },
            },
            {
                "image": str(tmp_path / "gyu.jpg"),
                "label": "규카츠",
                "providers": {
                    "sora2_current_best": {
                        "provider": "sora2_current_best",
                        "status": "completed",
                        "output_video": str(review_video),
                        "contact_sheet": str(tmp_path / "review.png"),
                        "summary_path": str(tmp_path / "review-summary.json"),
                        "mid_frame_metrics": {"mse": 3545.57},
                        "motion_metrics": {"avg_rgb_diff": 21.04},
                    },
                },
            },
        ],
    }
    annotate_benchmark_summary(summary)
    return summary


def test_collect_hybrid_source_candidates_filters_label(tmp_path: Path) -> None:
    summary = build_summary(tmp_path)

    candidates = collect_hybrid_source_candidates(summary, label="맥주")

    assert len(candidates) == 2
    assert {candidate["provider"] for candidate in candidates} == {"product_control_motion", "sora2_current_best"}


def test_select_hybrid_source_candidate_prefers_accept(tmp_path: Path) -> None:
    summary = build_summary(tmp_path)

    candidate = select_hybrid_source_candidate(summary, label="맥주")

    assert candidate["provider"] == "sora2_current_best"
    assert candidate["decision"] == "accept"


def test_select_hybrid_source_candidate_blocks_manual_review_without_flag(tmp_path: Path) -> None:
    summary = build_summary(tmp_path)

    try:
        select_hybrid_source_candidate(summary, label="규카츠")
    except ValueError as exc:
        assert "no accepted hybrid source candidate found" in str(exc)
    else:
        raise AssertionError("manual review candidate should not be auto-selected without explicit opt-in")


def test_select_hybrid_source_candidate_allows_manual_review_with_flag(tmp_path: Path) -> None:
    summary = build_summary(tmp_path)

    candidate = select_hybrid_source_candidate(summary, label="규카츠", allow_manual_review=True)
    snapshot = build_hybrid_source_selection_snapshot(candidate)

    assert candidate["decision"] == "manual_review"
    assert snapshot["gateDecision"] == "manual_review"
    assert snapshot["provider"] == "sora2_current_best"


def test_select_hybrid_source_candidate_accepts_promoted_manual_review(tmp_path: Path) -> None:
    summary = build_summary(tmp_path)
    decisions_root = tmp_path / "decisions"
    candidate = select_hybrid_source_candidate(summary, label="규카츠", allow_manual_review=True)
    packet = build_manual_review_packet(
        {
            "benchmarkId": candidate["benchmarkId"],
            "label": candidate["label"],
            "provider": candidate["provider"],
            "decision": candidate["decision"],
            "gateReason": candidate["gateReason"],
            "reviewCategory": "promotion_candidate",
            "recommendedAction": "identity_review_then_promote_if_pass",
            "imagePath": str(candidate["imagePath"]),
            "sourceVideoPath": str(candidate["sourceVideoPath"]),
            "contactSheetPath": str(candidate["contactSheetPath"]),
            "summaryPath": str(candidate["summaryPath"]),
            "midFrameMse": candidate["midFrameMse"],
            "motionAvgRgbDiff": candidate["motionAvgRgbDiff"],
        }
    )
    decision = apply_manual_review_decision(
        packet,
        reviewer="codex",
        final_decision="promote",
        summary_note="승격 허용",
        checklist_statuses={
            "main_subject_identity": "pass",
            "peripheral_layout": "pass",
            "text_qr_intrusion": "pass",
            "motion_packaging_fit": "pass",
            "promotion_readiness": "pass",
        },
        decided_at="2026-04-14T16:00:00+09:00",
    )
    decision_dir = decisions_root / "candidate"
    decision_dir.mkdir(parents=True, exist_ok=True)
    (decision_dir / "decision.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")

    promoted = select_hybrid_source_candidate(summary, label="규카츠", manual_review_decisions_dir=decisions_root)
    snapshot = build_hybrid_source_selection_snapshot(promoted)

    assert promoted["reviewFinalDecision"] == "promote"
    assert snapshot["selectionMode"] == "promoted_manual_review"
    assert snapshot["reviewDecisionPath"] is not None


def test_select_hybrid_source_candidate_keeps_hold_manual_review_blocked(tmp_path: Path) -> None:
    summary = build_summary(tmp_path)
    decisions_root = tmp_path / "decisions"
    candidate = select_hybrid_source_candidate(summary, label="규카츠", allow_manual_review=True)
    packet = build_manual_review_packet(
        {
            "benchmarkId": candidate["benchmarkId"],
            "label": candidate["label"],
            "provider": candidate["provider"],
            "decision": candidate["decision"],
            "gateReason": candidate["gateReason"],
            "reviewCategory": "promotion_candidate",
            "recommendedAction": "identity_review_then_promote_if_pass",
            "imagePath": str(candidate["imagePath"]),
            "sourceVideoPath": str(candidate["sourceVideoPath"]),
            "contactSheetPath": str(candidate["contactSheetPath"]),
            "summaryPath": str(candidate["summaryPath"]),
            "midFrameMse": candidate["midFrameMse"],
            "motionAvgRgbDiff": candidate["motionAvgRgbDiff"],
        }
    )
    decision = apply_manual_review_decision(
        packet,
        reviewer="codex",
        final_decision="hold",
        summary_note="보류",
        checklist_statuses={"promotion_readiness": "hold"},
        decided_at="2026-04-14T16:05:00+09:00",
    )
    decision_dir = decisions_root / "candidate"
    decision_dir.mkdir(parents=True, exist_ok=True)
    (decision_dir / "decision.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")

    try:
        select_hybrid_source_candidate(summary, label="규카츠", manual_review_decisions_dir=decisions_root)
    except ValueError as exc:
        assert "no accepted hybrid source candidate found" in str(exc)
    else:
        raise AssertionError("hold manual review candidate should remain blocked")
