from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-72-local-ltx-auto-prepare-mode-parity"
DEFAULT_IMAGES = [
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(규카츠).jpg",
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(라멘).jpg",
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(순두부짬뽕).jpg",
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(장어덮밥).jpg",
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(커피).jpg",
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(맥주).jpg",
    REPO_ROOT / "docs" / "sample" / "음식사진샘플(아이스크림).jpg",
]
DEFAULT_NEGATIVE_PROMPT = "worst quality, blurry, jittery, distorted, warped, overexposed, text, watermark"
DEFAULT_SEED = 7
PROMPT_MAP = {
    "규카츠": "crispy gyukatsu, bright tabletop lighting, strong steam cloud, realistic food motion, static close-up, minimal camera movement",
    "라멘": "ramen bowl, bright tabletop lighting, strong steam cloud, realistic food motion, static close-up, minimal camera movement",
    "순두부짬뽕": "spicy seafood noodle soup, bright tabletop lighting, strong steam cloud, realistic food motion, static close-up, minimal camera movement",
    "장어덮밥": "grilled eel rice bowl, bright tabletop lighting, strong steam cloud, realistic food motion, static close-up, minimal camera movement",
    "커피": "iced coffee, bright tabletop lighting, realistic drink commercial motion, static close-up, minimal camera movement",
    "맥주": "beer bottle and lager glass, bright tabletop lighting, realistic drink commercial motion, static close-up, minimal camera movement",
    "아이스크림": "soft serve ice cream, bright tabletop lighting, strong steam cloud, realistic food motion, static close-up, minimal camera movement",
}
MANUAL_POLICY = {
    "규카츠": "cover_center",
    "라멘": "contain_blur",
    "순두부짬뽕": "contain_blur",
    "장어덮밥": "contain_blur",
    "커피": "cover_top",
    "맥주": "cover_top",
    "아이스크림": "contain_blur",
}


def infer_label(image_path: Path) -> str:
    for key in MANUAL_POLICY:
        if key in image_path.stem:
            return key
    raise ValueError(f"unknown label for {image_path}")


def run_variant(image_path: Path, output_dir: Path, prepare_mode: str, offline: bool) -> dict[str, object]:
    env = os.environ.copy()
    if offline:
        env["HF_HUB_OFFLINE"] = "1"
    label = infer_label(image_path)
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
        PROMPT_MAP[label],
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
        "status": summary.get("status"),
        "elapsed_seconds": summary.get("elapsed_seconds"),
        "returncode": completed.returncode,
        "prepare_mode": summary.get("prepare_mode"),
        "resolved_prepare_mode": summary.get("resolved_prepare_mode"),
        "auto_shot_type": summary.get("auto_shot_type"),
        "summary_path": str(summary_path),
        "mid_frame": summary.get("output_mid_frame"),
    }


def evaluate_image(image_path: Path, output_dir: Path, offline: bool) -> dict[str, object]:
    label = infer_label(image_path)
    image_output_dir = output_dir / label
    image_output_dir.mkdir(parents=True, exist_ok=True)
    manual_mode = MANUAL_POLICY[label]
    baseline = run_variant(image_path, image_output_dir / f"manual-{manual_mode}", manual_mode, offline)
    variant = run_variant(image_path, image_output_dir / "auto", "auto", offline)
    return {
        "image": str(image_path),
        "label": label,
        "manual_prepare_mode": manual_mode,
        "auto_prepare_mode": variant["resolved_prepare_mode"],
        "auto_shot_type": variant["auto_shot_type"],
        "manual": baseline,
        "auto": variant,
        "matches_manual_policy": variant["resolved_prepare_mode"] == manual_mode,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate auto prepare_mode parity against current manual policy in local LTX.")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    images = [evaluate_image(image_path, args.output_dir, args.offline) for image_path in DEFAULT_IMAGES]
    matched = [item for item in images if item["matches_manual_policy"]]
    summary = {
        "experiment_id": "EXP-72",
        "validation_type": "auto_prepare_mode_parity",
        "seed": DEFAULT_SEED,
        "offline": args.offline,
        "images": images,
        "aggregate": {
            "image_count": len(images),
            "matched_count": len(matched),
            "parity_accuracy": round(len(matched) / max(len(images), 1), 4),
        },
    }
    summary_path = args.output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"artifact_path={summary_path}")


if __name__ == "__main__":
    main()
