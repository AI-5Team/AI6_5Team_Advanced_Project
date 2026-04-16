from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from video_benchmark_common import SAMPLE_LIBRARY, infer_label, video_motion_metrics


EXP90_ROOT = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-90-upper-bound-video-benchmark"
DEFAULT_IMAGE = SAMPLE_LIBRARY["맥주"]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-92-sora2-input-framing-ovaat"
BASELINE_SUMMARY_PATH = EXP90_ROOT / "sora2" / "맥주" / "summary.json"
MANUAL_VEO_SUMMARY_PATH = EXP90_ROOT / "manual_veo" / "맥주" / "summary.json"


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_result(summary_path: Path, *, provider: str, variant_name: str) -> dict[str, object]:
    summary = read_json(summary_path)
    output_video = Path(str(summary["output_video"]))
    motion_metrics = summary.get("motion_metrics") or video_motion_metrics(output_video)
    return {
        "provider": provider,
        "variant": variant_name,
        "status": summary.get("status"),
        "summary_path": str(summary_path),
        "input_reference_image": summary.get("input_reference_image"),
        "output_video": str(output_video),
        "output_mid_frame": summary.get("output_mid_frame"),
        "contact_sheet": summary.get("contact_sheet"),
        "prompt": summary.get("prompt"),
        "mid_frame_metrics": summary.get("mid_frame_metrics"),
        "motion_metrics": motion_metrics,
        "elapsed_seconds": summary.get("elapsed_seconds"),
        "resolved_prepare_mode": summary.get("resolved_prepare_mode"),
    }


def compare_to_baseline(result: dict[str, object], baseline: dict[str, object]) -> dict[str, float | None]:
    baseline_mid = baseline.get("mid_frame_metrics") or {}
    baseline_motion = baseline.get("motion_metrics") or {}
    result_mid = result.get("mid_frame_metrics") or {}
    result_motion = result.get("motion_metrics") or {}

    def diff(current: object, base: object) -> float | None:
        if current is None or base is None:
            return None
        return round(float(current) - float(base), 2)

    return {
        "mid_frame_mse_delta": diff(result_mid.get("mse"), baseline_mid.get("mse")),
        "avg_rgb_diff_delta": diff(result_motion.get("avg_rgb_diff"), baseline_motion.get("avg_rgb_diff")),
        "avg_gray_diff_delta": diff(result_motion.get("avg_gray_diff"), baseline_motion.get("avg_gray_diff")),
    }


def zoom_crop(image: Image.Image, *, scale: float, y_bias: float) -> Image.Image:
    width, height = image.size
    crop_width = int(width * scale)
    crop_height = int(height * scale)
    center_x = width / 2
    center_y = height * (0.5 + y_bias)
    left = round(center_x - crop_width / 2)
    top = round(center_y - crop_height / 2)
    left = max(0, min(left, width - crop_width))
    top = max(0, min(top, height - crop_height))
    right = left + crop_width
    bottom = top + crop_height
    return image.crop((left, top, right, bottom)).resize((width, height), Image.Resampling.LANCZOS)


def build_framing_variants(prepared_input_path: Path, output_dir: Path) -> dict[str, Path]:
    source = Image.open(prepared_input_path).convert("RGB")
    variant_dir = output_dir / "prepared_variants"
    variant_dir.mkdir(parents=True, exist_ok=True)

    variants = {
        "hero_medium_zoom": zoom_crop(source, scale=0.9, y_bias=0.04),
        "hero_tight_zoom": zoom_crop(source, scale=0.8, y_bias=0.06),
    }

    paths: dict[str, Path] = {}
    for name, image in variants.items():
        path = variant_dir / f"{name}.png"
        image.save(path)
        paths[name] = path
    return paths


def run_sora_variant(
    image_path: Path,
    prepared_image_path: Path,
    output_dir: Path,
    variant_name: str,
    prompt: str,
    *,
    model: str,
    seconds: int,
) -> dict[str, object]:
    variant_root = output_dir / variant_name
    command = [
        "uv",
        "run",
        "--with",
        "openai",
        "python",
        str(REPO_ROOT / "scripts" / "hosted_video_sora2_first_try.py"),
        "--image",
        str(image_path),
        "--prepared-image",
        str(prepared_image_path),
        "--output-dir",
        str(variant_root),
        "--prompt",
        prompt,
        "--seconds",
        str(seconds),
        "--model",
        model,
    ]
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    summary_path = variant_root / infer_label(image_path) / "summary.json"
    result = read_result(summary_path, provider="sora2", variant_name=variant_name)
    result["returncode"] = completed.returncode
    if completed.returncode != 0:
        result["stdout"] = completed.stdout
        result["stderr"] = completed.stderr
    result["prepared_input_variant"] = str(prepared_image_path)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Sora 2 input framing OVAT for the beer sample.")
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--model", default="sora-2")
    parser.add_argument("--seconds", type=int, default=4)
    args = parser.parse_args()

    label = infer_label(args.image)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    baseline = read_result(BASELINE_SUMMARY_PATH, provider="sora2", variant_name="baseline_reused")
    manual_veo_reference = read_result(MANUAL_VEO_SUMMARY_PATH, provider="manual_veo", variant_name="manual_veo_reference")
    baseline_prompt = str(read_json(BASELINE_SUMMARY_PATH)["prompt"])
    baseline_prepared_input = Path(str(read_json(BASELINE_SUMMARY_PATH)["prepared_input"]))
    prepared_variants = build_framing_variants(baseline_prepared_input, args.output_dir)

    variants: dict[str, object] = {
        "baseline_reused": baseline,
        "manual_veo_reference": manual_veo_reference,
    }

    for variant_name, prepared_image_path in prepared_variants.items():
        result = run_sora_variant(
            args.image,
            prepared_image_path,
            args.output_dir,
            variant_name,
            baseline_prompt,
            model=args.model,
            seconds=args.seconds,
        )
        result["baseline_comparison"] = compare_to_baseline(result, baseline)
        variants[variant_name] = result

    summary = {
        "experiment_id": "EXP-92-sora2-input-framing-ovaat",
        "image": str(args.image),
        "label": label,
        "model": args.model,
        "seconds": args.seconds,
        "variants": variants,
    }
    write_json(args.output_dir / "summary.json", summary)
    print(args.output_dir / "summary.json")


if __name__ == "__main__":
    main()
