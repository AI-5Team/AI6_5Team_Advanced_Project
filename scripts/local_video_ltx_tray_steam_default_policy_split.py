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
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-77-local-ltx-tray-steam-default-policy-split"
DEFAULT_NEGATIVE_PROMPT = "worst quality, blurry, jittery, distorted, warped, overexposed, text, watermark"
DEFAULT_SEED = 7
TRAY_IMAGES = {
    "규카츠": REPO_ROOT / "docs" / "sample" / "음식사진샘플(규카츠).jpg",
    "타코야키": REPO_ROOT / "docs" / "sample" / "음식사진샘플(타코야키).jpg",
}
PROMPT_BASE = {
    "규카츠": "crispy gyukatsu, bright tabletop lighting",
    "타코야키": "takoyaki snack tray, bright tabletop lighting",
}
WITH_STEAM_SUFFIX = "strong steam cloud, realistic food motion, static close-up, minimal camera movement"
NO_STEAM_SUFFIX = "realistic food motion, static close-up, minimal camera movement"


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


def build_prompt(label: str, steam_on: bool) -> str:
    suffix = WITH_STEAM_SUFFIX if steam_on else NO_STEAM_SUFFIX
    return f"{PROMPT_BASE[label]}, {suffix}"


def run_image(image_path: Path, prompt: str, output_dir: Path, offline: bool) -> dict[str, object]:
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


def aggregate_policy(label: str, steam_on: bool, output_dir: Path, offline: bool) -> dict[str, object]:
    runs: list[dict[str, object]] = []
    for image_label, image_path in TRAY_IMAGES.items():
        slug = f"{image_label}-{'steam-on' if steam_on else 'steam-off'}"
        run = run_image(image_path, build_prompt(image_label, steam_on), output_dir / slug, offline)
        run["label"] = image_label
        runs.append(run)
    completed_runs = [run for run in runs if run.get("status") == "completed"]
    mode_counter = Counter(str(run["resolved_prepare_mode"]) for run in completed_runs)
    return {
        "policy_label": label,
        "steam_on": steam_on,
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
            "avg_edge_variance": round(
                sum(float(run["mid_frame_metrics"]["edge_variance"]) for run in completed_runs) / max(len(completed_runs), 1),
                2,
            ),
            "resolved_prepare_modes": dict(mode_counter),
        },
    }


def build_comparison(baseline: dict[str, object], variant: dict[str, object]) -> dict[str, object]:
    per_image: list[dict[str, object]] = []
    baseline_by_label = {str(item["label"]): item for item in baseline["images"]}  # type: ignore[index]
    variant_by_label = {str(item["label"]): item for item in variant["images"]}  # type: ignore[index]
    for label in TRAY_IMAGES:
        base_run = baseline_by_label[label]
        var_run = variant_by_label[label]
        per_image.append(
            {
                "label": label,
                "resolved_prepare_mode": var_run["resolved_prepare_mode"],
                "mid_frame_mse_delta": round(
                    float(base_run["mid_frame_metrics"]["mse"]) - float(var_run["mid_frame_metrics"]["mse"]),
                    2,
                ),
                "edge_variance_delta": round(
                    float(var_run["mid_frame_metrics"]["edge_variance"]) - float(base_run["mid_frame_metrics"]["edge_variance"]),
                    2,
                ),
            }
        )
    return {
        "avg_mid_frame_mse_delta": round(
            float(baseline["aggregate"]["avg_mid_frame_mse"]) - float(variant["aggregate"]["avg_mid_frame_mse"]),  # type: ignore[index]
            2,
        ),
        "avg_edge_variance_delta": round(
            float(variant["aggregate"]["avg_edge_variance"]) - float(baseline["aggregate"]["avg_edge_variance"]),  # type: ignore[index]
            2,
        ),
        "per_image": per_image,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare tray/full-plate steam default on vs off across gyukatsu and takoyaki.")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    baseline = aggregate_policy("tray_steam_on", True, args.output_dir / "baseline-tray-steam-on", args.offline)
    variant = aggregate_policy("tray_steam_off", False, args.output_dir / "variant-tray-steam-off", args.offline)
    summary = {
        "experiment_id": "EXP-77",
        "validation_type": "tray_steam_default_policy_split",
        "baseline": baseline,
        "variant": variant,
        "comparison": build_comparison(baseline, variant),
    }
    summary_path = args.output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"artifact_path={summary_path}")


if __name__ == "__main__":
    main()
