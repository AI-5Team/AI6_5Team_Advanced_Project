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
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-63-local-ltx-multi-seed-shortlist"
DEFAULT_IMAGES = [
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(규카츠).jpg",
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(라멘).jpg",
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(순두부짬뽕).jpg",
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(장어덮밥).jpg",
]
DEFAULT_SEEDS = [7, 11, 19]
DEFAULT_FIXED_SEED = 7
DEFAULT_NEGATIVE_PROMPT = "worst quality, blurry, jittery, distorted, warped, overexposed, text, watermark"
PROMPT_MAP = {
    "규카츠": "crispy gyukatsu",
    "라멘": "ramen bowl",
    "순두부짬뽕": "spicy seafood noodle soup",
    "장어덮밥": "grilled eel rice bowl",
}


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


def infer_food_label(image_path: Path) -> str:
    for key, label in PROMPT_MAP.items():
        if key in image_path.stem:
            return label
    return "plated hot food"


def build_prompt(image_path: Path) -> str:
    return (
        f"{infer_food_label(image_path)}, bright tabletop lighting, strong steam cloud, "
        "realistic food motion, static close-up, minimal camera movement"
    )


def run_seed(image_path: Path, output_dir: Path, seed: int, offline: bool) -> dict[str, object]:
    env = os.environ.copy()
    if offline:
        env["HF_HUB_OFFLINE"] = "1"

    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "local_video_ltx_first_try.py"),
        "--image",
        str(image_path),
        "--num-frames",
        "25",
        "--steps",
        "6",
        "--fps",
        "8",
        "--seed",
        str(seed),
        "--prompt",
        build_prompt(image_path),
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
        "seed": seed,
        "status": summary.get("status"),
        "elapsed_seconds": summary.get("elapsed_seconds"),
        "returncode": completed.returncode,
        "summary_path": str(summary_path),
        "first_frame": str(first_frame),
        "mid_frame": str(mid_frame),
        "first_frame_metrics": image_metrics(prepared_input, first_frame),
        "mid_frame_metrics": image_metrics(prepared_input, mid_frame),
    }


def evaluate_image(image_path: Path, output_dir: Path, seeds: list[int], fixed_seed: int, offline: bool) -> dict[str, object]:
    image_output_dir = output_dir / image_path.stem.replace("음식사진샘플(", "").replace(")", "")
    image_output_dir.mkdir(parents=True, exist_ok=True)
    runs = []
    for seed in seeds:
        run_output_dir = image_output_dir / f"seed-{seed}"
        run_output_dir.mkdir(parents=True, exist_ok=True)
        runs.append(run_seed(image_path, run_output_dir, seed, offline))

    completed_runs = [run for run in runs if run.get("status") == "completed"]
    fixed_run = next(run for run in completed_runs if int(run["seed"]) == fixed_seed)
    shortlist_best = min(completed_runs, key=lambda item: float(item["mid_frame_metrics"]["mse"]))
    return {
        "image": str(image_path),
        "fixed_seed": fixed_seed,
        "runs": runs,
        "baseline_fixed_seed": {
            "seed": fixed_run["seed"],
            "mid_frame_mse": fixed_run["mid_frame_metrics"]["mse"],
            "edge_variance": fixed_run["mid_frame_metrics"]["edge_variance"],
        },
        "shortlist_best": {
            "seed": shortlist_best["seed"],
            "mid_frame_mse": shortlist_best["mid_frame_metrics"]["mse"],
            "edge_variance": shortlist_best["mid_frame_metrics"]["edge_variance"],
        },
        "improvement": {
            "mid_frame_mse_delta": round(
                float(fixed_run["mid_frame_metrics"]["mse"]) - float(shortlist_best["mid_frame_metrics"]["mse"]),
                2,
            ),
            "edge_variance_delta": round(
                float(shortlist_best["mid_frame_metrics"]["edge_variance"]) - float(fixed_run["mid_frame_metrics"]["edge_variance"]),
                2,
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare fixed seed vs multi-seed shortlist for the current local LTX baseline.")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--fixed-seed", type=int, default=DEFAULT_FIXED_SEED)
    parser.add_argument("--seeds", nargs="+", type=int, default=DEFAULT_SEEDS)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    images = [evaluate_image(image_path, args.output_dir, args.seeds, args.fixed_seed, args.offline) for image_path in DEFAULT_IMAGES]
    positive_improvements = [item for item in images if float(item["improvement"]["mid_frame_mse_delta"]) > 0]
    summary = {
        "experiment_id": "EXP-63",
        "validation_type": "multi_seed_shortlist",
        "fixed_seed": args.fixed_seed,
        "candidate_seeds": args.seeds,
        "offline": args.offline,
        "images": images,
        "aggregate": {
            "image_count": len(images),
            "shortlist_better_count": len(positive_improvements),
            "avg_mid_frame_mse_delta": round(
                sum(float(item["improvement"]["mid_frame_mse_delta"]) for item in images) / max(len(images), 1),
                2,
            ),
            "avg_edge_variance_delta": round(
                sum(float(item["improvement"]["edge_variance_delta"]) for item in images) / max(len(images), 1),
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
