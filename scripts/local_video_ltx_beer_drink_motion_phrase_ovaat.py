from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = REPO_ROOT / "docs" / "sample" / "음식사진샘플(맥주).jpg"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-78-local-ltx-beer-drink-motion-phrase-ovaat"
DEFAULT_NEGATIVE_PROMPT = "worst quality, blurry, jittery, distorted, warped, overexposed, text, watermark"
DEFAULT_SEED = 7
BASELINE_PROMPT = "beer bottle and lager glass, bright tabletop lighting, realistic drink commercial motion, static close-up, minimal camera movement"
VARIANT_PROMPT = "beer bottle and lager glass, bright tabletop lighting, still life beverage shot, static close-up, minimal camera movement"


def image_metrics(input_path: Path, compare_path: Path) -> dict[str, float]:
    source = np.asarray(Image.open(input_path).convert("RGB"), dtype=np.float32)
    target = np.asarray(Image.open(compare_path).convert("RGB"), dtype=np.float32)
    source_gray = np.asarray(Image.open(input_path).convert("L"), dtype=np.float32)
    target_gray = np.asarray(Image.open(compare_path).convert("L"), dtype=np.float32)
    edges = np.asarray(Image.open(compare_path).convert("L").filter(ImageFilter.FIND_EDGES), dtype=np.float32)
    return {
        "mse": round(float(np.mean((source - target) ** 2)), 2),
        "gray_mse": round(float(np.mean((source_gray - target_gray) ** 2)), 2),
        "edge_variance": round(float(np.var(edges)), 2),
    }


def run_variant(output_dir: Path, prompt: str, offline: bool) -> dict[str, object]:
    env = os.environ.copy()
    if offline:
        env["HF_HUB_OFFLINE"] = "1"
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "local_video_ltx_first_try.py"),
        "--image",
        str(DEFAULT_IMAGE),
        "--num-frames",
        "25",
        "--steps",
        "6",
        "--fps",
        "8",
        "--seed",
        str(DEFAULT_SEED),
        "--prepare-mode",
        "auto",
        "--prompt",
        prompt,
        "--negative-prompt",
        DEFAULT_NEGATIVE_PROMPT,
        "--output-dir",
        str(output_dir),
    ]
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    summary_path = output_dir / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    prepared_input = Path(str(summary["prepared_input"]))
    first_frame = Path(str(summary["output_first_frame"]))
    mid_frame = Path(str(summary["output_mid_frame"]))
    return {
        "status": summary.get("status"),
        "elapsed_seconds": summary.get("elapsed_seconds"),
        "returncode": completed.returncode,
        "prepare_mode": summary.get("prepare_mode"),
        "resolved_prepare_mode": summary.get("resolved_prepare_mode"),
        "auto_shot_type": summary.get("auto_shot_type"),
        "prompt": summary.get("prompt"),
        "summary_path": str(summary_path),
        "prepared_input": str(prepared_input),
        "first_frame": str(first_frame),
        "mid_frame": str(mid_frame),
        "first_frame_metrics": image_metrics(prepared_input, first_frame),
        "mid_frame_metrics": image_metrics(prepared_input, mid_frame),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare beer drink motion phrase vs still-life phrase on local LTX.")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    baseline = run_variant(args.output_dir / "baseline-drink-commercial-motion", BASELINE_PROMPT, args.offline)
    variant = run_variant(args.output_dir / "variant-still-life-beverage-shot", VARIANT_PROMPT, args.offline)
    summary = {
        "experiment_id": "EXP-78",
        "validation_type": "beer_drink_motion_phrase_ovaat",
        "image": str(DEFAULT_IMAGE),
        "seed": DEFAULT_SEED,
        "baseline": baseline,
        "variant": variant,
        "improvement": {
            "mid_frame_mse_delta": round(
                float(baseline["mid_frame_metrics"]["mse"]) - float(variant["mid_frame_metrics"]["mse"]),
                2,
            ),
            "edge_variance_delta": round(
                float(variant["mid_frame_metrics"]["edge_variance"]) - float(baseline["mid_frame_metrics"]["edge_variance"]),
                2,
            ),
        },
    }
    summary_path = args.output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"artifact_path={summary_path}")


if __name__ == "__main__":
    main()
