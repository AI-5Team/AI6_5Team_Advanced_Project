from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from uuid import uuid4

from services.worker.utils.runtime import WorkerRuntime, connect, dumps, ensure_dir, parse_json, resolve_storage_path, storage_url, utc_now


def run_publish_job(db_path: Path, storage_root: Path, template_spec_root: Path, upload_job_id: str) -> None:
    runtime = WorkerRuntime(db_path=db_path, storage_root=storage_root, template_spec_root=template_spec_root)
    with connect(runtime.db_path) as conn:
        _execute_publish(conn, runtime, upload_job_id)
        conn.commit()


def create_assist_package(db_path: Path, storage_root: Path, upload_job_id: str) -> dict:
    runtime = WorkerRuntime(db_path=db_path, storage_root=storage_root, template_spec_root=storage_root)
    with connect(runtime.db_path) as conn:
        return _build_assist_package(conn, runtime, upload_job_id)


def _execute_publish(conn: sqlite3.Connection, runtime: WorkerRuntime, upload_job_id: str) -> None:
    job = conn.execute("SELECT * FROM upload_jobs WHERE id = ?", (upload_job_id,)).fetchone()
    if job is None:
        raise ValueError("upload job not found")

    conn.execute(
        "UPDATE upload_jobs SET status = ?, updated_at = ? WHERE id = ?",
        ("publishing", utc_now(), upload_job_id),
    )
    conn.execute(
        "UPDATE content_projects SET current_status = ?, updated_at = ? WHERE id = ?",
        ("publishing", utc_now(), job["project_id"]),
    )

    if job["channel"] != "instagram":
        assist = _build_assist_package(conn, runtime, upload_job_id)
        conn.execute(
            "UPDATE upload_jobs SET status = ?, error_code = ?, assist_package_path = ?, updated_at = ? WHERE id = ?",
            ("assist_required", "PUBLISH_FAILED", assist["packagePath"], utc_now(), upload_job_id),
        )
        conn.execute(
            "UPDATE content_projects SET current_status = ?, updated_at = ? WHERE id = ?",
            ("upload_assist", utc_now(), job["project_id"]),
        )
        return

    external_post_id = f"ig_{uuid4().hex[:10]}"
    conn.execute(
        """
        UPDATE upload_jobs
        SET status = ?, external_post_id = ?, published_at = ?, updated_at = ?, error_code = NULL
        WHERE id = ?
        """,
        ("published", external_post_id, utc_now(), utc_now(), upload_job_id),
    )
    conn.execute(
        "UPDATE content_projects SET current_status = ?, updated_at = ? WHERE id = ?",
        ("published", utc_now(), job["project_id"]),
    )


def _build_assist_package(conn: sqlite3.Connection, runtime: WorkerRuntime, upload_job_id: str) -> dict:
    row = conn.execute(
        """
        SELECT uj.*, gv.video_path, gv.generation_run_id, cp.caption_options_json, cp.hashtags_json, cp.cta_text
        FROM upload_jobs uj
        JOIN generated_variants gv ON gv.id = uj.variant_id
        JOIN copy_sets cp ON cp.id = gv.copy_set_id
        WHERE uj.id = ?
        """,
        (upload_job_id,),
    ).fetchone()
    if row is None:
        raise ValueError("upload job not found for assist package")

    request_payload = parse_json(row["request_payload_snapshot_json"])
    captions = parse_json(row["caption_options_json"])
    hashtags = parse_json(row["hashtags_json"])
    media_abs = resolve_storage_path(runtime.storage_root, row["video_path"])
    package_dir = media_abs.parent / "assist"
    ensure_dir(package_dir)
    package_path = package_dir / f"{upload_job_id}.json"
    package = {
        "mediaUrl": storage_url(media_abs, runtime.storage_root),
        "caption": request_payload.get("captionOverride") or (captions[0] if captions else row["cta_text"]),
        "hashtags": request_payload.get("hashtags") or hashtags,
        "thumbnailText": request_payload.get("thumbnailText"),
        "packagePath": storage_url(package_path, runtime.storage_root),
    }
    package_path.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
    conn.execute(
        "UPDATE upload_jobs SET assist_package_path = ?, request_payload_snapshot_json = ? WHERE id = ?",
        (str(package_path.relative_to(runtime.storage_root).as_posix()), dumps(request_payload), upload_job_id),
    )
    return package
