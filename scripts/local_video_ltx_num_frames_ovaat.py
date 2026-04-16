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
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-42-local-ltx-video-num-frames-ovaat"
SHORT_PROMPT = "crispy gyukatsu, gentle steam, slow push-in, warm restaurant lighting, realistic food motion"


def run_ltx_variant(output_dir: Path, num_frames: int, offline: bool) -> dict[str, object]:
    env = os.environ.copy()
    if offline:
        env["HF_HUB_OFFLINE"] = "1"

    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "local_video_ltx_first_try.py"),
        "--num-frames",
        str(num_frames),
        "--steps",
        "6",
        "--fps",
        "8",
        "--prompt",
        SHORT_PROMPT,
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
    summary["stdout"] = completed.stdout
    summary["stderr"] = completed.stderr
    summary["returncode"] = completed.returncode
    return summary


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


def build_variant_report(output_dir: Path, summary: dict[str, object]) -> dict[str, object]:
    prepared_input = Path(str(summary["prepared_input"]))
    first_frame = Path(str(summary["output_first_frame"]))
    mid_frame = Path(str(summary["output_mid_frame"]))
    return {
        "output_dir": str(output_dir),
        "summary_path": str(output_dir / "summary.json"),
        "status": summary.get("status"),
        "elapsed_seconds": summary.get("elapsed_seconds"),
        "num_frames": summary.get("num_frames"),
        "prompt": summary.get("prompt"),
        "frame_count": summary.get("frame_count"),
        "first_frame_metrics": image_metrics(prepared_input, first_frame),
        "mid_frame_metrics": image_metrics(prepared_input, mid_frame),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare LTX num_frames OVAT with a fixed short prompt.")
    parser.add_argument("--baseline-frames", type=int, default=17)
    parser.add_argument("--variant-frames", type=int, default=25)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    baseline_dir = args.output_dir / f"frames-{args.baseline_frames}"
    variant_dir = args.output_dir / f"frames-{args.variant_frames}"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    variant_dir.mkdir(parents=True, exist_ok=True)

    baseline_summary = run_ltx_variant(baseline_dir, args.baseline_frames, args.offline)
    variant_summary = run_ltx_variant(variant_dir, args.variant_frames, args.offline)

    combined = {
        "experiment_id": "EXP-42",
        "lever": "num_frames",
        "baseline_frames": args.baseline_frames,
        "variant_frames": args.variant_frames,
        "offline": args.offline,
        "baseline": build_variant_report(baseline_dir, baseline_summary),
        "variant": build_variant_report(variant_dir, variant_summary),
    }

    combined["delta"] = {
        "elapsed_seconds": round(
            float(combined["variant"]["elapsed_seconds"] or 0) - float(combined["baseline"]["elapsed_seconds"] or 0),
            2,
        ),
        "mid_frame_mse": round(
            float(combined["variant"]["mid_frame_metrics"]["mse"]) - float(combined["baseline"]["mid_frame_metrics"]["mse"]),
            2,
        ),
        "mid_frame_edge_variance": round(
            float(combined["variant"]["mid_frame_metrics"]["edge_variance"])
            - float(combined["baseline"]["mid_frame_metrics"]["edge_variance"]),
            2,
        ),
    }

    summary_path = args.output_dir / "summary.json"
    summary_path.write_text(json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(combined, ensure_ascii=False, indent=2))
    print(f"artifact_path={summary_path}")


if __name__ == "__main__":
    main()
