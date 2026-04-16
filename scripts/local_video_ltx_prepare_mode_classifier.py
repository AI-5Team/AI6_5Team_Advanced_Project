from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


def extract_structure_features(image_path: Path) -> dict[str, float]:
    image = Image.open(image_path).convert("L")
    resized = image.resize((180, 240), Image.Resampling.LANCZOS)
    edges = np.asarray(resized.filter(ImageFilter.FIND_EDGES), dtype=np.float32) / 255.0

    mean_edge = float(edges.mean())
    top_edge = float(edges[:80].mean())
    bottom_edge = float(edges[160:].mean())
    center_edge = float(edges[:, 60:120].mean())

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
        # Bottle+glass shots often carry key detail lower in frame, unlike top-heavy cup shots.
        if features["bottom_edge_ratio"] >= 1.25 and features["top_edge_ratio"] <= 0.9:
            return "cover_bottom"
        return "cover_top"
    return "contain_blur"
