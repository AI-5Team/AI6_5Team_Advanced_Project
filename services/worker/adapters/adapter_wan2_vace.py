from __future__ import annotations

import json
import os
import shlex
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping


def _is_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Wan2VaceRequest:
    config_path: Path
    experiment_name: str
    outputs_root: Path | None = None
    extra_args: dict[str, str | int | float | bool] = field(default_factory=dict)


@dataclass(frozen=True)
class Wan2VaceRunResult:
    run_dir: Path
    meta_path: Path
    video_path: Path | None
    status: str
    error: str | None = None


@dataclass(frozen=True)
class Wan2VaceAdapterConfig:
    workspace_path: Path | None = None
    python_executable: str = "python"
    inference_script: str = "scripts/run_inference.py"
    timeout_sec: int = 5400
    enabled: bool = False
    default_args: tuple[str, ...] = ()

    @property
    def script_path(self) -> Path | None:
        if self.workspace_path is None:
            return None
        return (self.workspace_path / self.inference_script).resolve()


class Wan2VaceAdapter:
    def __init__(self, config: Wan2VaceAdapterConfig) -> None:
        self.config = config

    def is_configured(self) -> bool:
        return bool(
            self.config.enabled
            and self.config.workspace_path is not None
            and self.config.script_path is not None
            and self.config.script_path.exists()
        )

    def build_command(self, request: Wan2VaceRequest) -> list[str]:
        workspace_path = self.config.workspace_path
        script_path = self.config.script_path
        if workspace_path is None or script_path is None:
            raise RuntimeError("wan2_vace_workspace_missing")

        command = [
            self.config.python_executable,
            str(script_path),
            "--config",
            _normalize_cli_path(request.config_path, workspace_path),
        ]
        if request.outputs_root is not None:
            command.extend(["--outputs-root", _normalize_cli_path(request.outputs_root, workspace_path)])
        command.extend(self.config.default_args)
        command.extend(_serialize_extra_args(request.extra_args))
        return command

    def render(self, request: Wan2VaceRequest) -> Wan2VaceRunResult:
        if not self.config.enabled:
            raise RuntimeError("wan2_vace_disabled")

        workspace_path = self.config.workspace_path
        if workspace_path is None:
            raise RuntimeError("wan2_vace_workspace_missing")

        script_path = self.config.script_path
        if script_path is None or not script_path.exists():
            raise FileNotFoundError("wan2_vace_script_missing")

        config_path = _resolve_workspace_path(request.config_path, workspace_path)
        if not config_path.exists():
            raise FileNotFoundError("wan2_vace_config_missing")

        outputs_root = _resolve_outputs_root(request.outputs_root, workspace_path)
        existing_meta_paths = {
            str(path) for path in _list_meta_paths(outputs_root, request.experiment_name)
        }
        command = self.build_command(request)
        result = subprocess.run(  # noqa: S603
            command,
            cwd=workspace_path,
            env=os.environ.copy(),
            capture_output=True,
            text=True,
            timeout=self.config.timeout_sec,
            check=False,
        )

        meta_path = _select_meta_path(
            outputs_root=outputs_root,
            experiment_name=request.experiment_name,
            existing_meta_paths=existing_meta_paths,
        )
        if meta_path is None:
            detail = _truncate_output(result.stderr or result.stdout)
            if result.returncode != 0:
                raise RuntimeError(f"wan2_vace_failed:{result.returncode}:{detail}")
            raise FileNotFoundError("wan2_vace_meta_missing")

        run_result = _load_run_result(meta_path, workspace_path)
        if result.returncode != 0 or run_result.status != "ok":
            detail = run_result.error or _truncate_output(result.stderr or result.stdout)
            raise RuntimeError(f"wan2_vace_failed:{result.returncode}:{detail}")
        if run_result.video_path is None:
            raise FileNotFoundError("wan2_vace_video_missing")
        return run_result


def _serialize_extra_args(extra_args: Mapping[str, str | int | float | bool]) -> list[str]:
    serialized: list[str] = []
    for key, value in extra_args.items():
        option = f"--{key.replace('_', '-')}"
        if isinstance(value, bool):
            if value:
                serialized.append(option)
            continue
        serialized.extend([option, str(value)])
    return serialized


def _resolve_workspace_path(path: Path, workspace_path: Path) -> Path:
    candidate = path if path.is_absolute() else workspace_path / path
    return candidate.resolve(strict=False)


def _normalize_cli_path(path: Path, workspace_path: Path) -> str:
    candidate = _resolve_workspace_path(path, workspace_path)
    try:
        return str(candidate.relative_to(workspace_path))
    except ValueError:
        return str(candidate)


def _resolve_outputs_root(outputs_root: Path | None, workspace_path: Path) -> Path:
    if outputs_root is None:
        return (workspace_path / "outputs").resolve(strict=False)
    return _resolve_workspace_path(outputs_root, workspace_path)


def _list_meta_paths(outputs_root: Path, experiment_name: str) -> list[Path]:
    experiment_dir = outputs_root / experiment_name
    if not experiment_dir.exists():
        return []
    return sorted(
        (path.resolve(strict=False) for path in experiment_dir.glob("*/meta.json")),
        key=_path_sort_key,
    )


def _path_sort_key(path: Path) -> tuple[int, str]:
    stat = path.stat()
    return (stat.st_mtime_ns, str(path))


def _select_meta_path(
    outputs_root: Path,
    experiment_name: str,
    existing_meta_paths: set[str],
) -> Path | None:
    meta_paths = _list_meta_paths(outputs_root, experiment_name)
    if not meta_paths:
        return None
    new_meta_paths = [path for path in meta_paths if str(path) not in existing_meta_paths]
    if new_meta_paths:
        return new_meta_paths[-1]
    return meta_paths[-1]


def _load_run_result(meta_path: Path, workspace_path: Path) -> Wan2VaceRunResult:
    payload = json.loads(meta_path.read_text(encoding="utf-8"))
    status = str(payload.get("run", {}).get("status", "unknown"))
    error = payload.get("run", {}).get("error")
    video_raw = payload.get("output", {}).get("video_path")
    video_path = _resolve_workspace_path(Path(video_raw), workspace_path) if video_raw else None
    return Wan2VaceRunResult(
        run_dir=meta_path.parent,
        meta_path=meta_path,
        video_path=video_path,
        status=status,
        error=str(error) if error is not None else None,
    )


def _truncate_output(output: str | None) -> str:
    return (output or "").strip()[:240]


def load_wan2_vace_adapter_from_env(env: Mapping[str, str] | None = None) -> Wan2VaceAdapter:
    source = env if env is not None else os.environ
    workspace_raw = str(source.get("WORKER_WAN_VACE_WORKSPACE", "")).strip()
    default_args_raw = str(source.get("WORKER_WAN_VACE_DEFAULT_ARGS", "")).strip()
    config = Wan2VaceAdapterConfig(
        workspace_path=Path(workspace_raw).resolve() if workspace_raw else None,
        python_executable=str(source.get("WORKER_WAN_VACE_PYTHON", "python")).strip() or "python",
        inference_script=str(source.get("WORKER_WAN_VACE_SCRIPT", "scripts/run_inference.py")).strip()
        or "scripts/run_inference.py",
        timeout_sec=max(
            30,
            int(str(source.get("WORKER_WAN_VACE_TIMEOUT_SEC", "5400")).strip() or "5400"),
        ),
        enabled=_is_truthy(source.get("WORKER_WAN_VACE_ENABLED")),
        default_args=tuple(shlex.split(default_args_raw)) if default_args_raw else (),
    )
    return Wan2VaceAdapter(config)
