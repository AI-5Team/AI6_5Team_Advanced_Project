from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageFilter, ImageOps, ImageStat


def extract_structure_features(image_path: Path) -> dict[str, float]:
    image = Image.open(image_path).convert("L")
    resized = image.resize((180, 240), Image.Resampling.LANCZOS)
    edges = resized.filter(ImageFilter.FIND_EDGES)

    mean_edge = ImageStat.Stat(edges).mean[0] / 255.0
    top_edge = ImageStat.Stat(edges.crop((0, 0, 180, 80))).mean[0] / 255.0
    bottom_edge = ImageStat.Stat(edges.crop((0, 160, 180, 240))).mean[0] / 255.0
    center_edge = ImageStat.Stat(edges.crop((60, 0, 120, 240))).mean[0] / 255.0

    edge_floor = mean_edge + 1e-6
    return {
        "aspect_ratio": round(image.width / image.height, 4),
        "mean_edge": round(mean_edge, 4),
        "top_edge_ratio": round(top_edge / edge_floor, 4),
        "bottom_edge_ratio": round(bottom_edge / edge_floor, 4),
        "center_edge_ratio": round(center_edge / edge_floor, 4),
    }


def classify_shot_type(image_path: Path) -> str:
    features = extract_structure_features(image_path)
    if features["aspect_ratio"] >= 1.15 and features["mean_edge"] >= 0.12:
        return "tray_full_plate"
    if (
        features["aspect_ratio"] < 0.9
        and features["mean_edge"] <= 0.11
        and (
            (features["top_edge_ratio"] >= 1.18 and features["bottom_edge_ratio"] <= 0.8)
            or (features["bottom_edge_ratio"] >= 1.25 and features["center_edge_ratio"] >= 1.1)
        )
    ):
        return "glass_drink_candidate"
    return "preserve_shot"


def choose_prepare_mode(image_path: Path) -> str:
    features = extract_structure_features(image_path)
    shot_type = classify_shot_type(image_path)
    if shot_type == "tray_full_plate":
        return "cover_center"
    if shot_type == "glass_drink_candidate":
        if features["bottom_edge_ratio"] >= 1.25 and features["top_edge_ratio"] <= 0.9:
            return "cover_bottom"
        return "cover_top"
    return "cover_center"


def _prepare_cover(image: Image.Image, width: int, height: int, centering: tuple[float, float]) -> Image.Image:
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
