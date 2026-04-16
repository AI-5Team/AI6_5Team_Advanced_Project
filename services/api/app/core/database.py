from contextlib import contextmanager
from datetime import datetime, timezone
import sqlite3

from app.core.config import get_settings


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  name TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS store_profiles (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  business_type TEXT NOT NULL,
  region_name TEXT NOT NULL,
  detail_location TEXT,
  default_style TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS social_accounts (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  channel TEXT NOT NULL,
  account_name TEXT,
  status TEXT NOT NULL,
  access_token_ref TEXT,
  refresh_token_ref TEXT,
  token_expires_at TEXT,
  last_synced_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(user_id, channel),
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS content_projects (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  business_type TEXT NOT NULL,
  purpose TEXT NOT NULL,
  style TEXT NOT NULL,
  region_name TEXT NOT NULL,
  detail_location TEXT,
  selected_channels_json TEXT NOT NULL,
  latest_generation_run_id TEXT,
  current_status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS project_assets (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  original_file_name TEXT NOT NULL,
  mime_type TEXT NOT NULL,
  file_size_bytes INTEGER NOT NULL,
  width INTEGER NOT NULL,
  height INTEGER NOT NULL,
  storage_path TEXT NOT NULL,
  warnings_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(project_id) REFERENCES content_projects(id)
);

CREATE TABLE IF NOT EXISTS asset_derivatives (
  id TEXT PRIMARY KEY,
  asset_id TEXT NOT NULL,
  derivative_type TEXT NOT NULL,
  storage_path TEXT NOT NULL,
  width INTEGER NOT NULL,
  height INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE(asset_id, derivative_type),
  FOREIGN KEY(asset_id) REFERENCES project_assets(id)
);

CREATE TABLE IF NOT EXISTS generation_runs (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  run_type TEXT NOT NULL,
  trigger_source TEXT NOT NULL,
  template_id TEXT NOT NULL,
  input_snapshot_json TEXT NOT NULL,
  quick_options_snapshot_json TEXT NOT NULL,
  status TEXT NOT NULL,
  error_code TEXT,
  started_at TEXT,
  finished_at TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(project_id) REFERENCES content_projects(id)
);

CREATE TABLE IF NOT EXISTS generation_run_steps (
  id TEXT PRIMARY KEY,
  generation_run_id TEXT NOT NULL,
  step_name TEXT NOT NULL,
  status TEXT NOT NULL,
  error_code TEXT,
  started_at TEXT,
  finished_at TEXT,
  updated_at TEXT NOT NULL,
  UNIQUE(generation_run_id, step_name),
  FOREIGN KEY(generation_run_id) REFERENCES generation_runs(id)
);

CREATE TABLE IF NOT EXISTS copy_sets (
  id TEXT PRIMARY KEY,
  generation_run_id TEXT NOT NULL,
  hook_text TEXT NOT NULL,
  caption_options_json TEXT NOT NULL,
  hashtags_json TEXT NOT NULL,
  cta_text TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(generation_run_id) REFERENCES generation_runs(id)
);

CREATE TABLE IF NOT EXISTS generated_variants (
  id TEXT PRIMARY KEY,
  generation_run_id TEXT NOT NULL,
  copy_set_id TEXT NOT NULL,
  video_path TEXT,
  post_image_path TEXT,
  preview_thumbnail_path TEXT,
  duration_sec REAL,
  render_meta_json TEXT NOT NULL,
  is_selected INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  FOREIGN KEY(generation_run_id) REFERENCES generation_runs(id),
  FOREIGN KEY(copy_set_id) REFERENCES copy_sets(id)
);

CREATE TABLE IF NOT EXISTS upload_jobs (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  variant_id TEXT NOT NULL,
  social_account_id TEXT,
  channel TEXT NOT NULL,
  status TEXT NOT NULL,
  request_payload_snapshot_json TEXT NOT NULL,
  external_post_id TEXT,
  error_code TEXT,
  retry_count INTEGER NOT NULL DEFAULT 0,
  assist_package_path TEXT,
  assist_confirmed_at TEXT,
  published_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(project_id) REFERENCES content_projects(id),
  FOREIGN KEY(variant_id) REFERENCES generated_variants(id)
);

CREATE TABLE IF NOT EXISTS schedule_jobs (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  variant_id TEXT NOT NULL,
  channel TEXT NOT NULL,
  social_account_id TEXT,
  scheduled_for TEXT NOT NULL,
  status TEXT NOT NULL,
  payload_snapshot_json TEXT NOT NULL,
  linked_upload_job_id TEXT,
  error_code TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(project_id) REFERENCES content_projects(id),
  FOREIGN KEY(variant_id) REFERENCES generated_variants(id)
);

CREATE TABLE IF NOT EXISTS job_queue (
  id TEXT PRIMARY KEY,
  job_type TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  status TEXT NOT NULL,
  available_at TEXT NOT NULL,
  last_error TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS idempotency_keys (
  idempotency_key TEXT PRIMARY KEY,
  request_hash TEXT NOT NULL,
  response_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def initialize_database() -> None:
    settings = get_settings()
    settings.runtime_dir.mkdir(parents=True, exist_ok=True)
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(settings.db_path) as connection:
        connection.executescript(SCHEMA_SQL)
        connection.commit()


@contextmanager
def get_connection():
    initialize_database()
    connection = sqlite3.connect(get_settings().db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
