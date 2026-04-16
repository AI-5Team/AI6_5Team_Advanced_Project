from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-75-local-ltx-batch-runner-auto-default"
DEFAULT_IMAGES = [
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(규카츠).jpg",
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(라멘).jpg",
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(순두부짬뽕).jpg",
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(장어덮밥).jpg",
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(커피).jpg",
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(맥주).jpg",
]
DEFAULT_NEGATIVE_PROMPT = "worst quality, blurry, jittery, distorted, warped, overexposed, text, watermark"
DEFAULT_SEED = 7
LABEL_MAP = {
    "규카츠": "crispy gyukatsu",
    "타코야키": "takoyaki snack tray",
    "라멘": "ramen bowl",
    "순두부짬뽕": "spicy seafood noodle soup",
    "장어덮밥": "grilled eel rice bowl",
    "커피": "iced coffee",
    "맥주": "beer bottle and lager glass",
}
DRINK_KEYS = {"커피", "맥주"}
TRAY_KEYS = {"규카츠", "타코야키"}


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


def infer_label(image_path: Path) -> str:
    stem = image_path.stem
    for key in LABEL_MAP:
        if key in stem:
            return key
    return stem.replace("음식사진샘플(", "").replace(")", "")


def build_prompt(image_path: Path) -> str:
    key = infer_label(image_path)
    label = LABEL_MAP.get(key, "restaurant food")
    if key in DRINK_KEYS:
        return f"{label}, bright tabletop lighting, still life beverage shot, static close-up, minimal camera movement"
    if key in TRAY_KEYS:
        return f"{label}, bright tabletop lighting, realistic food motion, static close-up, minimal camera movement"
    return f"{label}, bright tabletop lighting, strong steam cloud, realistic food motion, static close-up, minimal camera movement"


def run_image(image_path: Path, output_dir: Path, prepare_mode: str, offline: bool) -> dict[str, object]:
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
        str(DEFAULT_SEED),
        "--prepare-mode",
        prepare_mode,
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
        "image": str(image_path),
        "label": infer_label(image_path),
        "status": summary.get("status"),
        "elapsed_seconds": summary.get("elapsed_seconds"),
        "returncode": completed.returncode,
        "prepare_mode": summary.get("prepare_mode"),
        "resolved_prepare_mode": summary.get("resolved_prepare_mode"),
        "auto_shot_type": summary.get("auto_shot_type"),
        "summary_path": str(summary_path),
        "mid_frame": str(mid_frame),
        "first_frame_metrics": image_metrics(prepared_input, first_frame),
        "mid_frame_metrics": image_metrics(prepared_input, mid_frame),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a reusable local LTX batch runner with auto prepare_mode by default.")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--prepare-mode", choices=["auto", "cover_center", "cover_top", "contain_blur"], default="auto")
    parser.add_argument("--images", nargs="*", type=Path, default=DEFAULT_IMAGES)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    runs: list[dict[str, object]] = []
    for image_path in args.images:
        slug = infer_label(image_path)
        output_dir = args.output_dir / slug
        output_dir.mkdir(parents=True, exist_ok=True)
        runs.append(run_image(image_path, output_dir, args.prepare_mode, args.offline))

    completed_runs = [run for run in runs if run.get("status") == "completed"]
    mode_counter = Counter(str(run["resolved_prepare_mode"]) for run in completed_runs)
    shot_counter = Counter(str(run["auto_shot_type"]) for run in completed_runs if run.get("auto_shot_type"))
    summary = {
        "runner_id": "local_ltx_batch_runner",
        "prepare_mode": args.prepare_mode,
        "offline": args.offline,
        "seed": DEFAULT_SEED,
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
            "resolved_prepare_modes": dict(mode_counter),
            "shot_type_counts": dict(shot_counter),
        },
    }
    summary_path = args.output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"artifact_path={summary_path}")


if __name__ == "__main__":
    main()
