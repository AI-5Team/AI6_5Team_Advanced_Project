from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from manual_review_decision import (
    apply_manual_review_decision,
    build_candidate_key,
    build_manual_review_packet,
    build_manual_review_packet_report,
    render_manual_review_decision_markdown,
)


def build_entry() -> dict:
    return {
        "benchmarkId": "EXP-239",
        "label": "규카츠",
        "provider": "sora2_current_best",
        "decision": "manual_review",
        "gateReason": "motion_is_usable_but_identity_review_is_needed",
        "reviewCategory": "promotion_candidate",
        "recommendedAction": "identity_review_then_promote_if_pass",
        "imagePath": "image.jpg",
        "sourceVideoPath": "video.mp4",
        "contactSheetPath": "contact.png",
        "summaryPath": "summary.json",
        "midFrameMse": 3545.57,
        "motionAvgRgbDiff": 21.04,
    }


def test_build_manual_review_packet_contains_checklist() -> None:
    packet = build_manual_review_packet(build_entry())

    assert packet["candidateKey"] == "EXP-239::규카츠::sora2_current_best"
    assert len(packet["checklist"]) == 5
    assert packet["suggestedFocus"] == ["peripheral_identity_drift", "high_motion_consistency"]


def test_build_manual_review_packet_report_collects_candidate_keys() -> None:
    packet_report = build_manual_review_packet_report({"entries": [build_entry()]})

    assert packet_report["entryCount"] == 1
    assert packet_report["candidateKeys"] == [build_candidate_key(build_entry())]


def test_apply_manual_review_decision_updates_statuses() -> None:
    packet = build_manual_review_packet(build_entry())

    decision = apply_manual_review_decision(
        packet,
        reviewer="codex",
        final_decision="hold",
        summary_note="주변 구성 drift는 남아 있어 보류",
        checklist_statuses={
            "main_subject_identity": "pass",
            "peripheral_layout": "hold",
            "text_qr_intrusion": "pass",
            "motion_packaging_fit": "pass",
            "promotion_readiness": "hold",
        },
        checklist_notes={
            "peripheral_layout": "프레이밍이 타이트해 주변 구성이 일부 잘립니다.",
        },
        decided_at="2026-04-14T15:30:00+09:00",
    )

    assert decision["finalDecision"] == "hold"
    assert decision["statusCounts"] == {"pass": 3, "hold": 2}
    assert decision["packet"]["checklist"][1]["notes"] == "프레이밍이 타이트해 주변 구성이 일부 잘립니다."


def test_render_manual_review_decision_markdown_contains_summary() -> None:
    packet = build_manual_review_packet(build_entry())
    decision = apply_manual_review_decision(
        packet,
        reviewer="codex",
        final_decision="hold",
        summary_note="contact sheet 기준으로는 추가 확인이 필요합니다.",
        checklist_statuses={"promotion_readiness": "hold"},
    )
    markdown = render_manual_review_decision_markdown(decision, experiment_id="EXP-249")

    assert "# EXP-249 Manual Review Decision" in markdown
    assert "summary note" in markdown
    assert "promotion_readiness" in markdown
