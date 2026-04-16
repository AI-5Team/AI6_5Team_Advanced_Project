from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from services.common.env_loader import load_repo_env
from video_benchmark_common import (
    DEFAULT_NEGATIVE_PROMPT,
    build_upper_bound_prompt,
    create_contact_sheet,
    extract_video_frames,
    image_metrics,
    infer_label,
    prepare_image,
    resolve_prepare_mode,
    video_motion_metrics,
    write_json,
)


DEFAULT_IMAGE = REPO_ROOT / "docs" / "sample" / "음식사진샘플(규카츠).jpg"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-90-upper-bound-video-benchmark" / "sora2"


def main() -> None:
    load_repo_env()
    parser = argparse.ArgumentParser(description="Run a Sora 2 image-to-video first try for upper-bound benchmarking.")
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--prepared-image", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--model", default="sora-2")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--seconds", type=int, default=4)
    parser.add_argument(
        "--prepare-mode",
        default="auto",
        choices=["cover_center", "cover_top", "cover_bottom", "contain_blur", "auto"],
    )
    parser.add_argument("--poll-interval-ms", type=int, default=5000)
    parser.add_argument("--prompt", default=None)
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover - runtime dependency path
        raise SystemExit("openai 패키지가 필요합니다. `uv run --with openai ...` 형태로 실행해 주세요.") from exc

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("OPENAI_API_KEY가 설정되어 있지 않습니다.")

    input_image_path = args.prepared_image or args.image
    label = infer_label(args.image)
    run_dir = args.output_dir / label
    run_dir.mkdir(parents=True, exist_ok=True)

    resolved_prepare_mode = "preprepared" if args.prepared_image else resolve_prepare_mode(args.image, args.prepare_mode)
    prompt = args.prompt or build_upper_bound_prompt(args.image)
    prepared_input_path = run_dir / "prepared_input.png"
    output_video_path = run_dir / "sora2_first_try.mp4"
    summary_path = run_dir / "summary.json"
    if args.prepared_image:
        image = prepare_image(input_image_path, args.width, args.height, "cover_center")
        image.save(prepared_input_path)
    else:
        image = prepare_image(args.image, args.width, args.height, resolved_prepare_mode)
        image.save(prepared_input_path)

    artifact: dict[str, object] = {
        "provider": "sora2",
        "image": str(args.image),
        "input_reference_image": str(input_image_path),
        "label": label,
        "prepared_input": str(prepared_input_path),
        "model": args.model,
        "prompt": prompt,
        "negative_prompt": DEFAULT_NEGATIVE_PROMPT,
        "prepare_mode": args.prepare_mode,
        "resolved_prepare_mode": resolved_prepare_mode,
        "seconds": args.seconds,
        "size": f"{args.width}x{args.height}",
        "status": "started",
        "output_video": str(output_video_path),
    }

    started_at = time.perf_counter()
    try:
        client = OpenAI(api_key=api_key)
        with prepared_input_path.open("rb") as image_file:
            video = client.videos.create_and_poll(
                model=args.model,
                prompt=prompt,
                input_reference=image_file,
                seconds=args.seconds,
                size=f"{args.width}x{args.height}",
                poll_interval_ms=args.poll_interval_ms,
            )
        artifact["video_id"] = getattr(video, "id", None)
        artifact["raw_status"] = getattr(video, "status", None)
        video_id = artifact["video_id"]
        if not video_id:
            raise RuntimeError("Sora response did not include a video id.")

        content = client.videos.download_content(video_id)
        content.write_to_file(output_video_path)
        midpoint_seconds = max(args.seconds / 2, 0.1)
        first_frame_path, mid_frame_path = extract_video_frames(output_video_path, run_dir, midpoint_seconds)
        contact_sheet_path = create_contact_sheet(output_video_path, run_dir / "contact_sheet.png")

        artifact["status"] = "completed"
        artifact["output_first_frame"] = str(first_frame_path)
        artifact["output_mid_frame"] = str(mid_frame_path)
        artifact["contact_sheet"] = str(contact_sheet_path)
        artifact["first_frame_metrics"] = image_metrics(prepared_input_path, first_frame_path)
        artifact["mid_frame_metrics"] = image_metrics(prepared_input_path, mid_frame_path)
        artifact["motion_metrics"] = video_motion_metrics(output_video_path)
    except Exception as exc:
        artifact["status"] = "failed"
        artifact["error_type"] = exc.__class__.__name__
        artifact["error"] = str(exc)
    finally:
        artifact["elapsed_seconds"] = round(time.perf_counter() - started_at, 2)
        write_json(summary_path, artifact)
        print(summary_path)


if __name__ == "__main__":
    main()
