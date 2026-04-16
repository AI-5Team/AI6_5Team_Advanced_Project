from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from services.worker.renderers.media import create_scene_overlay_image, render_hybrid_video
from services.worker.utils.runtime import ensure_dir
from video_benchmark_common import create_contact_sheet, write_json


DEFAULT_SOURCE_VIDEO = (
    REPO_ROOT
    / "docs"
    / "experiments"
    / "artifacts"
    / "exp-241-sora2-gyukatsu-input-framing-live-ovaat"
    / "baseline_auto"
    / "규카츠"
    / "sora2_first_try.mp4"
)
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-243-generated-video-hybrid-packaging-proof"

def main() -> None:
    parser = argparse.ArgumentParser(description="Overlay template packaging on top of a generated video clip.")
    parser.add_argument("--source-video", type=Path, default=DEFAULT_SOURCE_VIDEO)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--experiment-id", default="EXP-243-generated-video-hybrid-packaging-proof")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    overlays_dir = args.output_dir / "overlays"
    ensure_dir(overlays_dir)

    overlay_specs = [
        (
            overlays_dir / "scene1_hook.png",
            "HOOK",
            "규카츠 비주얼 바로 꽂기",
            "생성컷 위에 템플릿 훅을 먼저 얹기",
            0.0,
            1.3,
        ),
        (
            overlays_dir / "scene2_detail.png",
            "DETAIL",
            "튀김 결이랑 단면 강조",
            "메뉴 정체성은 유지하고 설명만 추가",
            1.3,
            2.6,
        ),
        (
            overlays_dir / "scene3_cta.png",
            "CTA",
            "지금 바로 저장 말고 방문",
            "생성컷도 패키징 안에서 광고처럼 마무리",
            2.6,
            4.0,
        ),
    ]

    overlays_for_ffmpeg: list[tuple[Path, float, float]] = []
    for path, badge, title, body, start_sec, end_sec in overlay_specs:
        create_scene_overlay_image(path, title, body, "b_grade_fun", badge_text=badge)
        overlays_for_ffmpeg.append((path, start_sec, end_sec))

    output_video = args.output_dir / "hybrid_packaged.mp4"
    render_hybrid_video(args.source_video, overlays_for_ffmpeg, output_video)
    contact_sheet = create_contact_sheet(output_video, args.output_dir / "hybrid_contact_sheet.png")

    summary = {
        "experiment_id": args.experiment_id,
        "source_video": str(args.source_video),
        "output_video": str(output_video),
        "contact_sheet": str(contact_sheet),
        "overlays": [
            {
                "path": str(path),
                "start_sec": start_sec,
                "end_sec": end_sec,
            }
            for path, start_sec, end_sec in overlays_for_ffmpeg
        ],
        "hypothesis": "generated shot에 template overlay를 얹으면 service fit이 개선되는가",
    }
    write_json(args.output_dir / "summary.json", summary)
    print(args.output_dir / "summary.json")


if __name__ == "__main__":
    main()
