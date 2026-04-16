from __future__ import annotations

import json
import os
import shutil
import sqlite3
import sys
from pathlib import Path
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

API_ROOT = REPO_ROOT / "services" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from services.worker.pipelines.generation import run_generation_job


ARTIFACT_ROOT = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-14-worker-scene-plan-bridge"
TEMPLATE_SPEC_ROOT = REPO_ROOT / "packages" / "template-spec"
SAMPLE_ROOT = REPO_ROOT / "docs" / "sample"

SCENARIOS = (
    {
        "name": "promotion",
        "project": {
            "business_type": "restaurant",
            "purpose": "promotion",
            "style": "b_grade_fun",
            "region_name": "성수동",
            "detail_location": "서울숲 근처",
            "template_id": "T02",
        },
        "assets": ("음식사진샘플(규카츠).jpg", "음식사진샘플(맥주).jpg"),
    },
    {
        "name": "review",
        "project": {
            "business_type": "restaurant",
            "purpose": "review",
            "style": "b_grade_fun",
            "region_name": "성수동",
            "detail_location": "연무장길",
            "template_id": "T04",
        },
        "assets": ("음식사진샘플(라멘).jpg",),
    },
)


def initialize_schema(db_path: Path) -> None:
    from services.api.app.core.config import get_settings
    from services.api.app.core.database import initialize_database

    get_settings.cache_clear()
    initialize_database()


def export_scenario(storage_root: Path, db_path: Path, scenario: dict) -> Path:
    from services.api.app.core.database import utc_now

    project_id = str(uuid4())
    user_id = str(uuid4())
    run_id = str(uuid4())
    now = utc_now()
    raw_dir = storage_root / "projects" / project_id / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    asset_ids: list[str] = []
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "INSERT INTO users (id, email, password_hash, name, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, f"{scenario['name']}@test.local", "x", scenario["name"], now, now),
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
                scenario["project"]["business_type"],
                scenario["project"]["purpose"],
                scenario["project"]["style"],
                scenario["project"]["region_name"],
                scenario["project"]["detail_location"],
                run_id,
                now,
                now,
            ),
        )

        for file_name in scenario["assets"]:
            asset_id = str(uuid4())
            source_path = SAMPLE_ROOT / file_name
            target_path = raw_dir / f"{asset_id}{source_path.suffix.lower()}"
            shutil.copy(source_path, target_path)
            asset_ids.append(asset_id)
            connection.execute(
                """
                INSERT INTO project_assets (
                  id, project_id, original_file_name, mime_type, file_size_bytes, width, height,
                  storage_path, warnings_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, 1200, 1600, ?, '[]', ?)
                """,
                (
                    asset_id,
                    project_id,
                    file_name,
                    "image/jpeg",
                    target_path.stat().st_size,
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
                scenario["project"]["template_id"],
                json.dumps({"assetIds": asset_ids, "templateId": scenario["project"]["template_id"]}, ensure_ascii=False),
                now,
            ),
        )
        for step_name in ["preprocessing", "copy_generation", "video_rendering", "post_rendering", "packaging"]:
            connection.execute(
                "INSERT INTO generation_run_steps (id, generation_run_id, step_name, status, error_code, started_at, finished_at, updated_at) VALUES (?, ?, ?, 'pending', NULL, NULL, NULL, ?)",
                (str(uuid4()), run_id, step_name, now),
            )
        connection.commit()

    run_generation_job(db_path, storage_root, TEMPLATE_SPEC_ROOT, project_id, run_id)
    return storage_root / "projects" / project_id / "runs" / run_id / "scene-plan.json"


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

    exported: list[dict[str, str]] = []
    for scenario in SCENARIOS:
        scene_plan_path = export_scenario(storage_root, db_path, scenario)
        target_path = ARTIFACT_ROOT / f"{scenario['name']}-scene-plan.json"
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(scene_plan_path, target_path)
        exported.append({"scenario": scenario["name"], "scenePlanPath": str(target_path)})

    (ARTIFACT_ROOT / "summary.json").write_text(json.dumps({"exports": exported}, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
