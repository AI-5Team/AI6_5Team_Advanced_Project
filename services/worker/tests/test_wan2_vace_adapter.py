from __future__ import annotations

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
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text("print('placeholder')\n", encoding="utf-8")

    adapter = load_wan2_vace_adapter_from_env(
        {
            "WORKER_WAN_VACE_ENABLED": "1",
            "WORKER_WAN_VACE_WORKSPACE": str(workspace),
            "WORKER_WAN_VACE_PYTHON": sys.executable,
            "WORKER_WAN_VACE_DEFAULT_ARGS": "--steps 24 --seed 7",
        }
    )

    request = Wan2VaceRequest(
        input_image_path=tmp_path / "input.png",
        output_video_path=tmp_path / "out" / "video.mp4",
        prompt="성수동 맥주잔 질감 강조",
        negative_prompt="손 왜곡 금지",
        extra_args={"fps": 12, "use_fp16": True},
    )
    command = adapter.build_command(request)

    assert command[0] == sys.executable
    assert command[1] == str(script_path.resolve())
    assert "--input-image" in command
    assert str(request.input_image_path) in command
    assert "--output-video" in command
    assert str(request.output_video_path) in command
    assert "--negative-prompt" in command
    assert "손 왜곡 금지" in command
    assert "--steps" in command
    assert "--seed" in command
    assert "--fps" in command
    assert "--use-fp16" in command
    assert adapter.is_configured() is True


def test_render_executes_configured_script(tmp_path: Path) -> None:
    workspace = tmp_path / "wan-workspace"
    script_path = workspace / "scripts" / "run_inference.py"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(
        "\n".join(
            [
                "from __future__ import annotations",
                "import argparse",
                "from pathlib import Path",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--mode')",
                "parser.add_argument('--input-image')",
                "parser.add_argument('--output-video')",
                "parser.add_argument('--prompt')",
                "parser.add_argument('--negative-prompt', default='')",
                "args = parser.parse_args()",
                "Path(args.output_video).write_text('|'.join([args.mode, args.input_image, args.prompt, args.negative_prompt]), encoding='utf-8')",
            ]
        ),
        encoding="utf-8",
    )
    input_image = tmp_path / "input.png"
    input_image.write_text("placeholder", encoding="utf-8")
    output_video = tmp_path / "outputs" / "video.mp4"

    adapter = load_wan2_vace_adapter_from_env(
        {
            "WORKER_WAN_VACE_ENABLED": "true",
            "WORKER_WAN_VACE_WORKSPACE": str(workspace),
            "WORKER_WAN_VACE_PYTHON": sys.executable,
            "WORKER_WAN_VACE_TIMEOUT_SEC": "60",
        }
    )

    result_path = adapter.render(
        Wan2VaceRequest(
            input_image_path=input_image,
            output_video_path=output_video,
            prompt="광고 컷 smoke run",
            negative_prompt="왜곡 금지",
        )
    )

    assert result_path == output_video
    assert output_video.exists() is True
    assert "광고 컷 smoke run" in output_video.read_text(encoding="utf-8")
