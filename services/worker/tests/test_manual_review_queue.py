from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from manual_review_queue import collect_manual_review_queue_entries, render_manual_review_queue_markdown, build_manual_review_queue_report
from video_quality_gate import annotate_benchmark_summary


def build_summary(tmp_path: Path) -> dict:
    review_video = tmp_path / "review.mp4"
    review_video.write_bytes(b"review")
    reference_video = tmp_path / "reference.mp4"
    reference_video.write_bytes(b"reference")

    summary = {
        "benchmark_id": "EXP-239",
        "images": [
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
                    "manual_veo": {
                        "provider": "manual_veo",
                        "status": "completed",
                        "output_video": str(reference_video),
                        "contact_sheet": str(tmp_path / "reference.png"),
                        "summary_path": str(tmp_path / "reference-summary.json"),
                        "mid_frame_metrics": {"mse": 5811.95},
                        "motion_metrics": {"avg_rgb_diff": 16.94},
                    },
                },
            }
        ],
    }
    annotate_benchmark_summary(summary)
    return summary


def test_collect_manual_review_queue_entries_filters_reference_only_by_default(tmp_path: Path) -> None:
    summary = build_summary(tmp_path)

    entries = collect_manual_review_queue_entries(summary)

    assert len(entries) == 1
    assert entries[0]["provider"] == "sora2_current_best"
    assert entries[0]["reviewCategory"] == "promotion_candidate"


def test_collect_manual_review_queue_entries_can_include_reference_only(tmp_path: Path) -> None:
    summary = build_summary(tmp_path)

    entries = collect_manual_review_queue_entries(summary, include_reference_only=True)

    assert len(entries) == 2
    assert {entry["reviewCategory"] for entry in entries} == {"promotion_candidate", "reference_only"}


def test_build_manual_review_queue_report_and_markdown(tmp_path: Path) -> None:
    summary = build_summary(tmp_path)

    report = build_manual_review_queue_report([summary], include_reference_only=True)
    markdown = render_manual_review_queue_markdown(report, experiment_id="EXP-248")

    assert report["entryCount"] == 2
    assert report["reviewCategoryCounts"] == {"promotion_candidate": 1, "reference_only": 1}
    assert "# EXP-248 Manual Review Queue" in markdown
    assert "identity_review_then_promote_if_pass" in markdown
