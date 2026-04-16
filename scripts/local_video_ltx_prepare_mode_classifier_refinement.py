from __future__ import annotations

import argparse
import json
from pathlib import Path

from local_video_ltx_prepare_mode_classifier import classify_shot_type, choose_prepare_mode, extract_structure_features


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-71-local-ltx-prepare-mode-classifier-refinement"
KNOWN_POLICY_LABELS = {
    "규카츠": "cover_center",
    "라멘": "contain_blur",
    "순두부짬뽕": "contain_blur",
    "장어덮밥": "contain_blur",
    "커피": "cover_top",
    "맥주": "cover_top",
    "아이스크림": "contain_blur",
}


def infer_label(image_path: Path) -> str:
    stem = image_path.stem
    for key in KNOWN_POLICY_LABELS:
        if key in stem:
            return key
    return stem.replace("음식사진샘플(", "").replace(")", "")


def classify_shot_type_v1(features: dict[str, float]) -> str:
    if features["aspect_ratio"] >= 1.15 and features["mean_edge"] >= 0.12:
        return "tray_full_plate"
    if (
        features["aspect_ratio"] < 0.9
        and features["mean_edge"] <= 0.11
        and features["top_edge_ratio"] >= 1.18
        and features["bottom_edge_ratio"] <= 0.8
    ):
        return "glass_drink_candidate"
    return "preserve_shot"


def choose_prepare_mode_v1(features: dict[str, float]) -> str:
    shot_type = classify_shot_type_v1(features)
    if shot_type == "tray_full_plate":
        return "cover_center"
    if shot_type == "glass_drink_candidate":
        return "cover_top"
    return "contain_blur"


def evaluate_image(image_path: Path) -> dict[str, object]:
    label = infer_label(image_path)
    features = extract_structure_features(image_path)
    old_shot_type = classify_shot_type_v1(features)
    old_mode = choose_prepare_mode_v1(features)
    new_shot_type = classify_shot_type(image_path)
    new_mode = choose_prepare_mode(image_path)
    result = {
        "image": str(image_path),
        "label": label,
        "features": features,
        "v1_shot_type": old_shot_type,
        "v1_prepare_mode": old_mode,
        "v2_shot_type": new_shot_type,
        "v2_prepare_mode": new_mode,
        "changed": old_mode != new_mode,
    }
    if label in KNOWN_POLICY_LABELS:
        expected_mode = KNOWN_POLICY_LABELS[label]
        result["expected_prepare_mode"] = expected_mode
        result["v1_matches_expected"] = old_mode == expected_mode
        result["v2_matches_expected"] = new_mode == expected_mode
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare prepare_mode classifier v1 vs v2 after drink generalization evidence.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    images = sorted((REPO_ROOT / "docs" / "sample").glob("음식사진샘플(*).jpg"))
    evaluations = [evaluate_image(path) for path in images]
    known = [item for item in evaluations if "expected_prepare_mode" in item]
    v1_matched = [item for item in known if item["v1_matches_expected"]]
    v2_matched = [item for item in known if item["v2_matches_expected"]]
    changed = [item for item in evaluations if item["changed"]]
    summary = {
        "experiment_id": "EXP-71",
        "validation_type": "prepare_mode_classifier_refinement",
        "images": evaluations,
        "aggregate": {
            "image_count": len(evaluations),
            "changed_count": len(changed),
            "changed_labels": [item["label"] for item in changed],
        },
        "known_eval": {
            "image_count": len(known),
            "v1_matched_count": len(v1_matched),
            "v1_accuracy": round(len(v1_matched) / max(len(known), 1), 4),
            "v2_matched_count": len(v2_matched),
            "v2_accuracy": round(len(v2_matched) / max(len(known), 1), 4),
        },
    }
    summary_path = args.output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"artifact_path={summary_path}")


if __name__ == "__main__":
    main()
