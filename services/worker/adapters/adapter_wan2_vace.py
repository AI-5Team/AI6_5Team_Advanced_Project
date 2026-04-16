from __future__ import annotations

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
    input_image_path: Path
    output_video_path: Path
    prompt: str
    negative_prompt: str | None = None
    mode: str = "i2v"
    extra_args: dict[str, str | int | float | bool] = field(default_factory=dict)


@dataclass(frozen=True)
class Wan2VaceAdapterConfig:
    workspace_path: Path | None = None
    python_executable: str = "python"
    inference_script: str = "scripts/run_inference.py"
    timeout_sec: int = 900
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
        script_path = self.config.script_path
        if self.config.workspace_path is None or script_path is None:
            raise RuntimeError("wan2_vace_workspace_missing")

        command = [
            self.config.python_executable,
            str(script_path),
            "--mode",
            request.mode,
            "--input-image",
            str(request.input_image_path),
            "--output-video",
            str(request.output_video_path),
            "--prompt",
            request.prompt,
        ]
        if request.negative_prompt:
            command.extend(["--negative-prompt", request.negative_prompt])
        command.extend(self.config.default_args)
        command.extend(_serialize_extra_args(request.extra_args))
        return command

    def render(self, request: Wan2VaceRequest) -> Path:
        if not self.config.enabled:
            raise RuntimeError("wan2_vace_disabled")

        if self.config.workspace_path is None:
            raise RuntimeError("wan2_vace_workspace_missing")

        script_path = self.config.script_path
        if script_path is None or not script_path.exists():
            raise FileNotFoundError("wan2_vace_script_missing")

        request.output_video_path.parent.mkdir(parents=True, exist_ok=True)
        command = self.build_command(request)
        result = subprocess.run(  # noqa: S603
            command,
            cwd=self.config.workspace_path,
            env=os.environ.copy(),
            capture_output=True,
            text=True,
            timeout=self.config.timeout_sec,
            check=False,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "").strip()[:240]
            raise RuntimeError(f"wan2_vace_failed:{result.returncode}:{detail}")
        return request.output_video_path


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


def load_wan2_vace_adapter_from_env(env: Mapping[str, str] | None = None) -> Wan2VaceAdapter:
    source = env if env is not None else os.environ
    workspace_raw = str(source.get("WORKER_WAN_VACE_WORKSPACE", "")).strip()
    default_args_raw = str(source.get("WORKER_WAN_VACE_DEFAULT_ARGS", "")).strip()
    config = Wan2VaceAdapterConfig(
        workspace_path=Path(workspace_raw).resolve() if workspace_raw else None,
        python_executable=str(source.get("WORKER_WAN_VACE_PYTHON", "python")).strip() or "python",
        inference_script=str(source.get("WORKER_WAN_VACE_SCRIPT", "scripts/run_inference.py")).strip()
        or "scripts/run_inference.py",
        timeout_sec=max(30, int(str(source.get("WORKER_WAN_VACE_TIMEOUT_SEC", "900")).strip() or "900")),
        enabled=_is_truthy(source.get("WORKER_WAN_VACE_ENABLED")),
        default_args=tuple(shlex.split(default_args_raw)) if default_args_raw else (),
    )
    return Wan2VaceAdapter(config)
