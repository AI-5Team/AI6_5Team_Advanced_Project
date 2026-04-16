from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-61-local-ltx-seed-stability"
DEFAULT_IMAGE = REPO_ROOT / "docs" / "sample" / "음식사진샘플(규카츠).jpg"
DEFAULT_SEEDS = [7, 11, 19]
DEFAULT_NEGATIVE_PROMPT = "worst quality, blurry, jittery, distorted, warped, overexposed, text, watermark"
DEFAULT_PROMPT = (
    "crispy gyukatsu, bright tabletop lighting, strong steam cloud, "
    "realistic food motion, static close-up, minimal camera movement"
)


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


def pairwise_mse(left_path: Path, right_path: Path) -> float:
    left = np.asarray(Image.open(left_path).convert("RGB"), dtype=np.float32)
    right = np.asarray(Image.open(right_path).convert("RGB"), dtype=np.float32)
    return round(float(np.mean((left - right) ** 2)), 2)


def run_seed(seed: int, image_path: Path, output_dir: Path, offline: bool) -> dict[str, object]:
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
        DEFAULT_PROMPT,
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
        "prompt": summary.get("prompt"),
        "negative_prompt": summary.get("negative_prompt"),
        "summary_path": str(summary_path),
        "first_frame": str(first_frame),
        "mid_frame": str(mid_frame),
        "first_frame_metrics": image_metrics(prepared_input, first_frame),
        "mid_frame_metrics": image_metrics(prepared_input, mid_frame),
    }


def stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return round(float(np.std(np.asarray(values, dtype=np.float32))), 2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Check seed stability for the current local LTX food-shot baseline.")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seeds", nargs="+", type=int, default=DEFAULT_SEEDS)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    runs: list[dict[str, object]] = []
    for seed in args.seeds:
        run_output_dir = args.output_dir / f"seed-{seed}"
        run_output_dir.mkdir(parents=True, exist_ok=True)
        runs.append(run_seed(seed, args.image, run_output_dir, args.offline))

    completed_runs = [run for run in runs if run.get("status") == "completed"]
    pairwise = []
    for left, right in combinations(completed_runs, 2):
        pairwise.append(
            {
                "left_seed": left["seed"],
                "right_seed": right["seed"],
                "mid_frame_mse": pairwise_mse(Path(str(left["mid_frame"])), Path(str(right["mid_frame"]))),
            }
        )

    mid_frame_mses = [float(run["mid_frame_metrics"]["mse"]) for run in completed_runs]
    edge_variances = [float(run["mid_frame_metrics"]["edge_variance"]) for run in completed_runs]
    best_run = min(completed_runs, key=lambda item: float(item["mid_frame_metrics"]["mse"]), default=None)
    worst_run = max(completed_runs, key=lambda item: float(item["mid_frame_metrics"]["mse"]), default=None)
    summary = {
        "experiment_id": "EXP-61",
        "validation_type": "seed_stability",
        "image": str(args.image),
        "prompt": DEFAULT_PROMPT,
        "negative_prompt": DEFAULT_NEGATIVE_PROMPT,
        "offline": args.offline,
        "runs": runs,
        "pairwise_mid_frame_mse": pairwise,
        "aggregate": {
            "completed": len(completed_runs),
            "total": len(runs),
            "avg_elapsed_seconds": round(
                sum(float(run["elapsed_seconds"] or 0) for run in completed_runs) / max(len(completed_runs), 1),
                2,
            ),
            "mid_frame_mse_stddev": stdev(mid_frame_mses),
            "mid_frame_edge_variance_stddev": stdev(edge_variances),
            "best_seed_by_mid_frame_mse": best_run["seed"] if best_run else None,
            "best_seed_mid_frame_mse": best_run["mid_frame_metrics"]["mse"] if best_run else None,
            "worst_seed_by_mid_frame_mse": worst_run["seed"] if worst_run else None,
            "worst_seed_mid_frame_mse": worst_run["mid_frame_metrics"]["mse"] if worst_run else None,
            "avg_pairwise_mid_frame_mse": round(
                sum(float(item["mid_frame_mse"]) for item in pairwise) / max(len(pairwise), 1),
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
