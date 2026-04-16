from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path
from uuid import uuid4


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
API_ROOT = REPO_ROOT / "services" / "api"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from hybrid_source_selection import build_hybrid_source_selection_snapshot, read_json, select_hybrid_source_candidate
from services.worker.pipelines.generation import run_generation_job


DEFAULT_EXPERIMENT_ID = "EXP-245-hybrid-generation-pipeline-spike"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-245-hybrid-generation-pipeline-spike"
DEFAULT_SAMPLE_IMAGE = REPO_ROOT / "docs" / "sample" / "음식사진샘플(규카츠).jpg"
DEFAULT_SOURCE_VIDEO = (
    REPO_ROOT
    / "docs"
    / "experiments"
    / "artifacts"
    / "exp-241-sora2-gyukatsu-input-framing-live-ovaat"
    / "baseline_auto"
    / "규카츠"
    / "sora2_first_try.mp4"
)
DEFAULT_BENCHMARK_SUMMARY = (
    REPO_ROOT
    / "docs"
    / "experiments"
    / "artifacts"
    / "exp-239-sora2-current-best-vs-control-two-sample-check"
    / "summary.json"
)


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def probe_duration(path: Path) -> float:
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "ffprobe duration probe failed")
    return float(completed.stdout.strip())


def initialize_database(runtime_dir: Path, storage_dir: Path, db_path: Path) -> None:
    os.environ["APP_RUNTIME_DIR"] = str(runtime_dir)
    os.environ["APP_STORAGE_DIR"] = str(storage_dir)
    os.environ["APP_DB_PATH"] = str(db_path)

    from app.core.config import get_settings as app_get_settings
    from services.api.app.core.config import get_settings
    from services.api.app.core.database import initialize_database as init_db

    app_get_settings.cache_clear()
    get_settings.cache_clear()
    init_db()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the hybrid generation pipeline spike with either manual or benchmark-gated source selection.")
    parser.add_argument("--experiment-id", default=DEFAULT_EXPERIMENT_ID)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--sample-image", type=Path, default=DEFAULT_SAMPLE_IMAGE)
    parser.add_argument("--source-video", type=Path, default=DEFAULT_SOURCE_VIDEO)
    parser.add_argument("--benchmark-summary", type=Path, default=None)
    parser.add_argument("--label", default=None)
    parser.add_argument("--provider", default=None)
    parser.add_argument("--allow-manual-review", action="store_true")
    parser.add_argument("--manual-review-decisions-dir", type=Path, default=None)
    return parser.parse_args()


def resolve_source_inputs(args: argparse.Namespace) -> tuple[Path, Path, dict[str, object]]:
    if args.benchmark_summary is None:
        return (
            args.sample_image,
            args.source_video,
            {
                "selectionMode": "manual",
                "provider": "manual_source",
                "gateDecision": "manual_override",
                "gateReason": "source video supplied directly",
                "imagePath": str(args.sample_image),
                "sourceVideoPath": str(args.source_video),
            },
        )

    if not args.label:
        raise ValueError("--label is required when --benchmark-summary is provided")
    benchmark_summary = read_json(args.benchmark_summary)
    candidate = select_hybrid_source_candidate(
        benchmark_summary,
        label=args.label,
        provider=args.provider,
        allow_manual_review=args.allow_manual_review,
        manual_review_decisions_dir=args.manual_review_decisions_dir,
    )
    selection_snapshot = build_hybrid_source_selection_snapshot(candidate)
    image_path = candidate["imagePath"]
    source_video_path = candidate["sourceVideoPath"]
    if not isinstance(image_path, Path) or not isinstance(source_video_path, Path):
        raise RuntimeError("selected hybrid source candidate returned invalid paths")
    return image_path, source_video_path, selection_snapshot


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir
    runtime_dir = output_dir / "runtime"
    storage_dir = runtime_dir / "storage"
    db_path = runtime_dir / "app.sqlite3"
    template_root = REPO_ROOT / "packages" / "template-spec"
    selected_sample_image, selected_source_video, selection_snapshot = resolve_source_inputs(args)

    if runtime_dir.exists():
        shutil.rmtree(runtime_dir)
    storage_dir.mkdir(parents=True, exist_ok=True)
    initialize_database(runtime_dir, storage_dir, db_path)

    project_id = str(uuid4())
    user_id = str(uuid4())
    asset_id = str(uuid4())
    run_id = str(uuid4())

    raw_dir = storage_dir / "projects" / project_id / "raw"
    hybrid_dir = storage_dir / "projects" / project_id / "hybrid"
    raw_dir.mkdir(parents=True, exist_ok=True)
    hybrid_dir.mkdir(parents=True, exist_ok=True)

    staged_raw = raw_dir / f"{asset_id}.jpg"
    staged_source_video = hybrid_dir / "source.mp4"
    shutil.copy(selected_sample_image, staged_raw)
    shutil.copy(selected_source_video, staged_source_video)

    from services.api.app.core.database import utc_now

    with sqlite3.connect(db_path) as connection:
        now = utc_now()
        connection.execute(
            "INSERT INTO users (id, email, password_hash, name, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, "hybrid@test.com", "x", "hybrid", now, now),
        )
        connection.execute(
            """
            INSERT INTO content_projects (
              id, user_id, business_type, purpose, style, region_name, detail_location,
              selected_channels_json, latest_generation_run_id, current_status, created_at, updated_at
            )
            VALUES (?, ?, 'restaurant', 'promotion', 'b_grade_fun', '성수동', '서울숲', '["instagram"]', ?, 'queued', ?, ?)
            """,
            (project_id, user_id, run_id, now, now),
        )
        connection.execute(
            """
            INSERT INTO project_assets (
              id, project_id, original_file_name, mime_type, file_size_bytes, width, height,
              storage_path, warnings_json, created_at
            )
            VALUES (?, ?, 'sample.jpg', 'image/jpeg', ?, 1200, 1600, ?, '[]', ?)
            """,
            (asset_id, project_id, staged_raw.stat().st_size, f"/projects/{project_id}/raw/{asset_id}.jpg", now),
        )
        input_snapshot = json.dumps(
            {
                "assetIds": [asset_id],
                "templateId": "T02",
                "hybridSourceVideoPath": f"/projects/{project_id}/hybrid/source.mp4",
                "hybridSourceSelection": selection_snapshot,
            },
            ensure_ascii=False,
        )
        connection.execute(
            """
            INSERT INTO generation_runs (
              id, project_id, run_type, trigger_source, template_id,
              input_snapshot_json, quick_options_snapshot_json, status, error_code, started_at, finished_at, created_at
            )
            VALUES (?, ?, 'initial', 'user', 'T02', ?, '{}', 'queued', NULL, NULL, NULL, ?)
            """,
            (run_id, project_id, input_snapshot, now),
        )
        for step in ["preprocessing", "copy_generation", "video_rendering", "post_rendering", "packaging"]:
            connection.execute(
                "INSERT INTO generation_run_steps (id, generation_run_id, step_name, status, error_code, started_at, finished_at, updated_at) VALUES (?, ?, ?, 'pending', NULL, NULL, NULL, ?)",
                (str(uuid4()), run_id, step, now),
            )
        connection.commit()

    run_generation_job(db_path, storage_dir, template_root, project_id, run_id)

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        variant = connection.execute(
            "SELECT video_path, post_image_path, preview_thumbnail_path, render_meta_json FROM generated_variants WHERE generation_run_id = ?",
            (run_id,),
        ).fetchone()
        run_row = connection.execute("SELECT status FROM generation_runs WHERE id = ?", (run_id,)).fetchone()
        if variant is None or run_row is None:
            raise RuntimeError("hybrid generation pipeline spike did not produce a variant")

    render_meta = json.loads(variant["render_meta_json"])
    final_video_path = storage_dir / variant["video_path"].lstrip("/")
    summary = {
        "experiment_id": args.experiment_id,
        "runtime_dir": str(runtime_dir),
        "project_id": project_id,
        "generation_run_id": run_id,
        "status": run_row["status"],
        "selected_sample_image": str(selected_sample_image),
        "selected_source_video": str(selected_source_video),
        "hybridSourceSelection": selection_snapshot,
        "video_path": variant["video_path"],
        "post_image_path": variant["post_image_path"],
        "preview_thumbnail_path": variant["preview_thumbnail_path"],
        "render_meta_path": str(final_video_path).replace("video.mp4", "render-meta.json"),
        "rendererVideoSourceMode": render_meta.get("rendererVideoSourceMode"),
        "rendererMotionMode": render_meta.get("rendererMotionMode"),
        "rendererHybridSourceVideo": render_meta.get("rendererHybridSourceVideo"),
        "rendererHybridSourceSelection": render_meta.get("rendererHybridSourceSelection"),
        "rendererHybridDurationStrategy": render_meta.get("rendererHybridDurationStrategy"),
        "rendererHybridTargetDurationSec": render_meta.get("rendererHybridTargetDurationSec"),
        "finalVideoDurationSec": round(probe_duration(final_video_path), 2),
        "rendererHybridOverlayTimeline": render_meta.get("rendererHybridOverlayTimeline"),
    }
    write_json(output_dir / "summary.json", summary)
    print(output_dir / "summary.json")


if __name__ == "__main__":
    main()
