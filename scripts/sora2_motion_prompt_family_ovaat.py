from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from video_benchmark_common import SAMPLE_LIBRARY, infer_label, video_motion_metrics


EXP90_ROOT = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-90-upper-bound-video-benchmark"
DEFAULT_IMAGE = SAMPLE_LIBRARY["맥주"]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-91-sora2-motion-prompt-family-ovaat"
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
        "output_video": str(output_video),
        "output_mid_frame": summary.get("output_mid_frame"),
        "contact_sheet": summary.get("contact_sheet"),
        "prompt": summary.get("prompt"),
        "mid_frame_metrics": summary.get("mid_frame_metrics"),
        "motion_metrics": motion_metrics,
        "elapsed_seconds": summary.get("elapsed_seconds"),
        "resolved_prepare_mode": summary.get("resolved_prepare_mode"),
    }


def build_motion_prompt_variants(label: str) -> dict[str, str]:
    if label != "맥주":
        raise ValueError("현재 EXP-91 스크립트는 맥주 샘플 전용으로 고정되어 있습니다.")

    return {
        "micro_motion_locked": (
            "Close-up beverage commercial shot of beer bottle and lager glass, product shape preserved, "
            "keep the bottle and glass positions fixed, keep the label readable, realistic liquid and glass details, "
            "continuous tiny carbonation bubbles rise through the beer, foam settles slightly over 4 seconds, "
            "small condensation highlights shimmer and slide subtly, locked-off tabletop composition, "
            "clearly visible product micro-motion without dramatic camera movement, bright tabletop lighting, "
            "premium beverage commercial realism, no object morphing, no duplicated glass or bottle, no extra props."
        ),
        "camera_orbit_beats": (
            "Close-up beverage commercial shot of beer bottle and lager glass, product shape preserved, "
            "keep bottle and glass positions consistent with the reference image, keep the label readable, "
            "realistic liquid and glass details, three clear motion beats over 4 seconds: bubbles rise, foam settles, "
            "a highlight rolls across the glass, slow controlled 10-degree camera orbit with a gentle push-in, "
            "visible but stable commercial motion, bright tabletop lighting, premium beverage commercial realism, "
            "no object morphing, no duplicated glass or bottle, no extra props."
        ),
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


def run_sora_variant(image_path: Path, output_dir: Path, variant_name: str, prompt: str, *, model: str, seconds: int) -> dict[str, object]:
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
        "--output-dir",
        str(variant_root),
        "--prompt",
        prompt,
        "--prepare-mode",
        "auto",
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
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Sora 2 motion prompt family OVAT for the beer sample.")
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--model", default="sora-2")
    parser.add_argument("--seconds", type=int, default=4)
    args = parser.parse_args()

    label = infer_label(args.image)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    baseline = read_result(BASELINE_SUMMARY_PATH, provider="sora2", variant_name="baseline_reused")
    manual_veo_reference = read_result(MANUAL_VEO_SUMMARY_PATH, provider="manual_veo", variant_name="manual_veo_reference")
    variants: dict[str, object] = {
        "baseline_reused": baseline,
        "manual_veo_reference": manual_veo_reference,
    }

    for variant_name, prompt in build_motion_prompt_variants(label).items():
        result = run_sora_variant(args.image, args.output_dir, variant_name, prompt, model=args.model, seconds=args.seconds)
        result["baseline_comparison"] = compare_to_baseline(result, baseline)
        variants[variant_name] = result

    summary = {
        "experiment_id": "EXP-91-sora2-motion-prompt-family-ovaat",
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
