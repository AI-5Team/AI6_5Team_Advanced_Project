from __future__ import annotations

import argparse
import importlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from services.worker.renderers.framing import classify_shot_type, choose_prepare_mode, prepare_image
from services.worker.renderers.media import CANVAS_SIZE, render_video
from video_benchmark_common import build_upper_bound_prompt, create_contact_sheet, video_motion_metrics


TRAIN_LABELS = [
    "맥주",
    "커피",
    "라멘",
    "타코야키",
    "순두부짬뽕",
    "아이스크림",
    "초코소보로호두과자",
    "귤모찌",
]
EVAL_LABELS = ["규카츠", "장어덮밥"]
APPROVED_INVENTORY_PATH = (
    REPO_ROOT
    / "docs"
    / "experiments"
    / "artifacts"
    / "exp-255-approved-hybrid-inventory-api-read-path"
    / "approved_inventory_full.json"
)
DEFAULT_OUTPUT_DIR = (
    REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-265-wan21-i2v-micro-lora-dataset-prep"
)


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def run_command(command: list[str]) -> tuple[bool, str]:
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    output = (completed.stdout or completed.stderr or "").strip()
    return completed.returncode == 0, output


def import_version(module_name: str) -> dict[str, Any]:
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:  # pragma: no cover - environment-specific
        return {"available": False, "error": type(exc).__name__, "detail": str(exc)}
    return {"available": True, "version": getattr(module, "__version__", None)}


def gpu_info() -> dict[str, Any]:
    try:
        torch = importlib.import_module("torch")
    except Exception as exc:  # pragma: no cover - environment-specific
        return {"torchAvailable": False, "error": type(exc).__name__, "detail": str(exc)}

    info: dict[str, Any] = {
        "torchAvailable": True,
        "cudaAvailable": bool(torch.cuda.is_available()),
        "deviceName": None,
        "bf16Supported": None,
        "freeVramGb": None,
        "totalVramGb": None,
    }
    if torch.cuda.is_available():
        info["deviceName"] = torch.cuda.get_device_name(0)
        info["bf16Supported"] = bool(torch.cuda.is_bf16_supported())
        free_mem, total_mem = torch.cuda.mem_get_info(0)
        info["freeVramGb"] = round(float(free_mem) / 1024**3, 2)
        info["totalVramGb"] = round(float(total_mem) / 1024**3, 2)
    return info


def detect_sample_images() -> dict[str, Path]:
    sample_dir = REPO_ROOT / "docs" / "sample"
    mapping: dict[str, Path] = {}
    for path in sample_dir.glob("*"):
        if not path.is_file():
            continue
        stem = path.stem
        if "(" in stem and ")" in stem:
            label = stem.split("(", 1)[1].rsplit(")", 1)[0]
            mapping[label] = path
    return mapping


def load_approved_inventory() -> list[dict[str, Any]]:
    payload = json.loads(APPROVED_INVENTORY_PATH.read_text(encoding="utf-8"))
    return list(payload.get("items") or [])


def train_variants_for_image(image_path: Path) -> list[dict[str, str | float]]:
    shot_type = classify_shot_type(image_path)
    base_prepare_mode = choose_prepare_mode(image_path)

    if shot_type == "glass_drink_candidate":
        return [
            {
                "variantId": "synthetic_push_top",
                "prepareMode": "cover_center",
                "motionPreset": "push_in_top",
                "durationSec": 1.2,
                "motionIntent": "top-anchored subtle push-in",
            },
            {
                "variantId": "synthetic_push_bottom",
                "prepareMode": "cover_bottom",
                "motionPreset": "push_in_bottom",
                "durationSec": 1.4,
                "motionIntent": "bottom-anchored subtle push-in",
            },
        ]

    if shot_type == "tray_full_plate":
        return [
            {
                "variantId": "synthetic_push_center",
                "prepareMode": "cover_center",
                "motionPreset": "push_in_center",
                "durationSec": 1.2,
                "motionIntent": "center push-in for full plate preserve",
            },
            {
                "variantId": "synthetic_push_top",
                "prepareMode": "cover_top",
                "motionPreset": "push_in_top",
                "durationSec": 1.4,
                "motionIntent": "top push-in for tray framing preserve",
            },
        ]

    secondary_prepare_mode = "cover_top" if base_prepare_mode != "cover_top" else "cover_center"
    secondary_motion = "push_in_top" if secondary_prepare_mode != "cover_bottom" else "push_in_bottom"
    return [
        {
            "variantId": "synthetic_push_center",
            "prepareMode": "cover_center",
            "motionPreset": "push_in_center",
            "durationSec": 1.2,
            "motionIntent": "center push-in preserve-first motion",
        },
        {
            "variantId": "synthetic_push_alt",
            "prepareMode": secondary_prepare_mode,
            "motionPreset": secondary_motion,
            "durationSec": 1.4,
            "motionIntent": "alternate preserve-first motion anchor",
        },
    ]


def ensure_clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def build_caption(image_path: Path, motion_intent: str) -> str:
    base = build_upper_bound_prompt(image_path)
    return (
        f"{base} Preserve the original product identity and layout. "
        f"Allow only {motion_intent}. Avoid morphing, ingredient drift, and composition rewrite."
    )


def create_synthetic_pair(
    *,
    image_path: Path,
    label: str,
    variant: dict[str, str | float],
    output_dir: Path,
) -> dict[str, Any]:
    pair_dir = output_dir / "synthetic" / label / str(variant["variantId"])
    pair_dir.mkdir(parents=True, exist_ok=True)

    prepared = prepare_image(image_path, CANVAS_SIZE[0], CANVAS_SIZE[1], str(variant["prepareMode"]))
    prepared_path = pair_dir / "prepared_input.png"
    prepared.save(prepared_path)

    video_path = pair_dir / "target.mp4"
    render_video(
        [(prepared_path, float(variant["durationSec"]))],
        video_path,
        motion_presets=[str(variant["motionPreset"])],
    )

    contact_sheet_path = pair_dir / "contact_sheet.png"
    create_contact_sheet(video_path, contact_sheet_path)
    motion_metrics = video_motion_metrics(video_path)

    summary = {
        "label": label,
        "imagePath": str(image_path),
        "preparedInputPath": str(prepared_path),
        "videoPath": str(video_path),
        "contactSheetPath": str(contact_sheet_path),
        "prepareMode": variant["prepareMode"],
        "motionPreset": variant["motionPreset"],
        "durationSec": variant["durationSec"],
        "motionIntent": variant["motionIntent"],
        "motionMetrics": motion_metrics,
        "createdAt": now_iso(),
    }
    (pair_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "split": "train",
        "label": label,
        "sourceKind": "synthetic_preserve_clip",
        "imagePath": str(image_path),
        "preparedInputPath": str(prepared_path),
        "videoPath": str(video_path),
        "contactSheetPath": str(contact_sheet_path),
        "caption": build_caption(image_path, str(variant["motionIntent"])),
        "prepareMode": variant["prepareMode"],
        "motionPreset": variant["motionPreset"],
        "clipDurationSec": variant["durationSec"],
        "suggestedNumFrames": 11 if float(variant["durationSec"]) <= 1.25 else 13,
        "suggestedFps": 8,
        "motionMetrics": motion_metrics,
    }


def select_reference_pairs(inventory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    references: list[dict[str, Any]] = []
    train_label_set = set(TRAIN_LABELS)
    for item in inventory:
        label = str(item.get("label") or "")
        if label not in train_label_set:
            continue
        video_path = item.get("sourceVideoPath")
        image_path = item.get("imagePath")
        if not isinstance(video_path, str) or not Path(video_path).exists():
            continue
        if not isinstance(image_path, str) or not Path(image_path).exists():
            continue
        references.append(
            {
                "split": "train",
                "label": label,
                "sourceKind": "approved_reference_clip",
                "imagePath": image_path,
                "preparedInputPath": None,
                "videoPath": video_path,
                "contactSheetPath": item.get("contactSheetPath"),
                "caption": build_caption(Path(image_path), "approved reference ad motion"),
                "prepareMode": None,
                "motionPreset": None,
                "clipDurationSec": None,
                "suggestedNumFrames": 11,
                "suggestedFps": 8,
                "motionMetrics": {"avg_rgb_diff": item.get("motionAvgRgbDiff")},
                "approvalSource": item.get("approvalSource"),
                "provider": item.get("provider"),
                "candidateKey": item.get("candidateKey"),
            }
        )
        if len(references) >= 3:
            break
    return references


def build_eval_samples(sample_images: dict[str, Path], inventory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_label = {str(item.get("label") or ""): item for item in inventory}
    samples: list[dict[str, Any]] = []
    for label in EVAL_LABELS:
        image_path = sample_images[label]
        reference_item = by_label.get(label)
        samples.append(
            {
                "split": "eval",
                "label": label,
                "imagePath": str(image_path),
                "caption": build_caption(image_path, "weak ad-friendly motion"),
                "referenceVideoPath": reference_item.get("sourceVideoPath") if reference_item else None,
                "referenceContactSheetPath": reference_item.get("contactSheetPath") if reference_item else None,
                "notes": "held-out preserve benchmark sample; not for training loss",
            }
        )
    return samples


def build_preflight() -> dict[str, Any]:
    ffmpeg_ok, ffmpeg_output = run_command(["ffmpeg", "-version"])
    ffprobe_ok, ffprobe_output = run_command(["ffprobe", "-version"])
    return {
        "pythonExecutable": sys.executable,
        "pythonVersion": sys.version,
        "createdAt": now_iso(),
        "gpu": gpu_info(),
        "modules": {
            "torch": import_version("torch"),
            "diffusers": import_version("diffusers"),
            "transformers": import_version("transformers"),
            "finetrainers": import_version("finetrainers"),
            "accelerate": import_version("accelerate"),
            "bitsandbytes": import_version("bitsandbytes"),
        },
        "commands": {
            "ffmpeg": {"available": ffmpeg_ok, "detail": ffmpeg_output.splitlines()[0] if ffmpeg_output else None},
            "ffprobe": {"available": ffprobe_ok, "detail": ffprobe_output.splitlines()[0] if ffprobe_output else None},
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare synthetic dataset manifest for EXP-264 micro-LoRA kill test.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--experiment-id", default="EXP-265-wan21-i2v-micro-lora-dataset-prep")
    args = parser.parse_args()

    sample_images = detect_sample_images()
    missing_train = [label for label in TRAIN_LABELS if label not in sample_images]
    missing_eval = [label for label in EVAL_LABELS if label not in sample_images]
    if missing_train or missing_eval:
        missing = ", ".join(missing_train + missing_eval)
        raise FileNotFoundError(f"required sample images missing: {missing}")

    ensure_clean_dir(args.output_dir)
    inventory = load_approved_inventory()

    synthetic_pairs: list[dict[str, Any]] = []
    for label in TRAIN_LABELS:
        image_path = sample_images[label]
        for variant in train_variants_for_image(image_path):
            synthetic_pairs.append(
                create_synthetic_pair(
                    image_path=image_path,
                    label=label,
                    variant=variant,
                    output_dir=args.output_dir,
                )
            )

    reference_pairs = select_reference_pairs(inventory)
    eval_samples = build_eval_samples(sample_images, inventory)
    preflight = build_preflight()

    manifest = {
        "experimentId": args.experiment_id,
        "createdAt": now_iso(),
        "trainPairs": synthetic_pairs + reference_pairs,
        "evalSamples": eval_samples,
        "stats": {
            "syntheticTrainPairs": len(synthetic_pairs),
            "approvedReferenceTrainPairs": len(reference_pairs),
            "totalTrainPairs": len(synthetic_pairs) + len(reference_pairs),
            "evalSamples": len(eval_samples),
            "trainLabels": TRAIN_LABELS,
            "evalLabels": EVAL_LABELS,
        },
        "preflight": preflight,
    }

    manifest_path = args.output_dir / "manifest.json"
    preflight_path = args.output_dir / "preflight.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    preflight_path.write_text(json.dumps(preflight, ensure_ascii=False, indent=2), encoding="utf-8")
    print(manifest_path)


if __name__ == "__main__":
    main()
