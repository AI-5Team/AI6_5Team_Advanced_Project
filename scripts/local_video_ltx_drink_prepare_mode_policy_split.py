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
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-85-local-ltx-drink-prepare-mode-policy-split"
DEFAULT_NEGATIVE_PROMPT = "worst quality, blurry, jittery, distorted, warped, overexposed, text, watermark"
DEFAULT_SEED = 7
DRINK_IMAGES = {
    "커피": REPO_ROOT / "docs" / "sample" / "음식사진샘플(커피).jpg",
    "맥주": REPO_ROOT / "docs" / "sample" / "음식사진샘플(맥주).jpg",
}
PROMPTS = {
    "커피": "iced coffee, bright tabletop lighting, still life beverage shot, static close-up, minimal camera movement",
    "맥주": "beer bottle and lager glass, bright tabletop lighting, still life beverage shot, static close-up, minimal camera movement",
}
OLD_POLICY = {
    "커피": "cover_top",
    "맥주": "cover_top",
}
NEW_POLICY = {
    "커피": "cover_top",
    "맥주": "cover_bottom",
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


def run_image(label: str, prepare_mode: str, output_dir: Path, offline: bool) -> dict[str, object]:
    env = os.environ.copy()
    if offline:
        env["HF_HUB_OFFLINE"] = "1"
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "local_video_ltx_first_try.py"),
        "--image",
        str(DRINK_IMAGES[label]),
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
        PROMPTS[label],
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
        "label": label,
        "status": summary.get("status"),
        "elapsed_seconds": summary.get("elapsed_seconds"),
        "returncode": completed.returncode,
        "prepare_mode": summary.get("prepare_mode"),
        "prompt": summary.get("prompt"),
        "summary_path": str(summary_path),
        "prepared_input": str(prepared_input),
        "first_frame": str(first_frame),
        "mid_frame": str(mid_frame),
        "first_frame_metrics": image_metrics(prepared_input, first_frame),
        "mid_frame_metrics": image_metrics(prepared_input, mid_frame),
    }


def run_policy(policy_label: str, modes: dict[str, str], output_dir: Path, offline: bool) -> dict[str, object]:
    runs = []
    for label in DRINK_IMAGES:
        runs.append(run_image(label, modes[label], output_dir / f"{label}-{modes[label]}", offline))
    avg_mid_mse = round(sum(float(run["mid_frame_metrics"]["mse"]) for run in runs) / len(runs), 2)
    avg_edge_var = round(sum(float(run["mid_frame_metrics"]["edge_variance"]) for run in runs) / len(runs), 2)
    return {
        "policy_label": policy_label,
        "seed": DEFAULT_SEED,
        "images": runs,
        "aggregate": {
            "completed": len([run for run in runs if run.get("status") == "completed"]),
            "total": len(runs),
            "avg_mid_frame_mse": avg_mid_mse,
            "avg_edge_variance": avg_edge_var,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare old vs new drink prepare-mode policy on local LTX.")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    baseline = run_policy("old_policy_all_cover_top", OLD_POLICY, args.output_dir / "baseline-old-policy", args.offline)
    variant = run_policy("new_policy_top_or_bottom", NEW_POLICY, args.output_dir / "variant-new-policy", args.offline)

    baseline_by_label = {str(item["label"]): item for item in baseline["images"]}  # type: ignore[index]
    variant_by_label = {str(item["label"]): item for item in variant["images"]}  # type: ignore[index]

    comparison = {
        "avg_mid_frame_mse_delta": round(
            float(baseline["aggregate"]["avg_mid_frame_mse"]) - float(variant["aggregate"]["avg_mid_frame_mse"]), 2  # type: ignore[index]
        ),
        "avg_edge_variance_delta": round(
            float(variant["aggregate"]["avg_edge_variance"]) - float(baseline["aggregate"]["avg_edge_variance"]), 2  # type: ignore[index]
        ),
        "per_image": [
            {
                "label": label,
                "baseline_prepare_mode": baseline_by_label[label]["prepare_mode"],
                "variant_prepare_mode": variant_by_label[label]["prepare_mode"],
                "mid_frame_mse_delta": round(
                    float(baseline_by_label[label]["mid_frame_metrics"]["mse"]) - float(variant_by_label[label]["mid_frame_metrics"]["mse"]),
                    2,
                ),
                "edge_variance_delta": round(
                    float(variant_by_label[label]["mid_frame_metrics"]["edge_variance"]) - float(baseline_by_label[label]["mid_frame_metrics"]["edge_variance"]),
                    2,
                ),
            }
            for label in DRINK_IMAGES
        ],
    }

    summary = {
        "experiment_id": "EXP-85",
        "validation_type": "drink_prepare_mode_policy_split",
        "baseline": baseline,
        "variant": variant,
        "comparison": comparison,
    }
    summary_path = args.output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"artifact_path={summary_path}")


if __name__ == "__main__":
    main()
