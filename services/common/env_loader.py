from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENV_FILES = (
    REPO_ROOT / ".env",
    REPO_ROOT / ".env.local",
)
ENV_ALIASES = (
    ("HF_TOKEN", "HUGGINGFACE_HUB_TOKEN"),
    ("LANGFUSE_BASE_URL", "LANGFUSE_HOST"),
)


def load_repo_env(paths: Iterable[Path] | None = None) -> None:
    loaded_keys: set[str] = set()
    env_paths = tuple(paths or DEFAULT_ENV_FILES)
    for env_path in env_paths:
        if not env_path.exists():
            continue
        for key, value in _parse_env_file(env_path).items():
            if value == "":
                continue
            os.environ[key] = value
            loaded_keys.add(key)
    _apply_aliases(loaded_keys)


def _parse_env_file(path: Path) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        parsed[key] = _normalize_value(value.strip())
    return parsed


def _normalize_value(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _apply_aliases(loaded_keys: set[str]) -> None:
    for primary, alias in ENV_ALIASES:
        primary_value = os.environ.get(primary, "").strip()
        alias_value = os.environ.get(alias, "").strip()
        if primary in loaded_keys and primary_value:
            os.environ[alias] = primary_value
        elif alias in loaded_keys and alias_value:
            os.environ[primary] = alias_value
        elif primary_value and not alias_value:
            os.environ[alias] = primary_value
        elif alias_value and not primary_value:
            os.environ[primary] = alias_value
