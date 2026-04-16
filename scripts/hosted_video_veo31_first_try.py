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
    write_json,
)


DEFAULT_IMAGE = REPO_ROOT / "docs" / "sample" / "음식사진샘플(규카츠).jpg"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-90-upper-bound-video-benchmark" / "veo31"


def main() -> None:
    load_repo_env()
    parser = argparse.ArgumentParser(description="Run a Veo 3.1 image-to-video first try for upper-bound benchmarking.")
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--model", default="veo-3.1-generate-preview")
    parser.add_argument("--width", type=int, default=720)
    parser.add_argument("--height", type=int, default=405)
    parser.add_argument("--aspect-ratio", default="16:9")
    parser.add_argument("--duration-seconds", type=int, default=4)
    parser.add_argument("--resolution", default="720p")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--poll-interval-sec", type=int, default=10)
    parser.add_argument("--timeout-sec", type=int, default=420)
    parser.add_argument(
        "--prepare-mode",
        default="auto",
        choices=["cover_center", "cover_top", "cover_bottom", "contain_blur", "auto"],
    )
    parser.add_argument("--prompt", default=None)
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:  # pragma: no cover - runtime dependency path
        raise SystemExit("google-genai가 필요합니다. `uv run --with google-genai ...` 형태로 실행해 주세요.") from exc

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("GEMINI_API_KEY가 설정되어 있지 않습니다.")

    label = infer_label(args.image)
    run_dir = args.output_dir / label
    run_dir.mkdir(parents=True, exist_ok=True)

    resolved_prepare_mode = resolve_prepare_mode(args.image, args.prepare_mode)
    prompt = args.prompt or build_upper_bound_prompt(args.image)
    prepared_input_path = run_dir / "prepared_input.png"
    output_video_path = run_dir / "veo31_first_try.mp4"
    summary_path = run_dir / "summary.json"
    image = prepare_image(args.image, args.width, args.height, resolved_prepare_mode)
    image.save(prepared_input_path)

    artifact: dict[str, object] = {
        "provider": "veo31",
        "image": str(args.image),
        "label": label,
        "prepared_input": str(prepared_input_path),
        "model": args.model,
        "prompt": prompt,
        "negative_prompt": DEFAULT_NEGATIVE_PROMPT,
        "prepare_mode": args.prepare_mode,
        "resolved_prepare_mode": resolved_prepare_mode,
        "aspect_ratio": args.aspect_ratio,
        "resolution": args.resolution,
        "duration_seconds": args.duration_seconds,
        "seed": args.seed,
        "status": "started",
        "output_video": str(output_video_path),
    }

    started_at = time.perf_counter()
    try:
        client = genai.Client(api_key=api_key)
        operation = client.models.generate_videos(
            model=args.model,
            prompt=prompt,
            image=types.Image.from_file(location=str(prepared_input_path), mime_type="image/png"),
            config=types.GenerateVideosConfig(
                aspectRatio=args.aspect_ratio,
                durationSeconds=args.duration_seconds,
                resolution=args.resolution,
                negativePrompt=DEFAULT_NEGATIVE_PROMPT,
            ),
        )
        artifact["operation_name"] = getattr(operation, "name", None)
        waited_seconds = 0
        while not operation.done:
            if waited_seconds >= args.timeout_sec:
                raise TimeoutError(f"Veo generation timed out after {args.timeout_sec} seconds")
            time.sleep(args.poll_interval_sec)
            waited_seconds += args.poll_interval_sec
            operation = client.operations.get(operation)

        response = operation.response
        generated_video = response.generated_videos[0]
        video_bytes = client.files.download(file=generated_video.video)
        output_video_path.write_bytes(video_bytes)
        midpoint_seconds = max(args.duration_seconds / 2, 0.1)
        first_frame_path, mid_frame_path = extract_video_frames(output_video_path, run_dir, midpoint_seconds)
        contact_sheet_path = create_contact_sheet(output_video_path, run_dir / "contact_sheet.png")

        artifact["status"] = "completed"
        artifact["output_first_frame"] = str(first_frame_path)
        artifact["output_mid_frame"] = str(mid_frame_path)
        artifact["contact_sheet"] = str(contact_sheet_path)
        artifact["first_frame_metrics"] = image_metrics(prepared_input_path, first_frame_path)
        artifact["mid_frame_metrics"] = image_metrics(prepared_input_path, mid_frame_path)
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
