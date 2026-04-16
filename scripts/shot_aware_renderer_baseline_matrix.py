from __future__ import annotations

import json
import os
import shutil
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path
from uuid import uuid4

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

API_ROOT = REPO_ROOT / "services" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from services.worker.pipelines.generation import run_generation_job
from services.worker.renderers.framing import choose_prepare_mode, classify_shot_type
from video_benchmark_common import create_contact_sheet, video_motion_metrics


ARTIFACT_ROOT = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-236-shot-aware-renderer-baseline-matrix"
TEMPLATE_SPEC_ROOT = REPO_ROOT / "packages" / "template-spec"
SAMPLE_ROOT = REPO_ROOT / "docs" / "sample"
STEP_NAMES = ("preprocessing", "copy_generation", "video_rendering", "post_rendering", "packaging")
SAMPLE_CASES = (
    ("규카츠", "음식사진샘플(규카츠).jpg"),
    ("타코야키", "음식사진샘플(타코야키).jpg"),
    ("맥주", "음식사진샘플(맥주).jpg"),
    ("커피", "음식사진샘플(커피).jpg"),
    ("라멘", "음식사진샘플(라멘).jpg"),
    ("순두부짬뽕", "음식사진샘플(순두부짬뽕).jpg"),
    ("장어덮밥", "음식사진샘플(장어덮밥).jpg"),
    ("귤모찌", "음식사진샘플(귤모찌).jpg"),
)
SCENARIOS = (
    {
        "scenarioId": "promotion",
        "templateId": "T02",
        "purpose": "promotion",
        "style": "b_grade_fun",
        "regionName": "성수동",
        "detailLocation": "서울숲 근처",
        "businessType": "restaurant",
    },
    {
        "scenarioId": "review",
        "templateId": "T04",
        "purpose": "review",
        "style": "b_grade_fun",
        "regionName": "성수동",
        "detailLocation": "연무장길",
        "businessType": "restaurant",
    },
)


def initialize_schema(db_path: Path) -> None:
    from services.api.app.core.config import get_settings
    from services.api.app.core.database import initialize_database

    get_settings.cache_clear()
    initialize_database()


def create_generation_run(
    storage_root: Path,
    db_path: Path,
    scenario: dict[str, str],
    label: str,
    sample_file_name: str,
) -> tuple[str, str]:
    from services.api.app.core.database import utc_now

    project_id = str(uuid4())
    user_id = str(uuid4())
    asset_id = str(uuid4())
    run_id = str(uuid4())
    now = utc_now()
    raw_dir = storage_root / "projects" / project_id / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    source_path = SAMPLE_ROOT / sample_file_name
    target_path = raw_dir / f"{asset_id}{source_path.suffix.lower()}"
    shutil.copy(source_path, target_path)
    width, height = Image.open(source_path).size
    mime_type = "image/png" if source_path.suffix.lower() == ".png" else "image/jpeg"

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "INSERT INTO users (id, email, password_hash, name, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, f"{scenario['scenarioId']}-{label}@test.local", "x", label, now, now),
        )
        connection.execute(
            """
            INSERT INTO content_projects (
              id, user_id, business_type, purpose, style, region_name, detail_location,
              selected_channels_json, latest_generation_run_id, current_status, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, '["instagram"]', ?, 'queued', ?, ?)
            """,
            (
                project_id,
                user_id,
                scenario["businessType"],
                scenario["purpose"],
                scenario["style"],
                scenario["regionName"],
                scenario["detailLocation"],
                run_id,
                now,
                now,
            ),
        )
        connection.execute(
            """
            INSERT INTO project_assets (
              id, project_id, original_file_name, mime_type, file_size_bytes, width, height,
              storage_path, warnings_json, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, '[]', ?)
            """,
            (
                asset_id,
                project_id,
                sample_file_name,
                mime_type,
                target_path.stat().st_size,
                width,
                height,
                f"/projects/{project_id}/raw/{target_path.name}",
                now,
            ),
        )
        connection.execute(
            """
            INSERT INTO generation_runs (
              id, project_id, run_type, trigger_source, template_id,
              input_snapshot_json, quick_options_snapshot_json, status, error_code, started_at, finished_at, created_at
            )
            VALUES (?, ?, 'initial', 'user', ?, ?, '{}', 'queued', NULL, NULL, NULL, ?)
            """,
            (
                run_id,
                project_id,
                scenario["templateId"],
                json.dumps({"assetIds": [asset_id], "templateId": scenario["templateId"]}, ensure_ascii=False),
                now,
            ),
        )
        for step_name in STEP_NAMES:
            connection.execute(
                """
                INSERT INTO generation_run_steps (
                  id, generation_run_id, step_name, status, error_code, started_at, finished_at, updated_at
                ) VALUES (?, ?, ?, 'pending', NULL, NULL, NULL, ?)
                """,
                (str(uuid4()), run_id, step_name, now),
            )
        connection.commit()
    return project_id, run_id


def run_case(storage_root: Path, db_path: Path, scenario: dict[str, str], label: str, sample_file_name: str) -> dict[str, object]:
    project_id, run_id = create_generation_run(storage_root, db_path, scenario, label, sample_file_name)
    run_generation_job(db_path, storage_root, TEMPLATE_SPEC_ROOT, project_id, run_id)

    run_dir = storage_root / "projects" / project_id / "runs" / run_id
    render_meta = json.loads((run_dir / "render-meta.json").read_text(encoding="utf-8"))
    video_path = run_dir / "video.mp4"
    output_dir = ARTIFACT_ROOT / scenario["templateId"] / label
    output_dir.mkdir(parents=True, exist_ok=True)
    contact_sheet_path = create_contact_sheet(video_path, output_dir / "contact_sheet.png")

    sample_path = SAMPLE_ROOT / sample_file_name
    scene_policies = render_meta.get("rendererScenePolicies", [])
    prepare_modes = [policy["prepareMode"] for policy in scene_policies]
    motion_presets = [policy["motionPreset"] for policy in scene_policies]
    classifier_prepare_mode = choose_prepare_mode(sample_path)
    shot_type = classify_shot_type(sample_path)
    return {
        "scenarioId": scenario["scenarioId"],
        "templateId": scenario["templateId"],
        "purpose": scenario["purpose"],
        "label": label,
        "samplePath": str(sample_path),
        "shotType": shot_type,
        "classifierPrepareMode": classifier_prepare_mode,
        "firstScenePrepareMode": prepare_modes[0] if prepare_modes else None,
        "firstSceneMatchesClassifier": bool(prepare_modes) and prepare_modes[0] == classifier_prepare_mode,
        "rendererFramingMode": render_meta.get("rendererFramingMode"),
        "rendererMotionMode": render_meta.get("rendererMotionMode"),
        "rendererScenePolicies": scene_policies,
        "prepareModes": prepare_modes,
        "motionPresets": motion_presets,
        "videoPath": str(video_path),
        "contactSheet": str(contact_sheet_path),
        "motionMetrics": video_motion_metrics(video_path),
    }


def build_aggregate(records: list[dict[str, object]]) -> dict[str, object]:
    by_template: dict[str, dict[str, object]] = {}
    for template_id in sorted({str(record["templateId"]) for record in records}):
        template_records = [record for record in records if record["templateId"] == template_id]
        shot_counts = Counter(str(record["shotType"]) for record in template_records)
        first_scene_match_count = sum(1 for record in template_records if record["firstSceneMatchesClassifier"])
        motion_avg = round(
            sum(float(record["motionMetrics"]["avg_rgb_diff"]) for record in template_records) / len(template_records),
            2,
        )
        by_template[template_id] = {
            "recordCount": len(template_records),
            "shotTypeCounts": dict(sorted(shot_counts.items())),
            "firstSceneClassifierParity": f"{first_scene_match_count}/{len(template_records)}",
            "avgRgbDiffMean": motion_avg,
        }

    by_shot_type: dict[str, dict[str, object]] = {}
    for shot_type in sorted({str(record["shotType"]) for record in records}):
        shot_records = [record for record in records if record["shotType"] == shot_type]
        prepare_sequences = Counter(" -> ".join(record["prepareModes"]) for record in shot_records)
        motion_sequences = Counter(" -> ".join(record["motionPresets"]) for record in shot_records)
        by_shot_type[shot_type] = {
            "recordCount": len(shot_records),
            "templates": sorted({str(record["templateId"]) for record in shot_records}),
            "prepareSequences": dict(sorted(prepare_sequences.items())),
            "motionSequences": dict(sorted(motion_sequences.items())),
        }

    return {"byTemplate": by_template, "byShotType": by_shot_type}


def main() -> None:
    runtime_root = ARTIFACT_ROOT / "runtime"
    storage_root = runtime_root / "storage"
    db_path = runtime_root / "app.sqlite3"

    if ARTIFACT_ROOT.exists():
        shutil.rmtree(ARTIFACT_ROOT)
    storage_root.mkdir(parents=True, exist_ok=True)

    os.environ["APP_RUNTIME_DIR"] = str(runtime_root)
    os.environ["APP_STORAGE_DIR"] = str(storage_root)
    os.environ["APP_DB_PATH"] = str(db_path)
    initialize_schema(db_path)

    records: list[dict[str, object]] = []
    for scenario in SCENARIOS:
        for label, sample_file_name in SAMPLE_CASES:
            records.append(run_case(storage_root, db_path, scenario, label, sample_file_name))

    summary = {
        "experimentId": "EXP-236-shot-aware-renderer-baseline-matrix",
        "sampleCount": len(SAMPLE_CASES),
        "templateCount": len(SCENARIOS),
        "records": records,
        "aggregate": build_aggregate(records),
    }
    summary_path = ARTIFACT_ROOT / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(summary_path)


if __name__ == "__main__":
    main()
