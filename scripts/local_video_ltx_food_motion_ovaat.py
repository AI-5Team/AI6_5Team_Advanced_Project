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
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-54-local-ltx-video-food-motion-phrase-ovaat"
BASE_PROMPT_PREFIX = "crispy gyukatsu, bright tabletop lighting, strong steam cloud"
BASE_PROMPT_SUFFIX = "static close-up, minimal camera movement"
BASELINE_MOTION = "realistic food motion"
VARIANT_MOTION = "subtle sizzling food motion"


def run_ltx_variant(output_dir: Path, prompt: str, offline: bool) -> dict[str, object]:
    env = os.environ.copy()
    if offline:
        env["HF_HUB_OFFLINE"] = "1"

    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "local_video_ltx_first_try.py"),
        "--num-frames",
        "25",
        "--steps",
        "6",
        "--fps",
        "8",
        "--prompt",
        prompt,
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
    summary["stdout"] = completed.stdout
    summary["stderr"] = completed.stderr
    summary["returncode"] = completed.returncode
    return summary


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


def build_variant_report(output_dir: Path, summary: dict[str, object]) -> dict[str, object]:
    prepared_input = Path(str(summary["prepared_input"]))
    first_frame = Path(str(summary["output_first_frame"]))
    mid_frame = Path(str(summary["output_mid_frame"]))
    return {
        "output_dir": str(output_dir),
        "summary_path": str(output_dir / "summary.json"),
        "status": summary.get("status"),
        "elapsed_seconds": summary.get("elapsed_seconds"),
        "prompt": summary.get("prompt"),
        "frame_count": summary.get("frame_count"),
        "first_frame_metrics": image_metrics(prepared_input, first_frame),
        "mid_frame_metrics": image_metrics(prepared_input, mid_frame),
    }


def build_prompt(motion_phrase: str) -> str:
    return f"{BASE_PROMPT_PREFIX}, {motion_phrase}, {BASE_PROMPT_SUFFIX}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare LTX food motion phrase OVAT with fixed bright tabletop food prompt.")
    parser.add_argument("--baseline-motion", default=BASELINE_MOTION)
    parser.add_argument("--variant-motion", default=VARIANT_MOTION)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    baseline_dir = args.output_dir / "baseline-realistic-motion"
    variant_dir = args.output_dir / "variant-sizzling-motion"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    variant_dir.mkdir(parents=True, exist_ok=True)

    baseline_prompt = build_prompt(args.baseline_motion)
    variant_prompt = build_prompt(args.variant_motion)

    baseline_summary = run_ltx_variant(baseline_dir, baseline_prompt, args.offline)
    variant_summary = run_ltx_variant(variant_dir, variant_prompt, args.offline)

    combined = {
        "experiment_id": "EXP-54",
        "lever": "food_motion_phrase",
        "baseline_motion": args.baseline_motion,
        "variant_motion": args.variant_motion,
        "offline": args.offline,
        "baseline": build_variant_report(baseline_dir, baseline_summary),
        "variant": build_variant_report(variant_dir, variant_summary),
    }

    combined["delta"] = {
        "elapsed_seconds": round(
            float(combined["variant"]["elapsed_seconds"] or 0) - float(combined["baseline"]["elapsed_seconds"] or 0),
            2,
        ),
        "mid_frame_mse": round(
            float(combined["variant"]["mid_frame_metrics"]["mse"]) - float(combined["baseline"]["mid_frame_metrics"]["mse"]),
            2,
        ),
        "mid_frame_edge_variance": round(
            float(combined["variant"]["mid_frame_metrics"]["edge_variance"])
            - float(combined["baseline"]["mid_frame_metrics"]["edge_variance"]),
            2,
        ),
    }

    summary_path = args.output_dir / "summary.json"
    summary_path.write_text(json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(combined, ensure_ascii=False, indent=2))
    print(f"artifact_path={summary_path}")


if __name__ == "__main__":
    main()
