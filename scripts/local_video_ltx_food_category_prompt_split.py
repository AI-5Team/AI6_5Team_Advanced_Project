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
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-64-local-ltx-food-category-prompt-split"
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
TAILORED_PROMPTS = {
    "규카츠": "crispy gyukatsu cutlet sliced on a wire rack, crunchy breading texture, pink center clearly visible, plated set meal, bright tabletop lighting, static close-up, minimal camera movement",
    "라멘": "ramen bowl with glossy broth surface, noodles clearly separated beneath toppings, gentle steam, overhead bowl close-up, minimal camera movement",
    "순두부짬뽕": "spicy red tofu seafood soup, soft tofu curds and scallions clearly visible, soup surface clearly defined, overhead close-up, minimal camera movement",
    "장어덮밥": "grilled eel rice bowl with glossy sauce over rice, lacquered bowl and eel strips clearly visible, slightly high-angle close-up, minimal camera movement",
    "커피": "iced coffee in a clear glass with visible ice cubes and crema, condensation on the glass, tabletop close-up, minimal camera movement",
    "아이스크림": "soft serve ice cream with swirl texture clearly visible, clean dessert close-up, bright tabletop lighting, minimal camera movement",
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


def build_generic_prompt(image_path: Path) -> str:
    key = infer_food_key(image_path)
    label = LABEL_MAP.get(key, "plated food")
    return (
        f"{label}, bright tabletop lighting, strong steam cloud, "
        "realistic food motion, static close-up, minimal camera movement"
    )


def build_tailored_prompt(image_path: Path) -> str:
    key = infer_food_key(image_path)
    return TAILORED_PROMPTS.get(
        key,
        "plated food close-up, bright tabletop lighting, static close-up, minimal camera movement",
    )


def run_variant(image_path: Path, output_dir: Path, prompt: str, offline: bool) -> dict[str, object]:
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
        "prompt": summary.get("prompt"),
        "summary_path": str(summary_path),
        "first_frame": str(first_frame),
        "mid_frame": str(mid_frame),
        "first_frame_metrics": image_metrics(prepared_input, first_frame),
        "mid_frame_metrics": image_metrics(prepared_input, mid_frame),
    }


def evaluate_image(image_path: Path, output_dir: Path, offline: bool) -> dict[str, object]:
    key = infer_food_key(image_path)
    image_output_dir = output_dir / image_path.stem.replace("음식사진샘플(", "").replace(")", "")
    image_output_dir.mkdir(parents=True, exist_ok=True)

    generic = run_variant(image_path, image_output_dir / "generic", build_generic_prompt(image_path), offline)
    tailored = run_variant(image_path, image_output_dir / "tailored", build_tailored_prompt(image_path), offline)

    return {
        "image": str(image_path),
        "category": key,
        "generic": generic,
        "tailored": tailored,
        "improvement": {
            "mid_frame_mse_delta": round(
                float(generic["mid_frame_metrics"]["mse"]) - float(tailored["mid_frame_metrics"]["mse"]),
                2,
            ),
            "edge_variance_delta": round(
                float(tailored["mid_frame_metrics"]["edge_variance"]) - float(generic["mid_frame_metrics"]["edge_variance"]),
                2,
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare generic vs category-tailored prompt templates for local LTX food shots.")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    images = [evaluate_image(image_path, args.output_dir, args.offline) for image_path in DEFAULT_IMAGES]
    positive_improvements = [item for item in images if float(item["improvement"]["mid_frame_mse_delta"]) > 0]
    summary = {
        "experiment_id": "EXP-64",
        "validation_type": "food_category_prompt_split",
        "seed": DEFAULT_SEED,
        "offline": args.offline,
        "images": images,
        "aggregate": {
            "image_count": len(images),
            "tailored_better_count": len(positive_improvements),
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
