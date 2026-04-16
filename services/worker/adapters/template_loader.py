from __future__ import annotations

from pathlib import Path

from services.worker.utils.runtime import load_json


def load_template(template_spec_root: Path, template_id: str) -> dict:
    return load_json(template_spec_root / "templates" / f"{template_id}-{'new-menu' if template_id == 'T01' else 'promotion' if template_id == 'T02' else 'location-push' if template_id == 'T03' else 'review'}.json")


def load_copy_rule(template_spec_root: Path, purpose: str) -> dict:
    return load_json(template_spec_root / "copy-rules" / f"{purpose}.json")


def load_style(template_spec_root: Path, style_id: str) -> dict:
    return load_json(template_spec_root / "styles" / f"{style_id}.json")
