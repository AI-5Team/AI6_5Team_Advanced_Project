from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

from services.worker.utils.runtime import ensure_dir


CANVAS_SIZE = (720, 1280)
POST_SIZE = (1080, 1080)

MOTION_PRESET_EXPRESSIONS = {
    "push_in_center": {
        "zoom": "if(eq(on,1),1.0,min(zoom+0.0015,1.10))",
        "x": "iw/2-(iw/zoom/2)",
        "y": "ih/2-(ih/zoom/2)",
    },
    "push_in_top": {
        "zoom": "if(eq(on,1),1.0,min(zoom+0.0014,1.10))",
        "x": "iw/2-(iw/zoom/2)",
        "y": "ih*0.38-(ih/zoom/2)",
    },
    "push_in_bottom": {
        "zoom": "if(eq(on,1),1.0,min(zoom+0.0014,1.10))",
        "x": "iw/2-(iw/zoom/2)",
        "y": "ih*0.62-(ih/zoom/2)",
    },
}


def preprocess_asset(source_path: Path, processed_dir: Path, asset_id: str) -> dict[str, Path]:
    ensure_dir(processed_dir)
    image = Image.open(source_path).convert("RGB")
    vertical = ImageOps.fit(image, CANVAS_SIZE, method=Image.Resampling.LANCZOS)
    square = ImageOps.fit(image, POST_SIZE, method=Image.Resampling.LANCZOS)
    vertical = ImageEnhancer(vertical).apply()
    square = ImageEnhancer(square).apply()

    vertical_path = processed_dir / f"{asset_id}_vertical.png"
    square_path = processed_dir / f"{asset_id}_square.png"
    vertical.save(vertical_path)
    square.save(square_path)
    return {"vertical": vertical_path, "square": square_path}


class ImageEnhancer:
    def __init__(self, image: Image.Image):
        self.image = image

    def apply(self) -> Image.Image:
        return self.image.filter(ImageFilter.GaussianBlur(radius=0.2))


def create_scene_image(output_path: Path, base_image_path: Path, primary_text: str, secondary_text: str, style_id: str, badge_text: str | None = None) -> None:
    base = Image.open(base_image_path).convert("RGB").resize(CANVAS_SIZE, Image.Resampling.LANCZOS)
    ensure_dir(output_path.parent)
    base.save(output_path)


def create_scene_overlay_image(output_path: Path, primary_text: str, secondary_text: str, style_id: str, badge_text: str | None = None) -> None:
    overlay = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    ensure_dir(output_path.parent)
    overlay.save(output_path)


def create_post_image(output_path: Path, base_image_path: Path, headline: str, body: str, cta_text: str, style_id: str) -> None:
    base = Image.open(base_image_path).convert("RGB").resize(POST_SIZE, Image.Resampling.LANCZOS)
    ensure_dir(output_path.parent)
    base.save(output_path)


def _run_ffmpeg(command: list[str], error_message: str) -> None:
    completed = subprocess.run(command, check=False, capture_output=True, text=True, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or error_message)


def _probe_video_duration(source_video_path: Path) -> float:
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(source_video_path.resolve()),
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "ffprobe duration probe failed")
    try:
        return float(completed.stdout.strip())
    except ValueError as exc:
        raise RuntimeError("ffprobe duration probe returned invalid output") from exc


def _render_static_video(scene_specs: list[tuple[Path, float]], output_path: Path) -> None:
    ensure_dir(output_path.parent)
    with tempfile.TemporaryDirectory() as temp_dir:
        concat_path = Path(temp_dir) / "concat.txt"
        lines: list[str] = []
        for image_path, duration in scene_specs:
            lines.append(f"file '{image_path.resolve().as_posix()}'")
            lines.append(f"duration {duration}")
        lines.append(f"file '{scene_specs[-1][0].resolve().as_posix()}'")
        concat_path.write_text("\n".join(lines), encoding="utf-8")

        command = [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
            "-vsync",
            "vfr",
            "-pix_fmt",
            "yuv420p",
            str(output_path.resolve()),
        ]
        _run_ffmpeg(command, "ffmpeg static render failed")


def _render_zoompan_clip(image_path: Path, output_path: Path, *, duration_sec: float, preset: str, fps: int = 12) -> None:
    ensure_dir(output_path.parent)
    if preset not in MOTION_PRESET_EXPRESSIONS:
        raise ValueError(f"unsupported motion preset: {preset}")

    frames = max(1, round(duration_sec * fps))
    motion = MOTION_PRESET_EXPRESSIONS[preset]
    zoompan_filter = (
        f"zoompan=z='{motion['zoom']}':x='{motion['x']}':y='{motion['y']}':d={frames}:"
        f"s={CANVAS_SIZE[0]}x{CANVAS_SIZE[1]}:fps={fps}"
    )
    command = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-loop",
        "1",
        "-i",
        str(image_path.resolve()),
        "-vf",
        zoompan_filter,
        "-t",
        str(duration_sec),
        "-pix_fmt",
        "yuv420p",
        str(output_path.resolve()),
    ]
    _run_ffmpeg(command, "ffmpeg zoompan render failed")


def _render_motion_video(scene_specs: list[tuple[Path, float, str]], output_path: Path) -> None:
    ensure_dir(output_path.parent)
    with tempfile.TemporaryDirectory() as temp_dir:
        clips_dir = Path(temp_dir) / "clips"
        clips_dir.mkdir(parents=True, exist_ok=True)
        clip_paths: list[Path] = []
        for index, (scene_image_path, duration_sec, preset) in enumerate(scene_specs, start=1):
            clip_path = clips_dir / f"scene_{index:02d}.mp4"
            _render_zoompan_clip(scene_image_path, clip_path, duration_sec=duration_sec, preset=preset)
            clip_paths.append(clip_path)

        concat_path = Path(temp_dir) / "concat.txt"
        concat_lines = [f"file '{clip_path.resolve().as_posix()}'" for clip_path in clip_paths]
        concat_path.write_text("\n".join(concat_lines), encoding="utf-8")
        command = [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(output_path.resolve()),
        ]
        _run_ffmpeg(command, "ffmpeg motion concat render failed")


def render_hybrid_video(source_video_path: Path, overlay_specs: list[tuple[Path, float, float]], output_path: Path) -> None:
    if not overlay_specs:
        raise ValueError("overlay_specs must not be empty")

    ensure_dir(output_path.parent)
    source_duration_sec = _probe_video_duration(source_video_path)
    target_duration_sec = max(end_sec for _, _, end_sec in overlay_specs)
    command = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-i",
        str(source_video_path.resolve()),
    ]
    for overlay_path, _, _ in overlay_specs:
        command.extend(["-i", str(overlay_path.resolve())])

    filter_parts: list[str] = []
    previous_label = "[0:v]"
    if source_duration_sec < target_duration_sec:
        pad_duration_sec = round(target_duration_sec - source_duration_sec, 3)
        filter_parts.append(f"[0:v]tpad=stop_mode=clone:stop_duration={pad_duration_sec}[base]")
        previous_label = "[base]"
    for index, (_, start_sec, end_sec) in enumerate(overlay_specs, start=1):
        output_label = f"[v{index}]"
        filter_parts.append(
            f"{previous_label}[{index}:v]overlay=0:0:enable='between(t,{start_sec},{end_sec})'{output_label}"
        )
        previous_label = output_label

    command.extend(
        [
            "-filter_complex",
            ";".join(filter_parts),
            "-map",
            previous_label,
            "-map",
            "0:a?",
            "-c:v",
            "libx264",
            "-c:a",
            "copy",
            "-pix_fmt",
            "yuv420p",
            str(output_path.resolve()),
        ]
    )
    _run_ffmpeg(command, "ffmpeg hybrid overlay render failed")


def render_video(scene_specs: list[tuple[Path, float]], output_path: Path, *, motion_presets: list[str] | None = None) -> None:
    if not scene_specs:
        raise ValueError("scene_specs must not be empty")
    if motion_presets is None:
        _render_static_video(scene_specs, output_path)
        return
    if len(motion_presets) != len(scene_specs):
        raise ValueError("motion_presets length must match scene_specs length")
    motion_scene_specs = [
        (image_path, duration, motion_presets[index])
        for index, (image_path, duration) in enumerate(scene_specs)
    ]
    _render_motion_video(motion_scene_specs, output_path)
