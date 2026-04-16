from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = (
    REPO_ROOT
    / "docs"
    / "experiments"
    / "artifacts"
    / "exp-265-wan21-i2v-micro-lora-dataset-prep"
    / "manifest.json"
)
DEFAULT_OUTPUT_DIR = (
    REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-266-wan21-i2v-micro-lora-dry-run"
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def relative_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def export_dataset(manifest_path: Path, output_dir: Path) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    ensure_clean_dir(output_dir)

    dataset_root = output_dir / "train_dataset"
    videos_dir = dataset_root / "videos"
    dataset_root.mkdir(parents=True, exist_ok=True)
    videos_dir.mkdir(parents=True, exist_ok=True)

    prompt_lines: list[str] = []
    video_lines: list[str] = []
    exported_items: list[dict[str, Any]] = []

    train_pairs = list(manifest.get("trainPairs") or [])
    for index, item in enumerate(train_pairs, start=1):
        src_video = Path(str(item["videoPath"]))
        if not src_video.exists():
            raise FileNotFoundError(f"training video not found: {src_video}")

        safe_label = str(item["label"]).replace(" ", "_")
        safe_kind = str(item["sourceKind"]).replace(" ", "_")
        target_name = f"{index:03d}_{safe_label}_{safe_kind}{src_video.suffix.lower()}"
        dst_video = videos_dir / target_name
        shutil.copy2(src_video, dst_video)

        caption = str(item["caption"])
        prompt_lines.append(caption)
        video_lines.append(relative_posix(dst_video, dataset_root))
        exported_items.append(
            {
                "index": index,
                "label": item["label"],
                "sourceKind": item["sourceKind"],
                "sourceVideoPath": str(src_video),
                "exportedVideoPath": str(dst_video),
                "caption": caption,
            }
        )

    (dataset_root / "prompt.txt").write_text("\n".join(prompt_lines), encoding="utf-8")
    (dataset_root / "videos.txt").write_text("\n".join(video_lines), encoding="utf-8")

    training_config = {
        "datasets": [
            {
                "data_root": str(dataset_root),
                "dataset_type": "video",
                "video_resolution_buckets": [[13, 480, 832]],
                "reshape_mode": "bicubic",
                "remove_common_llm_caption_prefixes": False,
            }
        ]
    }
    write_json(output_dir / "training.json", training_config)

    validation_items: list[dict[str, Any]] = []
    for item in manifest.get("evalSamples") or []:
        validation_items.append(
            {
                "caption": str(item["caption"]),
                "image_path": str(item["imagePath"]),
                "video_path": item.get("referenceVideoPath"),
                "num_inference_steps": 8,
                "num_frames": 13,
                "height": 480,
                "width": 832,
            }
        )
    write_json(output_dir / "validation.json", {"data": validation_items})

    export_summary = {
        "sourceManifest": str(manifest_path),
        "outputDir": str(output_dir),
        "datasetRoot": str(dataset_root),
        "trainingConfig": str(output_dir / "training.json"),
        "validationConfig": str(output_dir / "validation.json"),
        "trainItemCount": len(exported_items),
        "exportedItems": exported_items,
    }
    write_json(output_dir / "export_summary.json", export_summary)
    return export_summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Export EXP-265 manifest to finetrainers local video dataset format.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    summary = export_dataset(args.manifest, args.output_dir)
    print(summary["datasetRoot"])


if __name__ == "__main__":
    main()
