from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from PIL import ImageFont


FONT_CANDIDATES = [
    Path("C:/Windows/Fonts/malgun.ttf"),
    Path("C:/Windows/Fonts/malgunbd.ttf"),
    Path("C:/Windows/Fonts/arial.ttf"),
]

BOLD_FONT_CANDIDATES = [
    Path("C:/Windows/Fonts/malgunbd.ttf"),
    Path("C:/Windows/Fonts/malgun.ttf"),
    Path("C:/Windows/Fonts/arial.ttf"),
]


@dataclass(frozen=True)
class WorkerRuntime:
    db_path: Path
    storage_root: Path
    template_spec_root: Path


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def connect(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_json(value: object) -> dict | list:
    if value is None:
        return {}
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str) and value:
        return json.loads(value)
    return {}


def dumps(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def resolve_storage_path(storage_root: Path, storage_path: str) -> Path:
    return storage_root / storage_path.lstrip("/").replace("/", str(Path("/")))


def storage_url(path: Path, storage_root: Path) -> str:
    relative = path.relative_to(storage_root).as_posix()
    return f"/media/{relative}"


def public_storage_path(path: Path, storage_root: Path) -> str:
    relative = path.relative_to(storage_root).as_posix()
    return f"/{relative}"


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    ordered = BOLD_FONT_CANDIDATES if bold else FONT_CANDIDATES
    for candidate in ordered:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()
