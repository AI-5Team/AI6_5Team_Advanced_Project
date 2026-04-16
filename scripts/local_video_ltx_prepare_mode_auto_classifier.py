from __future__ import annotations

import argparse
import json
from pathlib import Path

from local_video_ltx_prepare_mode_classifier import classify_shot_type, choose_prepare_mode, extract_structure_features


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-69-local-ltx-prepare-mode-auto-classifier"
KNOWN_BASELINE_POLICY = {
    "규카츠": "cover_center",
    "라멘": "contain_blur",
    "순두부짬뽕": "contain_blur",
    "장어덮밥": "contain_blur",
    "커피": "cover_top",
    "아이스크림": "contain_blur",
}


def infer_label(image_path: Path) -> str:
    stem = image_path.stem
    for key in KNOWN_BASELINE_POLICY:
        if key in stem:
            return key
    return stem.replace("음식사진샘플(", "").replace(")", "")


def evaluate_image(image_path: Path) -> dict[str, object]:
    label = infer_label(image_path)
    predicted_mode = choose_prepare_mode(image_path)
    shot_type = classify_shot_type(image_path)
    result = {
        "image": str(image_path),
        "label": label,
        "features": extract_structure_features(image_path),
        "shot_type": shot_type,
        "predicted_prepare_mode": predicted_mode,
    }
    if label in KNOWN_BASELINE_POLICY:
        expected = KNOWN_BASELINE_POLICY[label]
        result["expected_prepare_mode"] = expected
        result["matches_known_baseline"] = predicted_mode == expected
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a simple image-only prepare_mode classifier for local LTX.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    images = sorted((REPO_ROOT / "docs" / "sample").glob("음식사진샘플(*).jpg"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    evaluations = [evaluate_image(path) for path in images]
    known = [item for item in evaluations if "expected_prepare_mode" in item]
    matched = [item for item in known if item["matches_known_baseline"]]
    summary = {
        "experiment_id": "EXP-69",
        "validation_type": "prepare_mode_auto_classifier",
        "images": evaluations,
        "known_baseline_eval": {
            "image_count": len(known),
            "matched_count": len(matched),
            "accuracy": round(len(matched) / max(len(known), 1), 4),
        },
    }
    summary_path = args.output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"artifact_path={summary_path}")


if __name__ == "__main__":
    main()
