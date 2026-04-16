from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from video_benchmark_common import (
    SAMPLE_LIBRARY,
    build_upper_bound_prompt,
    create_contact_sheet,
    extract_video_frames,
    image_metrics,
    infer_label,
    prepare_image,
    resolve_prepare_mode,
    video_motion_metrics,
)
from video_quality_gate import annotate_benchmark_summary
from services.worker.renderers.media import CANVAS_SIZE, create_scene_image


DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-90-upper-bound-video-benchmark"
DEFAULT_IMAGES = (SAMPLE_LIBRARY["규카츠"], SAMPLE_LIBRARY["맥주"])
DEFAULT_MANUAL_VEO_DIR = DEFAULT_OUTPUT_DIR / "manual" / "veo"
DEFAULT_BENCHMARK_ID = "EXP-90-upper-bound-video-benchmark-pilot"


def build_product_control_scene_specs(label: str, resolved_prepare_mode: str) -> list[dict[str, object]]:
    if label == "맥주":
        return [
            {
                "scene_id": "s1",
                "duration_sec": 0.9,
                "primary_text": "맥주각 바로 옴",
                "secondary_text": "첫 장면에서 시원함부터 꽂기",
                "badge_text": "HOOK",
                "prepare_mode": "cover_bottom",
            },
            {
                "scene_id": "s2",
                "duration_sec": 0.9,
                "primary_text": "거품이랑 병 라벨 먼저",
                "secondary_text": "브랜드 느낌 안 깨고 컷만 빠르게",
                "badge_text": "DETAIL",
                "prepare_mode": resolved_prepare_mode,
            },
            {
                "scene_id": "s3",
                "duration_sec": 1.0,
                "primary_text": "퇴근길 1차 각",
                "secondary_text": "영상은 과장, 제품은 그대로",
                "badge_text": "MOOD",
                "prepare_mode": "cover_center",
            },
            {
                "scene_id": "s4",
                "duration_sec": 1.2,
                "primary_text": "저장 말고 바로 방문",
                "secondary_text": "B급 템포로 마무리 CTA",
                "badge_text": "CTA",
                "prepare_mode": "cover_bottom",
            },
        ]

    return [
        {
            "scene_id": "s1",
            "duration_sec": 0.9,
            "primary_text": "규카츠 비주얼 바로 꽂기",
            "secondary_text": "첫 컷에서 메뉴 정체성부터 고정",
            "badge_text": "HOOK",
            "prepare_mode": "cover_center",
        },
        {
            "scene_id": "s2",
            "duration_sec": 0.9,
            "primary_text": "튀김 결이랑 단면 강조",
            "secondary_text": "원본 음식 모양은 건드리지 않기",
            "badge_text": "DETAIL",
            "prepare_mode": resolved_prepare_mode,
        },
        {
            "scene_id": "s3",
            "duration_sec": 1.0,
            "primary_text": "과장된 문구는 허용",
            "secondary_text": "메뉴 변형은 불허",
            "badge_text": "RULE",
            "prepare_mode": "cover_top",
        },
        {
            "scene_id": "s4",
            "duration_sec": 1.2,
            "primary_text": "지금 바로 저장 말고 방문",
            "secondary_text": "템플릿 컷으로 B급 광고 완성",
            "badge_text": "CTA",
            "prepare_mode": "cover_center",
        },
    ]


def build_product_control_motion_presets(label: str) -> list[str]:
    if label == "맥주":
        return ["push_in_bottom", "push_in_bottom", "push_in_center", "push_in_bottom"]
    return ["push_in_center", "push_in_center", "push_in_top", "push_in_center"]


def run_command(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def read_summary(summary_path: Path) -> dict[str, object]:
    return json.loads(summary_path.read_text(encoding="utf-8"))


def render_control_video(scene_specs: list[tuple[Path, float]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
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
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "ffmpeg render failed")


def render_zoompan_clip(image_path: Path, output_path: Path, *, duration_sec: float, preset: str, fps: int = 12) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames = max(1, round(duration_sec * fps))
    if preset == "push_in_center":
        zoom_expr = "if(eq(on,1),1.0,min(zoom+0.0015,1.10))"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"
    elif preset == "push_in_bottom":
        zoom_expr = "if(eq(on,1),1.0,min(zoom+0.0014,1.10))"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih*0.62-(ih/zoom/2)"
    elif preset == "push_in_top":
        zoom_expr = "if(eq(on,1),1.0,min(zoom+0.0014,1.10))"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih*0.38-(ih/zoom/2)"
    else:
        raise ValueError(f"unsupported motion preset: {preset}")

    zoompan_filter = (
        f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}':d={frames}:"
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
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "ffmpeg zoompan render failed")


def render_control_motion_video(scene_specs: list[tuple[Path, float, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    clips_dir = output_path.parent / "_clips"
    clips_dir.mkdir(parents=True, exist_ok=True)
    clip_paths: list[Path] = []
    for index, (scene_image_path, duration_sec, preset) in enumerate(scene_specs, start=1):
        clip_path = clips_dir / f"scene_{index:02d}.mp4"
        render_zoompan_clip(scene_image_path, clip_path, duration_sec=duration_sec, preset=preset)
        clip_paths.append(clip_path)

    with tempfile.TemporaryDirectory() as temp_dir:
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
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "ffmpeg concat motion render failed")


def zoom_crop(image: Image.Image, *, scale: float, y_bias: float) -> Image.Image:
    width, height = image.size
    crop_width = int(width * scale)
    crop_height = int(height * scale)
    center_x = width / 2
    center_y = height * (0.5 + y_bias)
    left = round(center_x - crop_width / 2)
    top = round(center_y - crop_height / 2)
    left = max(0, min(left, width - crop_width))
    top = max(0, min(top, height - crop_height))
    right = left + crop_width
    bottom = top + crop_height
    return image.crop((left, top, right, bottom)).resize((width, height), Image.Resampling.LANCZOS)


def build_sora_current_best_input(image_path: Path, output_dir: Path) -> tuple[Path, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    resolved_prepare_mode = resolve_prepare_mode(image_path, "auto")
    base_input = prepare_image(image_path, 1280, 720, resolved_prepare_mode)
    y_bias_map = {
        "cover_top": -0.04,
        "cover_center": 0.0,
        "cover_bottom": 0.06,
        "contain_blur": 0.0,
    }
    hero_tight = zoom_crop(base_input, scale=0.8, y_bias=y_bias_map.get(resolved_prepare_mode, 0.0))
    prepared_variant_path = output_dir / "hero_tight_zoom.png"
    hero_tight.save(prepared_variant_path)
    return prepared_variant_path, resolved_prepare_mode


def run_product_control(image_path: Path, output_dir: Path) -> dict[str, object]:
    label = infer_label(image_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    resolved_prepare_mode = resolve_prepare_mode(image_path, "auto")
    prepared_input_path = output_dir / "prepared_input.png"
    prepare_image(image_path, CANVAS_SIZE[0], CANVAS_SIZE[1], resolved_prepare_mode).save(prepared_input_path)

    scene_specs = build_product_control_scene_specs(label, resolved_prepare_mode)
    rendered_scenes: list[tuple[Path, float]] = []
    for scene in scene_specs:
        scene_id = str(scene["scene_id"])
        scene_prepare_mode = str(scene["prepare_mode"])
        base_path = output_dir / f"{scene_id}_base.png"
        scene_image_path = output_dir / f"{scene_id}.png"
        prepare_image(image_path, CANVAS_SIZE[0], CANVAS_SIZE[1], scene_prepare_mode).save(base_path)
        create_scene_image(
            scene_image_path,
            base_path,
            str(scene["primary_text"]),
            str(scene["secondary_text"]),
            style_id="b_grade_fun",
            badge_text=str(scene["badge_text"]),
        )
        rendered_scenes.append((scene_image_path, float(scene["duration_sec"])))

    output_video = output_dir / "product_control.mp4"
    render_control_video(rendered_scenes, output_video)
    first_frame_path, mid_frame_path = extract_video_frames(output_video, output_dir, midpoint_seconds=2.0)
    contact_sheet_path = create_contact_sheet(output_video, output_dir / "contact_sheet.png")
    summary_path = output_dir / "summary.json"
    summary = {
        "provider": "product_control",
        "control_type": "template_motion_compositor",
        "image": str(image_path),
        "label": label,
        "prepared_input": str(prepared_input_path),
        "resolved_prepare_mode": resolved_prepare_mode,
        "scene_specs": scene_specs,
        "status": "completed",
        "output_video": str(output_video),
        "output_first_frame": str(first_frame_path),
        "output_mid_frame": str(mid_frame_path),
        "contact_sheet": str(contact_sheet_path),
        "mid_frame_metrics": image_metrics(prepared_input_path, mid_frame_path),
        "motion_metrics": video_motion_metrics(output_video),
        "packaging_fit": "native_control",
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "provider": "product_control",
        "summary_path": str(summary_path),
        "returncode": 0,
        "status": "completed",
        "elapsed_seconds": None,
        "resolved_prepare_mode": resolved_prepare_mode,
        "mid_frame_metrics": summary["mid_frame_metrics"],
        "motion_metrics": summary["motion_metrics"],
        "output_mid_frame": str(mid_frame_path),
        "output_video": str(output_video),
        "contact_sheet": str(contact_sheet_path),
        "error": None,
        "control_type": "template_motion_compositor",
        "packaging_fit": "native_control",
    }


def run_product_control_motion(image_path: Path, output_dir: Path) -> dict[str, object]:
    label = infer_label(image_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    resolved_prepare_mode = resolve_prepare_mode(image_path, "auto")
    prepared_input_path = output_dir / "prepared_input.png"
    prepare_image(image_path, CANVAS_SIZE[0], CANVAS_SIZE[1], resolved_prepare_mode).save(prepared_input_path)

    scene_specs = build_product_control_scene_specs(label, resolved_prepare_mode)
    motion_presets = build_product_control_motion_presets(label)
    rendered_scenes: list[tuple[Path, float, str]] = []
    motion_scene_specs: list[dict[str, object]] = []
    for scene, motion_preset in zip(scene_specs, motion_presets, strict=True):
        scene_id = str(scene["scene_id"])
        scene_prepare_mode = str(scene["prepare_mode"])
        base_path = output_dir / f"{scene_id}_base.png"
        scene_image_path = output_dir / f"{scene_id}.png"
        prepare_image(image_path, CANVAS_SIZE[0], CANVAS_SIZE[1], scene_prepare_mode).save(base_path)
        create_scene_image(
            scene_image_path,
            base_path,
            str(scene["primary_text"]),
            str(scene["secondary_text"]),
            style_id="b_grade_fun",
            badge_text=str(scene["badge_text"]),
        )
        rendered_scenes.append((scene_image_path, float(scene["duration_sec"]), motion_preset))
        motion_scene_specs.append({**scene, "motion_preset": motion_preset})

    output_video = output_dir / "product_control_motion.mp4"
    render_control_motion_video(rendered_scenes, output_video)
    first_frame_path, mid_frame_path = extract_video_frames(output_video, output_dir, midpoint_seconds=2.0)
    contact_sheet_path = create_contact_sheet(output_video, output_dir / "contact_sheet.png")
    summary_path = output_dir / "summary.json"
    summary = {
        "provider": "product_control_motion",
        "control_type": "template_motion_compositor_zoompan",
        "image": str(image_path),
        "label": label,
        "prepared_input": str(prepared_input_path),
        "resolved_prepare_mode": resolved_prepare_mode,
        "scene_specs": motion_scene_specs,
        "status": "completed",
        "output_video": str(output_video),
        "output_first_frame": str(first_frame_path),
        "output_mid_frame": str(mid_frame_path),
        "contact_sheet": str(contact_sheet_path),
        "mid_frame_metrics": image_metrics(prepared_input_path, mid_frame_path),
        "motion_metrics": video_motion_metrics(output_video),
        "packaging_fit": "native_control_candidate",
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "provider": "product_control_motion",
        "summary_path": str(summary_path),
        "returncode": 0,
        "status": "completed",
        "elapsed_seconds": None,
        "resolved_prepare_mode": resolved_prepare_mode,
        "mid_frame_metrics": summary["mid_frame_metrics"],
        "motion_metrics": summary["motion_metrics"],
        "output_mid_frame": str(mid_frame_path),
        "output_video": str(output_video),
        "contact_sheet": str(contact_sheet_path),
        "error": None,
        "control_type": "template_motion_compositor_zoompan",
        "packaging_fit": "native_control_candidate",
    }


def run_ltx(image_path: Path, output_dir: Path, prompt: str) -> dict[str, object]:
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "local_video_ltx_first_try.py"),
        "--image",
        str(image_path),
        "--output-dir",
        str(output_dir),
        "--num-frames",
        "25",
        "--fps",
        "8",
        "--steps",
        "6",
        "--seed",
        "7",
        "--prepare-mode",
        "auto",
        "--prompt",
        prompt,
    ]
    completed = run_command(command, cwd=REPO_ROOT)
    summary = read_summary(output_dir / "summary.json")
    prepared_input = Path(str(summary["prepared_input"]))
    output_mid_frame = Path(str(summary["output_mid_frame"]))
    output_video = Path(str(summary["output_video"]))
    contact_sheet_path = create_contact_sheet(output_video, output_dir / "contact_sheet.png")
    return {
        "provider": "local_ltx",
        "summary_path": str(output_dir / "summary.json"),
        "returncode": completed.returncode,
        "status": summary.get("status"),
        "elapsed_seconds": summary.get("elapsed_seconds"),
        "resolved_prepare_mode": summary.get("resolved_prepare_mode"),
        "mid_frame_metrics": image_metrics(prepared_input, output_mid_frame),
        "motion_metrics": video_motion_metrics(output_video),
        "output_mid_frame": summary.get("output_mid_frame"),
        "output_video": summary.get("output_video"),
        "contact_sheet": str(contact_sheet_path),
        "error": summary.get("error"),
    }


def run_veo31(image_path: Path, output_dir: Path, prompt: str) -> dict[str, object]:
    command = [
        "uv",
        "run",
        "--with",
        "google-genai",
        "python",
        str(REPO_ROOT / "scripts" / "hosted_video_veo31_first_try.py"),
        "--image",
        str(image_path),
        "--output-dir",
        str(output_dir),
        "--prompt",
        prompt,
        "--prepare-mode",
        "auto",
        "--duration-seconds",
        "4",
        "--resolution",
        "720p",
    ]
    completed = run_command(command, cwd=REPO_ROOT)
    summary = read_summary(output_dir / infer_label(image_path) / "summary.json")
    return {
        "provider": "veo31",
        "summary_path": str(output_dir / infer_label(image_path) / "summary.json"),
        "returncode": completed.returncode,
        "status": summary.get("status"),
        "elapsed_seconds": summary.get("elapsed_seconds"),
        "resolved_prepare_mode": summary.get("resolved_prepare_mode"),
        "mid_frame_metrics": summary.get("mid_frame_metrics"),
        "motion_metrics": (
            video_motion_metrics(Path(str(summary["output_video"])))
            if summary.get("status") == "completed" and summary.get("output_video")
            else None
        ),
        "output_mid_frame": summary.get("output_mid_frame"),
        "output_video": summary.get("output_video"),
        "contact_sheet": summary.get("contact_sheet"),
        "error": summary.get("error"),
    }


def run_sora2(image_path: Path, output_dir: Path, prompt: str) -> dict[str, object]:
    command = [
        "uv",
        "run",
        "--with",
        "openai",
        "python",
        str(REPO_ROOT / "scripts" / "hosted_video_sora2_first_try.py"),
        "--image",
        str(image_path),
        "--output-dir",
        str(output_dir),
        "--prompt",
        prompt,
        "--prepare-mode",
        "auto",
        "--seconds",
        "4",
    ]
    completed = run_command(command, cwd=REPO_ROOT)
    summary = read_summary(output_dir / infer_label(image_path) / "summary.json")
    return {
        "provider": "sora2",
        "summary_path": str(output_dir / infer_label(image_path) / "summary.json"),
        "returncode": completed.returncode,
        "status": summary.get("status"),
        "elapsed_seconds": summary.get("elapsed_seconds"),
        "resolved_prepare_mode": summary.get("resolved_prepare_mode"),
        "mid_frame_metrics": summary.get("mid_frame_metrics"),
        "motion_metrics": summary.get("motion_metrics")
        or (
            video_motion_metrics(Path(str(summary["output_video"])))
            if summary.get("status") == "completed" and summary.get("output_video")
            else None
        ),
        "output_mid_frame": summary.get("output_mid_frame"),
        "output_video": summary.get("output_video"),
        "contact_sheet": summary.get("contact_sheet"),
        "error": summary.get("error"),
    }


def run_sora2_current_best(image_path: Path, output_dir: Path, prompt: str) -> dict[str, object]:
    prepared_variant_path, resolved_prepare_mode = build_sora_current_best_input(image_path, output_dir / "prepared_variants")
    command = [
        "uv",
        "run",
        "--with",
        "openai",
        "python",
        str(REPO_ROOT / "scripts" / "hosted_video_sora2_first_try.py"),
        "--image",
        str(image_path),
        "--prepared-image",
        str(prepared_variant_path),
        "--output-dir",
        str(output_dir / "run"),
        "--prompt",
        prompt,
        "--prepare-mode",
        "auto",
        "--seconds",
        "4",
    ]
    completed = run_command(command, cwd=REPO_ROOT)
    summary = read_summary(output_dir / "run" / infer_label(image_path) / "summary.json")
    return {
        "provider": "sora2_current_best",
        "variant": "hero_tight_zoom",
        "summary_path": str(output_dir / "run" / infer_label(image_path) / "summary.json"),
        "returncode": completed.returncode,
        "status": summary.get("status"),
        "elapsed_seconds": summary.get("elapsed_seconds"),
        "resolved_prepare_mode": resolved_prepare_mode,
        "mid_frame_metrics": summary.get("mid_frame_metrics"),
        "motion_metrics": summary.get("motion_metrics")
        or (
            video_motion_metrics(Path(str(summary["output_video"])))
            if summary.get("status") == "completed" and summary.get("output_video")
            else None
        ),
        "output_mid_frame": summary.get("output_mid_frame"),
        "output_video": summary.get("output_video"),
        "contact_sheet": summary.get("contact_sheet"),
        "error": summary.get("error"),
        "prepared_input_variant": str(prepared_variant_path),
    }


def run_manual_provider(image_path: Path, output_dir: Path, *, provider_name: str, provider_root: Path, file_name: str) -> dict[str, object]:
    label = infer_label(image_path)
    manual_video_path = provider_root / label / file_name
    if not manual_video_path.exists():
        return {
            "provider": provider_name,
            "summary_path": None,
            "returncode": None,
            "status": "missing",
            "elapsed_seconds": None,
            "resolved_prepare_mode": None,
            "mid_frame_metrics": None,
            "output_mid_frame": None,
            "output_video": str(manual_video_path),
            "contact_sheet": None,
            "error": f"{provider_name} file not found",
        }

    output_dir.mkdir(parents=True, exist_ok=True)
    first_frame_path, mid_frame_path = extract_video_frames(manual_video_path, output_dir, midpoint_seconds=2.0)
    contact_sheet_path = create_contact_sheet(manual_video_path, output_dir / "contact_sheet.png")
    frame_size_image = Path(first_frame_path)
    from PIL import Image  # local import to keep runtime dependency narrow

    width, height = Image.open(frame_size_image).size
    resolved_prepare_mode = resolve_prepare_mode(image_path, "auto")
    prepared_input_path = output_dir / "prepared_input.png"
    prepared_image = prepare_image(image_path, width, height, resolved_prepare_mode)
    prepared_image.save(prepared_input_path)
    summary_path = output_dir / "summary.json"
    summary = {
        "provider": provider_name,
        "image": str(image_path),
        "label": label,
        "prepared_input": str(prepared_input_path),
        "prepare_mode": "auto",
        "resolved_prepare_mode": resolved_prepare_mode,
        "status": "completed",
        "output_video": str(manual_video_path),
        "output_first_frame": str(first_frame_path),
        "output_mid_frame": str(mid_frame_path),
        "contact_sheet": str(contact_sheet_path),
        "first_frame_metrics": image_metrics(prepared_input_path, first_frame_path),
        "mid_frame_metrics": image_metrics(prepared_input_path, mid_frame_path),
        "motion_metrics": video_motion_metrics(manual_video_path),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "provider": provider_name,
        "summary_path": str(summary_path),
        "returncode": 0,
        "status": "completed",
        "elapsed_seconds": None,
        "resolved_prepare_mode": resolved_prepare_mode,
        "mid_frame_metrics": summary["mid_frame_metrics"],
        "motion_metrics": summary["motion_metrics"],
        "output_mid_frame": str(mid_frame_path),
        "output_video": str(manual_video_path),
        "contact_sheet": str(contact_sheet_path),
        "error": None,
    }


def run_manual_veo(image_path: Path, output_dir: Path) -> dict[str, object]:
    return run_manual_provider(
        image_path,
        output_dir,
        provider_name="manual_veo",
        provider_root=DEFAULT_MANUAL_VEO_DIR,
        file_name="veo_manual.mp4",
    )

def main() -> None:
    parser = argparse.ArgumentParser(description="Run a benchmark between the current product control and image-to-video candidates.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--benchmark-id", default=DEFAULT_BENCHMARK_ID)
    parser.add_argument(
        "--providers",
        nargs="+",
        choices=["product_control", "product_control_motion", "local_ltx", "veo31", "sora2", "sora2_current_best", "manual_veo"],
        default=["product_control", "local_ltx", "veo31", "sora2", "manual_veo"],
    )
    parser.add_argument("--images", nargs="*", type=Path, default=list(DEFAULT_IMAGES))
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    comparison_rows: list[dict[str, object]] = []
    for image_path in args.images:
        label = infer_label(image_path)
        prompt = build_upper_bound_prompt(image_path)
        row: dict[str, object] = {
            "image": str(image_path),
            "label": label,
            "prompt": prompt,
            "providers": {},
        }
        if "product_control" in args.providers:
            row["providers"]["product_control"] = run_product_control(image_path, args.output_dir / "product_control" / label)
        if "product_control_motion" in args.providers:
            row["providers"]["product_control_motion"] = run_product_control_motion(image_path, args.output_dir / "product_control_motion" / label)
        if "local_ltx" in args.providers:
            row["providers"]["local_ltx"] = run_ltx(image_path, args.output_dir / "local_ltx" / label, prompt)
        if "veo31" in args.providers:
            row["providers"]["veo31"] = run_veo31(image_path, args.output_dir / "veo31", prompt)
        if "sora2" in args.providers:
            row["providers"]["sora2"] = run_sora2(image_path, args.output_dir / "sora2", prompt)
        if "sora2_current_best" in args.providers:
            row["providers"]["sora2_current_best"] = run_sora2_current_best(image_path, args.output_dir / "sora2_current_best" / label, prompt)
        if "manual_veo" in args.providers:
            row["providers"]["manual_veo"] = run_manual_veo(image_path, args.output_dir / "manual_veo" / label)
        comparison_rows.append(row)

    summary = {
        "benchmark_id": args.benchmark_id,
        "images": comparison_rows,
    }
    annotate_benchmark_summary(summary)
    summary_path = args.output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(summary_path)


if __name__ == "__main__":
    main()
