from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image

from services.worker.renderers.media import create_scene_overlay_image, render_hybrid_video, render_video


def make_png(path: Path, color: tuple[int, int, int]) -> None:
    image = Image.new("RGB", (720, 1280), color)
    image.save(path, format="PNG")


def probe_duration(path: Path) -> float:
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout
    return float(completed.stdout.strip())


def test_render_video_supports_motion_presets(tmp_path: Path) -> None:
    scene_a = tmp_path / "scene-a.png"
    scene_b = tmp_path / "scene-b.png"
    output_path = tmp_path / "motion-video.mp4"
    make_png(scene_a, (220, 120, 80))
    make_png(scene_b, (90, 120, 220))

    render_video(
        [(scene_a, 1.0), (scene_b, 1.2)],
        output_path,
        motion_presets=["push_in_center", "push_in_top"],
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 0
    assert probe_duration(output_path) >= 1.9


def test_render_hybrid_video_overlays_generated_clip(tmp_path: Path) -> None:
    scene_a = tmp_path / "scene-a.png"
    scene_b = tmp_path / "scene-b.png"
    source_video = tmp_path / "source.mp4"
    overlay_a = tmp_path / "overlay-a.png"
    overlay_b = tmp_path / "overlay-b.png"
    output_path = tmp_path / "hybrid.mp4"

    make_png(scene_a, (220, 120, 80))
    make_png(scene_b, (90, 120, 220))
    render_video([(scene_a, 1.0), (scene_b, 1.0)], source_video, motion_presets=["push_in_center", "push_in_top"])

    create_scene_overlay_image(overlay_a, "HOOK", "Generated clip packaging", "b_grade_fun", badge_text="HOOK")
    create_scene_overlay_image(overlay_b, "CTA", "Overlay bridge check", "b_grade_fun", badge_text="CTA")

    render_hybrid_video(
        source_video,
        [
            (overlay_a, 0.0, 1.0),
            (overlay_b, 1.0, 2.8),
        ],
        output_path,
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 0
    assert probe_duration(output_path) >= 2.7
