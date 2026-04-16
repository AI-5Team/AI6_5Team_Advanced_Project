from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from services.worker.utils.runtime import public_storage_path


def _badge_text(purpose: str, scene_role: str, slot: str) -> str:
    if scene_role == "closing":
        return "CTA"
    if purpose == "promotion" and scene_role == "opening":
        return "TODAY DEAL"
    if purpose == "review":
        return "REAL REVIEW"
    return slot.replace("_", " ").upper()


def _stamp_text(purpose: str, scene_role: str, scene: Mapping[str, object]) -> str:
    slot = str(scene["slot"])
    if scene_role == "closing":
        return "POST READY"
    if purpose == "promotion" and slot == "benefit":
        return "BENEFIT"
    if purpose == "promotion" and slot == "period":
        return "LIMITED"
    if purpose == "review" and scene_role == "review":
        return "REVIEW CUT"
    return slot.replace("_", " ").upper()


def _scene_role(purpose: str, scene: Mapping[str, object], index: int, last_index: int) -> str:
    text_role = str(scene["textRole"])
    slot = str(scene["slot"])
    if index == last_index or text_role == "cta" or slot == "cta":
        return "closing"
    if purpose == "review" and text_role in {"review_quote", "product_name"}:
        return "review"
    if index == 0 or text_role in {"hook", "region_hook"}:
        return "opening"
    return "support"


def _layout_hint(purpose: str, scene_role: str) -> str:
    if scene_role == "closing":
        return "cta_poster"
    if purpose == "review" or scene_role == "review":
        return "review_poster"
    if scene_role == "opening":
        return "offer_poster"
    return "support_panel"


def _kicker_text(template_title: str, purpose: str, slot: str, secondary_text: str, scene_role: str) -> str:
    if scene_role == "closing":
        return "확인 후 바로 게시로 이어지는 마지막 장면"
    if purpose == "promotion" and slot == "benefit":
        return "혜택과 기간감이 먼저 읽히는 프로모션 구성"
    if purpose == "review":
        return "리뷰형 장면은 다시 찾는 이유를 먼저 남깁니다"
    if secondary_text:
        return secondary_text
    return f"{template_title} 장면"


def build_scene_plan(
    project: Mapping[str, object],
    template: dict,
    style: dict,
    copy_bundle: dict,
    processed_assets: list[dict[str, Path]],
    storage_root: Path,
) -> dict:
    hero_asset = processed_assets[0]["vertical"]
    detail_assets = [item["vertical"] for item in processed_assets] or [hero_asset]
    palette = style.get("palette", {})
    typography = style.get("typography", {})
    scenes: list[dict] = []

    template_scenes = template.get("scenes", [])
    last_index = len(template_scenes) - 1
    purpose = str(project["purpose"])
    template_title = str(template.get("title", template.get("templateId", "scene")))

    for index, scene in enumerate(template_scenes):
        text_role = str(scene["textRole"])
        slot = str(scene["slot"])
        primary_text = copy_bundle["sceneText"].get(text_role, copy_bundle["hookText"])
        secondary_text = copy_bundle["subText"].get(text_role, copy_bundle["captions"][0])
        asset_path = detail_assets[index % len(detail_assets)] if scene["mediaRole"] == "detail" else hero_asset
        scene_role = _scene_role(purpose, scene, index, last_index)
        layout_hint = _layout_hint(purpose, scene_role)
        badge_text = _badge_text(purpose, scene_role, slot)
        stamp_text = _stamp_text(purpose, scene_role, scene)

        scenes.append(
            {
                "sceneId": scene["sceneId"],
                "slot": slot,
                "textRole": text_role,
                "mediaRole": scene["mediaRole"],
                "sceneRole": scene_role,
                "durationSec": float(scene["durationSec"]),
                "asset": {
                    "storagePath": public_storage_path(asset_path, storage_root),
                    "derivativeType": "vertical",
                },
                "copy": {
                    "primaryText": primary_text,
                    "secondaryText": secondary_text,
                    "headline": primary_text,
                    "body": secondary_text,
                    "kicker": _kicker_text(template_title, purpose, slot, secondary_text, scene_role),
                    "cta": copy_bundle["ctaText"],
                    "badgeText": badge_text,
                    "stampText": stamp_text,
                },
                "renderHints": {
                    "layoutHint": layout_hint,
                    "effects": list(scene.get("effects", [])),
                    "motionPreset": style.get("motionPreset"),
                    "captionLength": style.get("captionLength"),
                    "safeArea": template.get("safeArea", {}),
                    "palette": {
                        "background": palette.get("background"),
                        "surface": palette.get("surface"),
                        "accent": palette.get("accent"),
                        "textPrimary": palette.get("textPrimary"),
                        "textOnSurface": palette.get("textOnSurface"),
                    },
                    "typography": {
                        "headlineSize": typography.get("headlineSize"),
                        "bodySize": typography.get("bodySize"),
                        "ctaSize": typography.get("ctaSize"),
                        "fontFamily": typography.get("fontFamily"),
                    },
                },
            }
        )

    return {
        "sceneSpecVersion": template.get("sceneSpecVersion", "v1"),
        "templateId": template["templateId"],
        "templateTitle": template_title,
        "purpose": purpose,
        "styleId": style["styleId"],
        "businessType": project["business_type"],
        "regionName": project["region_name"],
        "durationSec": float(template["durationSec"]),
        "sceneCount": len(scenes),
        "scenes": scenes,
    }
