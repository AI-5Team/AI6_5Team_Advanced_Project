from __future__ import annotations

import json
import sys
from pathlib import Path

from services.worker.adapters.adapter_wan2_vace import (
    Wan2VaceRequest,
    load_wan2_vace_adapter_from_env,
)


def test_load_wan2_vace_adapter_defaults_to_disabled() -> None:
    adapter = load_wan2_vace_adapter_from_env({})

    assert adapter.config.enabled is False
    assert adapter.config.workspace_path is None
    assert adapter.is_configured() is False


def test_build_command_uses_workspace_boundary(tmp_path: Path) -> None:
    workspace = tmp_path / "i2v-motion-experiments"
    script_path = workspace / "scripts" / "run_inference.py"
    config_path = workspace / "configs" / "experiments" / "smoke.yaml"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text("print('placeholder')\n", encoding="utf-8")
    config_path.write_text("experiment: smoke\n", encoding="utf-8")

    adapter = load_wan2_vace_adapter_from_env(
        {
            "WORKER_WAN_VACE_ENABLED": "1",
            "WORKER_WAN_VACE_WORKSPACE": str(workspace),
            "WORKER_WAN_VACE_PYTHON": sys.executable,
            "WORKER_WAN_VACE_DEFAULT_ARGS": "--trace",
        }
    )

    request = Wan2VaceRequest(
        config_path=config_path,
        experiment_name="smoke",
        outputs_root=workspace / "custom-outputs",
        extra_args={"profile": "smoke", "use_cache": True},
    )
    command = adapter.build_command(request)

    assert command[0] == sys.executable
    assert command[1] == str(script_path.resolve())
    assert "--config" in command
    assert Path(command[command.index("--config") + 1]) == Path("configs/experiments/smoke.yaml")
    assert "--outputs-root" in command
    assert Path(command[command.index("--outputs-root") + 1]) == Path("custom-outputs")
    assert "--trace" in command
    assert "--profile" in command
    assert "smoke" in command
    assert "--use-cache" in command
    assert adapter.is_configured() is True


def test_render_executes_configured_script_and_reads_meta(tmp_path: Path) -> None:
    workspace = tmp_path / "wan-workspace"
    script_path = workspace / "scripts" / "run_inference.py"
    config_path = workspace / "configs" / "experiments" / "smoke.yaml"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("experiment: smoke\n", encoding="utf-8")
    script_path.write_text(
        "\n".join(
            [
                "from __future__ import annotations",
                "import argparse",
                "import json",
                "from pathlib import Path",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--config')",
                "parser.add_argument('--outputs-root', default='outputs')",
                "args = parser.parse_args()",
                "config_path = Path(args.config)",
                "if not config_path.is_absolute():",
                "    config_path = Path.cwd() / config_path",
                "experiment = config_path.stem",
                "outputs_root = Path(args.outputs_root)",
                "if not outputs_root.is_absolute():",
                "    outputs_root = Path.cwd() / outputs_root",
                "run_dir = outputs_root / experiment / f'{experiment}_20260423-010203_seed42'",
                "run_dir.mkdir(parents=True, exist_ok=True)",
                "video_path = run_dir / 'wan21_vace_i2v_42.mp4'",
                "video_path.write_text('generated', encoding='utf-8')",
                "meta = {'run': {'status': 'ok', 'error': None}, 'output': {'video_path': str(video_path)}}",
                "(run_dir / 'meta.json').write_text(json.dumps(meta), encoding='utf-8')",
            ]
        ),
        encoding="utf-8",
    )
    output_root = workspace / "custom-outputs"

    adapter = load_wan2_vace_adapter_from_env(
        {
            "WORKER_WAN_VACE_ENABLED": "true",
            "WORKER_WAN_VACE_WORKSPACE": str(workspace),
            "WORKER_WAN_VACE_PYTHON": sys.executable,
            "WORKER_WAN_VACE_TIMEOUT_SEC": "60",
        }
    )

    result = adapter.render(
        Wan2VaceRequest(
            config_path=config_path,
            experiment_name="smoke",
            outputs_root=output_root,
        )
    )

    assert result.status == "ok"
    assert result.video_path is not None
    assert result.run_dir == result.meta_path.parent
    assert result.video_path.exists() is True
    assert result.video_path.read_text(encoding="utf-8") == "generated"


def test_render_raises_when_meta_reports_error(tmp_path: Path) -> None:
    workspace = tmp_path / "wan-workspace"
    script_path = workspace / "scripts" / "run_inference.py"
    config_path = workspace / "configs" / "experiments" / "broken.yaml"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("experiment: broken\n", encoding="utf-8")
    script_path.write_text(
        "\n".join(
            [
                "from __future__ import annotations",
                "import argparse",
                "import json",
                "from pathlib import Path",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--config')",
                "parser.add_argument('--outputs-root', default='outputs')",
                "args = parser.parse_args()",
                "outputs_root = Path(args.outputs_root)",
                "if not outputs_root.is_absolute():",
                "    outputs_root = Path.cwd() / outputs_root",
                "run_dir = outputs_root / 'broken' / 'broken_20260423-010203_seed42'",
                "run_dir.mkdir(parents=True, exist_ok=True)",
                "meta = {'run': {'status': 'error', 'error': 'RuntimeError: smoke failure'}, 'output': {'video_path': None}}",
                "(run_dir / 'meta.json').write_text(json.dumps(meta), encoding='utf-8')",
                "raise SystemExit(1)",
            ]
        ),
        encoding="utf-8",
    )

    adapter = load_wan2_vace_adapter_from_env(
        {
            "WORKER_WAN_VACE_ENABLED": "true",
            "WORKER_WAN_VACE_WORKSPACE": str(workspace),
            "WORKER_WAN_VACE_PYTHON": sys.executable,
        }
    )

    try:
        adapter.render(
            Wan2VaceRequest(
                config_path=config_path,
                experiment_name="broken",
                outputs_root=workspace / "custom-outputs",
            )
        )
    except RuntimeError as exc:
        assert "smoke failure" in str(exc)
    else:
        raise AssertionError("expected RuntimeError for error meta")
