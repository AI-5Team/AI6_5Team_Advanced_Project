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
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-58-local-ltx-baseline-multi-image-validation"
DEFAULT_IMAGES = [
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(규카츠).jpg",
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(라멘).jpg",
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(순두부짬뽕).jpg",
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(장어덮밥).jpg",
]
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


def run_variant(image_path: Path, output_dir: Path, offline: bool) -> dict[str, object]:
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
    return {
        "image": str(image_path),
        "prompt": summary.get("prompt"),
        "negative_prompt": summary.get("negative_prompt"),
        "status": summary.get("status"),
        "elapsed_seconds": summary.get("elapsed_seconds"),
        "frame_count": summary.get("frame_count"),
        "returncode": completed.returncode,
        "first_frame_metrics": image_metrics(Path(str(summary["prepared_input"])), Path(str(summary["output_first_frame"]))),
        "mid_frame_metrics": image_metrics(Path(str(summary["prepared_input"])), Path(str(summary["output_mid_frame"]))),
        "summary_path": str(summary_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate current LTX food-shot baseline across multiple real food photos.")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    runs: list[dict[str, object]] = []
    for image_path in DEFAULT_IMAGES:
        slug = image_path.stem.replace("음식사진샘플(", "").replace(")", "")
        output_dir = args.output_dir / slug
        output_dir.mkdir(parents=True, exist_ok=True)
        runs.append(run_variant(image_path, output_dir, args.offline))

    completed_runs = [run for run in runs if run.get("status") == "completed"]
    combined = {
        "experiment_id": "EXP-58",
        "validation_type": "multi_image_baseline_validation",
        "baseline_prompt_shape": "bright tabletop lighting + strong steam cloud + realistic food motion + static close-up",
        "offline": args.offline,
        "images": runs,
        "aggregate": {
            "completed": len(completed_runs),
            "total": len(runs),
            "avg_elapsed_seconds": round(
                sum(float(run["elapsed_seconds"] or 0) for run in completed_runs) / max(len(completed_runs), 1),
                2,
            ),
            "avg_mid_frame_mse": round(
                sum(float(run["mid_frame_metrics"]["mse"]) for run in completed_runs) / max(len(completed_runs), 1),
                2,
            ),
            "avg_mid_frame_edge_variance": round(
                sum(float(run["mid_frame_metrics"]["edge_variance"]) for run in completed_runs) / max(len(completed_runs), 1),
                2,
            ),
        },
    }

    summary_path = args.output_dir / "summary.json"
    summary_path.write_text(json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(combined, ensure_ascii=False, indent=2))
    print(f"artifact_path={summary_path}")


if __name__ == "__main__":
    main()
