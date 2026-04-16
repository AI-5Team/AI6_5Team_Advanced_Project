from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from local_video_ltx_prepare_mode_classifier import choose_prepare_mode, classify_shot_type


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NEGATIVE_PROMPT = "worst quality, blurry, jittery, distorted, warped, overexposed, text, watermark"
LABEL_MAP = {
    "규카츠": "crispy gyukatsu set",
    "타코야키": "takoyaki snack tray",
    "라멘": "ramen bowl",
    "순두부짬뽕": "spicy seafood noodle soup",
    "장어덮밥": "grilled eel rice bowl",
    "커피": "iced coffee in a clear glass",
    "맥주": "beer bottle and lager glass",
}
SAMPLE_LIBRARY = {
    "규카츠": REPO_ROOT / "docs" / "sample" / "음식사진샘플(규카츠).jpg",
    "타코야키": REPO_ROOT / "docs" / "sample" / "음식사진샘플(타코야키).jpg",
    "라멘": REPO_ROOT / "docs" / "sample" / "음식사진샘플(라멘).jpg",
    "순두부짬뽕": REPO_ROOT / "docs" / "sample" / "음식사진샘플(순두부짬뽕).jpg",
    "장어덮밥": REPO_ROOT / "docs" / "sample" / "음식사진샘플(장어덮밥).jpg",
    "커피": REPO_ROOT / "docs" / "sample" / "음식사진샘플(커피).jpg",
    "맥주": REPO_ROOT / "docs" / "sample" / "음식사진샘플(맥주).jpg",
}


def infer_label(image_path: Path) -> str:
    stem = image_path.stem
    for key in LABEL_MAP:
        if key in stem:
            return key
    return stem.replace("음식사진샘플(", "").replace(")", "")


def build_upper_bound_prompt(image_path: Path) -> str:
    key = infer_label(image_path)
    label = LABEL_MAP.get(key, "restaurant food")
    shot_type = classify_shot_type(image_path)
    if shot_type == "tray_full_plate":
        return (
            f"Close-up tabletop food commercial shot of {label}, crispy texture preserved, "
            "gentle steam rising, subtle natural motion only, static close-up, very small camera push-in, "
            "warm restaurant lighting, realistic appetizing food motion, no object morphing, no extra ingredients."
        )
    if shot_type == "glass_drink_candidate":
        return (
            f"Close-up beverage commercial shot of {label}, product shape preserved, realistic liquid and glass details, "
            "subtle condensation shimmer, static tabletop composition, minimal camera drift, bright tabletop lighting, "
            "natural commercial motion, no object morphing, no duplicated glass or bottle."
        )
    return (
        f"Close-up food commercial shot of {label}, product shape preserved, realistic texture, "
        "soft natural steam only, static close-up, minimal camera movement, warm restaurant lighting, "
        "natural appetizing motion, no object morphing, no extra ingredients."
    )


def resolve_prepare_mode(image_path: Path, prepare_mode: str) -> str:
    return choose_prepare_mode(image_path) if prepare_mode == "auto" else prepare_mode


def _prepare_cover(image: Image.Image, width: int, height: int, centering: tuple[float, float] = (0.5, 0.5)) -> Image.Image:
    return ImageOps.fit(image, (width, height), method=Image.Resampling.LANCZOS, centering=centering)


def _prepare_contain_blur(image: Image.Image, width: int, height: int) -> Image.Image:
    contained = ImageOps.contain(image, (width, height), method=Image.Resampling.LANCZOS)
    background = image.resize((width, height), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=24))
    offset = ((width - contained.width) // 2, (height - contained.height) // 2)
    background.paste(contained, offset)
    return background


def prepare_image(image_path: Path, width: int, height: int, prepare_mode: str) -> Image.Image:
    image = Image.open(image_path).convert("RGB")
    if prepare_mode == "cover_center":
        return _prepare_cover(image, width, height, centering=(0.5, 0.5))
    if prepare_mode == "cover_top":
        return _prepare_cover(image, width, height, centering=(0.5, 0.35))
    if prepare_mode == "cover_bottom":
        return _prepare_cover(image, width, height, centering=(0.5, 0.7))
    if prepare_mode == "contain_blur":
        return _prepare_contain_blur(image, width, height)
    raise ValueError(f"unsupported prepare mode: {prepare_mode}")


def image_metrics(input_path: Path, compare_path: Path) -> dict[str, float]:
    source = np.asarray(Image.open(input_path).convert("RGB"), dtype=np.float32)
    target = np.asarray(Image.open(compare_path).convert("RGB"), dtype=np.float32)
    source_gray = np.asarray(Image.open(input_path).convert("L"), dtype=np.float32)
    target_gray = np.asarray(Image.open(compare_path).convert("L"), dtype=np.float32)
    edges = np.asarray(Image.open(compare_path).convert("L").filter(ImageFilter.FIND_EDGES), dtype=np.float32)
    return {
        "mse": round(float(np.mean((source - target) ** 2)), 2),
        "gray_mse": round(float(np.mean((source_gray - target_gray) ** 2)), 2),
        "edge_variance": round(float(np.var(edges)), 2),
    }


def extract_video_frames(video_path: Path, output_dir: Path, midpoint_seconds: float) -> tuple[Path, Path]:
    first_frame_path = output_dir / "first_frame.png"
    mid_frame_path = output_dir / "mid_frame.png"
    first_command = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-i",
        str(video_path),
        "-vf",
        "select=eq(n\\,0)",
        "-vframes",
        "1",
        str(first_frame_path),
    ]
    mid_command = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-ss",
        f"{midpoint_seconds:.2f}",
        "-i",
        str(video_path),
        "-vframes",
        "1",
        str(mid_frame_path),
    ]
    subprocess.run(first_command, cwd=REPO_ROOT, check=True, capture_output=True, text=True, encoding="utf-8")
    subprocess.run(mid_command, cwd=REPO_ROOT, check=True, capture_output=True, text=True, encoding="utf-8")
    return first_frame_path, mid_frame_path


def create_contact_sheet(video_path: Path, output_path: Path, *, fps: int = 2, columns: int = 4) -> Path:
    command = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-i",
        str(video_path),
        "-vf",
        f"fps={fps},scale=320:-1,tile={columns}x1",
        "-frames:v",
        "1",
        str(output_path),
    ]
    subprocess.run(command, cwd=REPO_ROOT, check=True, capture_output=True, text=True, encoding="utf-8")
    return output_path


def video_motion_metrics(video_path: Path, *, sample_fps: int = 4, max_frames: int = 16) -> dict[str, float]:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        frame_pattern = temp_root / "frame_%03d.png"
        command = [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(video_path),
            "-vf",
            f"fps={sample_fps},scale=320:-1",
            "-frames:v",
            str(max_frames),
            str(frame_pattern),
        ]
        subprocess.run(command, cwd=REPO_ROOT, check=True, capture_output=True, text=True, encoding="utf-8")
        frames = sorted(temp_root.glob("frame_*.png"))
        if len(frames) < 2:
            return {
                "sample_fps": float(sample_fps),
                "sampled_frames": float(len(frames)),
                "avg_rgb_diff": 0.0,
                "max_rgb_diff": 0.0,
                "avg_gray_diff": 0.0,
            }

        rgb_diffs: list[float] = []
        gray_diffs: list[float] = []
        previous_rgb = np.asarray(Image.open(frames[0]).convert("RGB"), dtype=np.float32)
        previous_gray = np.asarray(Image.open(frames[0]).convert("L"), dtype=np.float32)
        for frame_path in frames[1:]:
            current_rgb = np.asarray(Image.open(frame_path).convert("RGB"), dtype=np.float32)
            current_gray = np.asarray(Image.open(frame_path).convert("L"), dtype=np.float32)
            rgb_diffs.append(float(np.mean(np.abs(current_rgb - previous_rgb))))
            gray_diffs.append(float(np.mean(np.abs(current_gray - previous_gray))))
            previous_rgb = current_rgb
            previous_gray = current_gray

        return {
            "sample_fps": float(sample_fps),
            "sampled_frames": float(len(frames)),
            "avg_rgb_diff": round(float(np.mean(rgb_diffs)), 2),
            "max_rgb_diff": round(float(np.max(rgb_diffs)), 2),
            "avg_gray_diff": round(float(np.mean(gray_diffs)), 2),
        }


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
