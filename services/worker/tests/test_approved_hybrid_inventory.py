from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from approved_hybrid_inventory import build_approved_hybrid_inventory_report


def write_summary(path: Path) -> Path:
    accepted_video = path.parent / "accepted.mp4"
    accepted_video.write_bytes(b"accept")
    review_video = path.parent / "review.mp4"
    review_video.write_bytes(b"review")
    payload = {
        "benchmark_id": "EXP-239",
        "images": [
            {
                "image": str(path.parent / "beer.jpg"),
                "label": "맥주",
                "providers": {
                    "sora2_current_best": {
                        "provider": "sora2_current_best",
                        "status": "completed",
                        "output_video": str(accepted_video),
                        "contact_sheet": str(path.parent / "accepted.png"),
                        "summary_path": str(path.parent / "accepted-summary.json"),
                        "mid_frame_metrics": {"mse": 2898.03},
                        "motion_metrics": {"avg_rgb_diff": 7.91},
                    }
                },
            },
            {
                "image": str(path.parent / "gyu.jpg"),
                "label": "규카츠",
                "providers": {
                    "sora2_current_best": {
                        "provider": "sora2_current_best",
                        "status": "completed",
                        "output_video": str(review_video),
                        "contact_sheet": str(path.parent / "review.png"),
                        "summary_path": str(path.parent / "review-summary.json"),
                        "mid_frame_metrics": {"mse": 3545.57},
                        "motion_metrics": {"avg_rgb_diff": 21.04},
                    }
                },
            },
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_promoted_decision(decisions_root: Path) -> None:
    candidate_key = "EXP-239::규카츠::sora2_current_best"
    decision_dir = decisions_root / "exp-239__규카츠__sora2_current_best"
    decision_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "candidateKey": candidate_key,
        "finalDecision": "promote",
        "reviewer": "codex",
        "decidedAt": "2026-04-14T16:20:00+09:00",
        "summaryNote": "approved",
        "packet": {
            "benchmarkId": "EXP-239",
            "label": "규카츠",
            "provider": "sora2_current_best",
            "decision": "manual_review",
            "gateReason": "identity_drift_requires_manual_review",
            "reviewCategory": "promotion_candidate",
            "sourceVideoPath": str(decisions_root / "review.mp4"),
            "contactSheetPath": str(decisions_root / "review.png"),
            "summaryPath": str(decisions_root / "review-summary.json"),
            "midFrameMse": 3545.57,
            "motionAvgRgbDiff": 21.04,
        },
    }
    (decision_dir / "decision.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def test_build_approved_hybrid_inventory_report_merges_accept_and_promote(tmp_path: Path) -> None:
    summary_path = write_summary(tmp_path / "summary.json")
    decisions_root = tmp_path / "decisions"
    decisions_root.mkdir(parents=True, exist_ok=True)
    write_promoted_decision(decisions_root)

    report = build_approved_hybrid_inventory_report([summary_path], decisions_root=decisions_root)

    assert report["itemCount"] == 2
    assert report["laneCounts"] == {"drink_glass_lane": 1, "tray_full_plate_lane": 1}
    assert report["approvalSourceCounts"] == {"benchmark_accept": 1, "manual_review_promote": 1}
    assert report["recommendedByLabel"]["맥주"]["approvalSource"] == "benchmark_accept"
    assert report["recommendedByLabel"]["규카츠"]["approvalSource"] == "manual_review_promote"
    assert report["recommendedByLane"]["tray_full_plate_lane"]["selectionMode"] == "promoted_manual_review"
