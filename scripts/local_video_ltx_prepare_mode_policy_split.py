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
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-66-local-ltx-prepare-mode-policy-split"
DEFAULT_IMAGES = [
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(규카츠).jpg",
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(라멘).jpg",
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(순두부짬뽕).jpg",
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(장어덮밥).jpg",
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(커피).jpg",
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(아이스크림).jpg",
]
DEFAULT_NEGATIVE_PROMPT = "worst quality, blurry, jittery, distorted, warped, overexposed, text, watermark"
DEFAULT_SEED = 7
LABEL_MAP = {
    "규카츠": "crispy gyukatsu",
    "라멘": "ramen bowl",
    "순두부짬뽕": "spicy seafood noodle soup",
    "장어덮밥": "grilled eel rice bowl",
    "커피": "iced coffee",
    "아이스크림": "soft serve ice cream",
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


def infer_food_key(image_path: Path) -> str:
    for key in LABEL_MAP:
        if key in image_path.stem:
            return key
    return "기타"


def build_prompt(image_path: Path) -> str:
    label = LABEL_MAP.get(infer_food_key(image_path), "plated food")
    return (
        f"{label}, bright tabletop lighting, strong steam cloud, "
        "realistic food motion, static close-up, minimal camera movement"
    )


def choose_policy_mode(image_path: Path) -> str:
    key = infer_food_key(image_path)
    if key == "규카츠":
        return "cover_center"
    return "contain_blur"


def run_variant(image_path: Path, output_dir: Path, prepare_mode: str, offline: bool) -> dict[str, object]:
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


def evaluate_image(image_path: Path, output_dir: Path, offline: bool) -> dict[str, object]:
    image_output_dir = output_dir / image_path.stem.replace("음식사진샘플(", "").replace(")", "")
    image_output_dir.mkdir(parents=True, exist_ok=True)
    baseline = run_variant(image_path, image_output_dir / "uniform-contain-blur", "contain_blur", offline)
    policy_mode = choose_policy_mode(image_path)
    variant = run_variant(image_path, image_output_dir / f"policy-{policy_mode}", policy_mode, offline)
    return {
        "image": str(image_path),
        "policy_prepare_mode": policy_mode,
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare a single global prepare mode vs a shot-type prepare policy for local LTX.")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    images = [evaluate_image(image_path, args.output_dir, args.offline) for image_path in DEFAULT_IMAGES]
    positive = [item for item in images if float(item["improvement"]["mid_frame_mse_delta"]) > 0]
    summary = {
        "experiment_id": "EXP-66",
        "validation_type": "prepare_mode_policy_split",
        "seed": DEFAULT_SEED,
        "baseline_prepare_mode": "contain_blur",
        "variant_policy": {
            "규카츠": "cover_center",
            "default": "contain_blur",
        },
        "offline": args.offline,
        "images": images,
        "aggregate": {
            "image_count": len(images),
            "policy_better_count": len(positive),
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
