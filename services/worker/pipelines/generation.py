from __future__ import annotations

import base64
import json
import os
import shutil
import sqlite3
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from uuid import uuid4

from services.worker.adapters.template_loader import load_copy_rule, load_style, load_template
from services.worker.planning.scene_plan import build_scene_plan
from services.worker.renderers.framing import choose_prepare_mode, classify_shot_type, prepare_image
from services.worker.renderers.media import (
    CANVAS_SIZE,
    create_post_image,
    create_scene_image,
    create_scene_overlay_image,
    preprocess_asset,
    render_hybrid_video,
    render_video,
)
from services.worker.utils.runtime import WorkerRuntime, connect, dumps, ensure_dir, parse_json, public_storage_path, resolve_storage_path, storage_url, utc_now


def run_generation_job(db_path: Path, storage_root: Path, template_spec_root: Path, project_id: str, generation_run_id: str) -> None:
    runtime = WorkerRuntime(db_path=db_path, storage_root=storage_root, template_spec_root=template_spec_root)
    with connect(runtime.db_path) as conn:
        try:
            _execute_generation(conn, runtime, project_id, generation_run_id)
            conn.commit()
        except Exception as exc:
            _mark_generation_failed(conn, project_id, generation_run_id, "RENDER_FAILED", str(exc))
            conn.commit()
            raise


def _resolve_bgrade_scene_policy(source_path: Path, scene: dict) -> dict[str, str]:
    shot_type = classify_shot_type(source_path)
    base_prepare_mode = choose_prepare_mode(source_path)
    slot = str(scene.get("slot") or "")
    media_role = str(scene.get("mediaRole") or "")

    if shot_type == "glass_drink_candidate":
        anchor_motion = "push_in_bottom" if base_prepare_mode == "cover_bottom" else "push_in_top"
        if slot == "period":
            return {"shotType": shot_type, "prepareMode": "cover_center", "motionPreset": "push_in_center"}
        return {"shotType": shot_type, "prepareMode": base_prepare_mode, "motionPreset": anchor_motion}

    if shot_type == "tray_full_plate":
        if slot == "period":
            return {"shotType": shot_type, "prepareMode": "cover_top", "motionPreset": "push_in_top"}
        return {"shotType": shot_type, "prepareMode": "cover_center", "motionPreset": "push_in_center"}

    if shot_type == "preserve_shot":
        if slot == "period":
            return {"shotType": shot_type, "prepareMode": "cover_top", "motionPreset": "push_in_top"}
        if media_role == "detail":
            return {"shotType": shot_type, "prepareMode": "cover_center", "motionPreset": "push_in_top"}
        return {"shotType": shot_type, "prepareMode": "cover_center", "motionPreset": "push_in_center"}

    if media_role == "detail":
        return {"shotType": shot_type, "prepareMode": base_prepare_mode, "motionPreset": "push_in_top"}
    return {"shotType": shot_type, "prepareMode": base_prepare_mode, "motionPreset": "push_in_center"}


def _execute_generation(conn: sqlite3.Connection, runtime: WorkerRuntime, project_id: str, generation_run_id: str) -> None:
    project = conn.execute("SELECT * FROM content_projects WHERE id = ?", (project_id,)).fetchone()
    run = conn.execute("SELECT * FROM generation_runs WHERE id = ?", (generation_run_id,)).fetchone()
    if project is None or run is None:
        raise ValueError("project or generation run not found")

    input_snapshot = parse_json(run["input_snapshot_json"])
    quick_options = parse_json(run["quick_options_snapshot_json"])
    asset_ids = input_snapshot.get("assetIds", [])
    template_id = run["template_id"]

    template = load_template(runtime.template_spec_root, template_id)
    style_id = input_snapshot.get("styleOverride") or project["style"]
    style = load_style(runtime.template_spec_root, style_id)
    copy_rule = load_copy_rule(runtime.template_spec_root, project["purpose"])

    project_root = runtime.storage_root / "projects" / project_id.lstrip("/")
    processed_dir = project_root / "processed"
    run_dir = project_root / "runs" / generation_run_id
    scene_dir = run_dir / "scenes"
    ensure_dir(processed_dir)
    ensure_dir(run_dir)
    ensure_dir(scene_dir)

    conn.execute(
        "UPDATE generation_runs SET status = ?, started_at = ?, error_code = NULL WHERE id = ?",
        ("processing", utc_now(), generation_run_id),
    )
    _set_step(conn, generation_run_id, "preprocessing", "processing")
    conn.execute(
        "UPDATE content_projects SET current_status = ?, latest_generation_run_id = ?, updated_at = ? WHERE id = ?",
        ("preprocessing", generation_run_id, utc_now(), project_id),
    )

    processed_assets = _preprocess_assets(conn, runtime, processed_dir, asset_ids)
    hybrid_source_video_path = _resolve_hybrid_source_video_path(runtime.storage_root, input_snapshot)
    hybrid_source_selection = _resolve_hybrid_source_selection(input_snapshot)

    _complete_step(conn, generation_run_id, "preprocessing")
    _set_step(conn, generation_run_id, "copy_generation", "processing")
    conn.execute(
        "UPDATE content_projects SET current_status = ?, updated_at = ? WHERE id = ?",
        ("generating", utc_now(), project_id),
    )

    copy_bundle = _build_copy_bundle(project, template, copy_rule, style_id, quick_options, input_snapshot, processed_assets)
    copy_set_id = str(uuid4())
    conn.execute(
        """
        INSERT INTO copy_sets (id, generation_run_id, hook_text, caption_options_json, hashtags_json, cta_text, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            copy_set_id,
            generation_run_id,
            copy_bundle["hookText"],
            dumps(copy_bundle["captions"]),
            dumps(copy_bundle["hashtags"]),
            copy_bundle["ctaText"],
            utc_now(),
        ),
    )
    _complete_step(conn, generation_run_id, "copy_generation")

    _set_step(conn, generation_run_id, "video_rendering", "processing")
    scene_plan = build_scene_plan(project, template, style, copy_bundle, processed_assets, runtime.storage_root)
    scene_plan_path = run_dir / "scene-plan.json"
    scene_plan_path.write_text(json.dumps(scene_plan, ensure_ascii=False, indent=2), encoding="utf-8")

    video_scene_specs = []
    hybrid_overlay_specs: list[tuple[Path, float, float]] = []
    scene_render_policies: list[dict[str, str | int]] = []
    scene_motion_presets: list[str] = []
    hero_asset = processed_assets[0]
    detail_assets = processed_assets or [hero_asset]
    current_start_sec = 0.0
    for index, scene in enumerate(template["scenes"], start=1):
        scene_path = scene_dir / f"{scene['sceneId']}.png"
        text_role = scene["textRole"]
        primary_text = copy_bundle["sceneText"].get(text_role, copy_bundle["hookText"])
        secondary_text = copy_bundle["subText"].get(text_role, copy_bundle["captions"][0])
        asset_item = detail_assets[(index - 1) % len(detail_assets)] if scene["mediaRole"] == "detail" else hero_asset
        if style_id == "b_grade_fun":
            scene_policy = _resolve_bgrade_scene_policy(asset_item["source"], scene)
            base_image_path = scene_dir / f"{scene['sceneId']}_base.png"
            prepared_image = prepare_image(
                asset_item["source"],
                CANVAS_SIZE[0],
                CANVAS_SIZE[1],
                str(scene_policy["prepareMode"]),
            )
            prepared_image.save(base_image_path)
            if hybrid_source_video_path is None:
                scene_motion_presets.append(str(scene_policy["motionPreset"]))
            scene_render_policies.append(
                {
                    "sceneId": str(scene["sceneId"]),
                    "assetIndex": (index - 1) % len(detail_assets) if scene["mediaRole"] == "detail" else 0,
                    "shotType": str(scene_policy["shotType"]),
                    "prepareMode": str(scene_policy["prepareMode"]),
                    "motionPreset": str(scene_policy["motionPreset"]),
                }
            )
        else:
            base_image_path = asset_item["vertical"]
        badge = scene["slot"].replace("_", " ").upper()
        create_scene_image(scene_path, base_image_path, primary_text, secondary_text, style_id, badge_text=badge[:10])
        if hybrid_source_video_path is not None:
            overlay_path = scene_dir / f"{scene['sceneId']}_overlay.png"
            create_scene_overlay_image(overlay_path, primary_text, secondary_text, style_id, badge_text=badge[:10])
            duration_sec = float(scene["durationSec"])
            hybrid_overlay_specs.append((overlay_path, current_start_sec, current_start_sec + duration_sec))
            current_start_sec += duration_sec
        video_scene_specs.append((scene_path, float(scene["durationSec"])))

    video_path = run_dir / "video.mp4"
    thumb_path = run_dir / "thumb.png"
    motion_presets = scene_motion_presets or None
    if hybrid_source_video_path is not None:
        render_hybrid_video(hybrid_source_video_path, hybrid_overlay_specs, video_path)
    else:
        render_video(video_scene_specs, video_path, motion_presets=motion_presets)
    shutil.copy(video_scene_specs[0][0], thumb_path)
    _complete_step(conn, generation_run_id, "video_rendering")

    _set_step(conn, generation_run_id, "post_rendering", "processing")
    post_path = run_dir / "post.png"
    create_post_image(
        post_path,
        processed_assets[0]["square"],
        copy_bundle["hookText"],
        copy_bundle["captions"][0],
        copy_bundle["ctaText"],
        style_id,
    )
    _complete_step(conn, generation_run_id, "post_rendering")

    _set_step(conn, generation_run_id, "packaging", "processing")
    copy_policy_state = _build_active_copy_policy_state(project, copy_rule, quick_options, input_snapshot)
    copy_deck = _build_copy_deck(runtime.template_spec_root, template_id, copy_bundle)
    scene_layer_summary = _build_scene_layer_summary(runtime.template_spec_root, template_id)
    change_impact_summary = _build_change_impact_summary(str(run["run_type"]), quick_options)
    prompt_baseline_summary = _build_prompt_baseline_summary(
        runtime.template_spec_root,
        purpose=str(project["purpose"]),
        template_id=template_id,
        style_id=style_id,
        quick_options=quick_options,
        input_snapshot=input_snapshot,
    )
    hybrid_source_public_path = _path_for_render_meta(hybrid_source_video_path, runtime.storage_root) if hybrid_source_video_path else None
    render_meta = {
        "projectId": project_id,
        "generationRunId": generation_run_id,
        "templateId": template_id,
        "style": style_id,
        "purpose": project["purpose"],
        "usedAssetIds": asset_ids,
        "durationSec": template["durationSec"],
        "scenePlanPath": public_storage_path(scene_plan_path, runtime.storage_root),
        "sceneSpecVersion": scene_plan["sceneSpecVersion"],
        "sceneCount": scene_plan["sceneCount"],
        "sceneLayerSummary": scene_layer_summary,
        "changeImpactSummary": change_impact_summary,
        "copyPolicy": copy_policy_state,
        "copyDeck": copy_deck,
        "copyGeneration": copy_bundle.get("copyGeneration"),
        "promptBaselineSummary": prompt_baseline_summary,
        "rendererFramingMode": "hybrid_source_video" if hybrid_source_video_path else ("shot_aware_prepare_mode" if motion_presets else "preprocessed_vertical"),
        "rendererVideoSourceMode": "hybrid_generated_clip" if hybrid_source_video_path else "scene_image_render",
        "rendererMotionMode": "hybrid_overlay_packaging" if hybrid_source_video_path else ("zoompan_control" if motion_presets else "static_concat"),
        "rendererMotionPresets": [] if hybrid_source_video_path else (motion_presets or []),
        "rendererScenePolicies": scene_render_policies,
        "rendererHybridSourceVideo": hybrid_source_public_path,
        "rendererHybridSourceSelection": hybrid_source_selection,
        "rendererHybridDurationStrategy": "freeze_last_frame" if hybrid_source_video_path else None,
        "rendererHybridTargetDurationSec": round(hybrid_overlay_specs[-1][2], 2) if hybrid_overlay_specs else None,
        "rendererHybridOverlayTimeline": [
            {
                "sceneId": str(template["scenes"][index]["sceneId"]),
                "startSec": round(start_sec, 2),
                "endSec": round(end_sec, 2),
                "overlayPath": _path_for_render_meta(overlay_path, runtime.storage_root),
            }
            for index, (overlay_path, start_sec, end_sec) in enumerate(hybrid_overlay_specs)
        ],
        "createdAt": utc_now(),
    }
    (run_dir / "render-meta.json").write_text(json.dumps(render_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (run_dir / "caption_options.json").write_text(json.dumps(copy_bundle["captions"], ensure_ascii=False, indent=2), encoding="utf-8")
    (run_dir / "hashtags.json").write_text(json.dumps(copy_bundle["hashtags"], ensure_ascii=False, indent=2), encoding="utf-8")

    variant_id = str(uuid4())
    conn.execute(
        "UPDATE generated_variants SET is_selected = 0 WHERE generation_run_id IN (SELECT id FROM generation_runs WHERE project_id = ?)",
        (project_id,),
    )
    conn.execute(
        """
        INSERT INTO generated_variants (
            id, generation_run_id, copy_set_id, video_path, post_image_path, preview_thumbnail_path,
            duration_sec, render_meta_json, is_selected, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        """,
        (
            variant_id,
            generation_run_id,
            copy_set_id,
            public_storage_path(video_path, runtime.storage_root),
            public_storage_path(post_path, runtime.storage_root),
            public_storage_path(thumb_path, runtime.storage_root),
            float(template["durationSec"]),
            dumps(render_meta),
            utc_now(),
        ),
    )
    _complete_step(conn, generation_run_id, "packaging")
    conn.execute(
        "UPDATE generation_runs SET status = ?, finished_at = ?, error_code = NULL WHERE id = ?",
        ("completed", utc_now(), generation_run_id),
    )
    conn.execute(
        "UPDATE content_projects SET current_status = ?, latest_generation_run_id = ?, updated_at = ? WHERE id = ?",
        ("generated", generation_run_id, utc_now(), project_id),
    )


def _preprocess_assets(conn: sqlite3.Connection, runtime: WorkerRuntime, processed_dir: Path, asset_ids: list[str]) -> list[dict[str, Path]]:
    results: list[dict[str, Path]] = []
    for asset_id in asset_ids:
        asset = conn.execute("SELECT * FROM project_assets WHERE id = ?", (asset_id,)).fetchone()
        if asset is None:
            continue
        source_path = resolve_storage_path(runtime.storage_root, asset["storage_path"])
        derivatives = preprocess_asset(source_path, processed_dir, asset_id)
        for derivative_type, abs_path in derivatives.items():
            conn.execute(
                """
                INSERT INTO asset_derivatives (id, asset_id, derivative_type, storage_path, width, height, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(asset_id, derivative_type) DO UPDATE SET
                    storage_path = excluded.storage_path,
                    width = excluded.width,
                    height = excluded.height,
                    created_at = excluded.created_at
                """,
                (
                    str(uuid4()),
                    asset_id,
                    derivative_type,
                    public_storage_path(abs_path, runtime.storage_root),
                    720 if derivative_type == "vertical" else 1080,
                    1280 if derivative_type == "vertical" else 1080,
                    utc_now(),
                ),
            )
        results.append({"source": source_path, **derivatives})
    if not results:
        raise ValueError("no valid assets for preprocessing")
    return results


def _resolve_hybrid_source_video_path(storage_root: Path, input_snapshot: dict) -> Path | None:
    hybrid_source_video = input_snapshot.get("hybridSourceVideoPath")
    if not isinstance(hybrid_source_video, str) or not hybrid_source_video:
        return None
    resolved = resolve_storage_path(storage_root, hybrid_source_video) if hybrid_source_video.startswith("/") else Path(hybrid_source_video)
    if not resolved.exists():
        raise ValueError(f"hybrid source video not found: {hybrid_source_video}")
    return resolved


def _resolve_hybrid_source_selection(input_snapshot: dict) -> dict | None:
    selection = input_snapshot.get("hybridSourceSelection")
    return selection if isinstance(selection, dict) else None


def _path_for_render_meta(path: Path | None, storage_root: Path) -> str | None:
    if path is None:
        return None
    try:
        return public_storage_path(path, storage_root)
    except ValueError:
        return str(path)


def _build_copy_bundle(
    project: sqlite3.Row,
    template: dict,
    copy_rule: dict,
    style_id: str,
    quick_options: dict,
    input_snapshot: dict,
    processed_assets: list[dict[str, Path]],
) -> dict:
    deterministic_bundle = _build_deterministic_copy_bundle(project, template, copy_rule, style_id, quick_options, input_snapshot)
    provider = str(os.environ.get("WORKER_COPY_PROVIDER", "deterministic")).strip().lower()
    if provider not in {"openai", "auto"}:
        deterministic_bundle["copyGeneration"] = {
            "sourceMode": "deterministic_rule",
            "provider": "local_rule",
            "model": None,
            "fallbackReason": None,
        }
        return deterministic_bundle

    api_key = os.environ.get("OPENAI_API_KEY")
    model_name = str(os.environ.get("WORKER_COPY_OPENAI_MODEL", "gpt-5-mini")).strip() or "gpt-5-mini"
    if not api_key:
        deterministic_bundle["copyGeneration"] = {
            "sourceMode": "deterministic_fallback",
            "provider": "openai",
            "model": model_name,
            "fallbackReason": "openai_api_key_missing",
        }
        return deterministic_bundle

    try:
        llm_bundle = _request_openai_copy_bundle(
            api_key=api_key,
            model_name=model_name,
            prompt_package=_build_openai_copy_prompt(project, template, copy_rule, style_id, quick_options, input_snapshot, deterministic_bundle),
            asset_paths=tuple(item["source"] for item in processed_assets[:2] if isinstance(item.get("source"), Path)),
            timeout_sec=max(5, int(os.environ.get("WORKER_COPY_TIMEOUT_SEC", "45"))),
        )
        merged_bundle = _merge_llm_copy_bundle(project, deterministic_bundle, llm_bundle)
        merged_bundle["copyGeneration"] = {
            "sourceMode": "openai_live",
            "provider": "openai",
            "model": model_name,
            "fallbackReason": None,
        }
        return merged_bundle
    except Exception as exc:
        deterministic_bundle["copyGeneration"] = {
            "sourceMode": "deterministic_fallback",
            "provider": "openai",
            "model": model_name,
            "fallbackReason": _sanitize_copy_generation_error(exc),
        }
        return deterministic_bundle


def _build_deterministic_copy_bundle(project: sqlite3.Row, template: dict, copy_rule: dict, style_id: str, quick_options: dict, input_snapshot: dict) -> dict:
    region = project["region_name"]
    business = "카페" if project["business_type"] == "cafe" else "음식점"
    shorten = bool(quick_options.get("shorterCopy") or input_snapshot.get("shorterCopy"))
    emphasize_region = bool(quick_options.get("emphasizeRegion") or input_snapshot.get("emphasizeRegion"))
    highlight_price = bool(quick_options.get("highlightPrice") or input_snapshot.get("highlightPrice"))
    region_prefix = f"{region}에서" if emphasize_region else f"{region} 기준"

    hook = copy_rule["sampleHooks"][0]
    if project["purpose"] == "new_menu":
        hook = f"{region_prefix} 먼저 만나는 신메뉴"
    elif project["purpose"] == "promotion":
        hook = f"{region_prefix} 오늘 바로 쓰기 좋은 혜택"
    elif project["purpose"] == "review":
        hook = f"{region_prefix} 다시 찾게 되는 한 줄 후기"
    elif project["purpose"] == "location_push":
        hook = f"{region_prefix} 가볍게 들르기 좋은 {business}"

    hook = hook if shorten else f"{hook}로 분위기를 한 번에 보여드립니다"
    product_line = f"{region} {business} 대표 메뉴를 짧고 선명하게 소개합니다"
    difference_line = "가격 포인트가 먼저 보이도록 구성했습니다" if highlight_price else "메뉴, 분위기, CTA를 한 흐름으로 정리했습니다"
    cta = "지금 바로 들러보세요" if style_id == "b_grade_fun" else "오늘 바로 방문해 보세요"

    captions = [
        hook[:78],
        f"{region} {business} 홍보에 맞춘 {template['title']} 결과물입니다."[:78],
        ("가격과 혜택이 잘 보이게 구성했습니다." if highlight_price else "짧게 봐도 이해되는 구조로 정리했습니다.")[:78],
    ]
    hashtags = [
        f"#{region.replace(' ', '')}",
        "#카페홍보" if project["business_type"] == "cafe" else "#음식점홍보",
        "#오늘만할인" if project["purpose"] == "promotion" else "#신메뉴홍보",
        "#지역마케팅",
        "#숏폼광고",
    ]

    scene_text = {
        "hook": hook,
        "product_name": product_line,
        "difference": difference_line,
        "benefit": difference_line,
        "urgency": "이번 주 안에 더 주목받을 수 있게 구성했습니다",
        "cta": cta,
        "region_hook": hook,
        "visit_reason": f"{region}에서 찾기 쉬운 이유를 짧게 담았습니다",
        "review_quote": f"\"{region}에서 다시 찾고 싶은 한 곳\"",
    }
    sub_text = {
        "hook": captions[0],
        "product_name": captions[1],
        "difference": captions[2],
        "benefit": captions[2],
        "urgency": captions[2],
        "cta": cta,
        "region_hook": captions[0],
        "visit_reason": captions[1],
        "review_quote": captions[1],
    }

    return {
        "hookText": hook[:38],
        "captions": captions,
        "hashtags": hashtags,
        "ctaText": cta,
        "sceneText": scene_text,
        "subText": sub_text,
    }


def _build_openai_copy_prompt(
    project: sqlite3.Row,
    template: dict,
    copy_rule: dict,
    style_id: str,
    quick_options: dict,
    input_snapshot: dict,
    deterministic_bundle: dict,
) -> dict[str, str]:
    quick_option_state = _normalize_quick_option_state(quick_options, input_snapshot)
    detail_location = str(project["detail_location"] or "").strip()
    scene_roles = []
    for scene in template.get("scenes", []):
        role = str(scene.get("textRole") or "").strip()
        if role and role not in scene_roles:
            scene_roles.append(role)

    system_instruction = (
        "당신은 한국어 숏폼 광고 카피를 만드는 실무 카피라이터입니다. "
        "반드시 JSON 객체만 반환하고, 입력에 없는 가격 숫자, 할인, 상세 위치, 과장된 사실을 만들지 마세요. "
        "결과물은 template/hybrid 영상 패키징과 upload assist에 바로 연결되는 짧고 선명한 카피여야 합니다."
    )
    user_prompt = (
        "다음 컨텍스트에 맞춰 광고 카피 JSON을 생성하세요.\n"
        f"- 업종: {project['business_type']}\n"
        f"- 목적: {project['purpose']}\n"
        f"- 스타일: {style_id}\n"
        f"- 지역명: {project['region_name']}\n"
        f"- 상세 위치: {detail_location or '없음'}\n"
        f"- 템플릿 제목: {template.get('title', '')}\n"
        f"- 템플릿 scene textRole: {', '.join(scene_roles) if scene_roles else 'hook, product_name, difference, cta'}\n"
        f"- quick options: {json.dumps(quick_option_state, ensure_ascii=False)}\n"
        f"- sample hooks: {json.dumps(copy_rule.get('sampleHooks', [])[:3], ensure_ascii=False)}\n"
        f"- deterministic baseline: {json.dumps(deterministic_bundle, ensure_ascii=False)}\n"
        "출력 제약:\n"
        "- hookText는 38자 이하\n"
        "- captions는 정확히 3개, 각 78자 이하\n"
        "- hashtags는 정확히 5개, 모두 #으로 시작\n"
        "- ctaText는 18자 이하\n"
        "- sceneText와 subText는 baseline에 있는 모든 key를 유지\n"
        "- detail_location이 있더라도 상세 위치 문자열은 출력에 직접 쓰지 말 것\n"
        "- emphasizeRegion=true여도 지역명 반복은 최소화할 것\n"
        "- highlightPrice=true라도 입력에 없는 숫자/할인 문구는 만들지 말 것\n"
        "- style이 b_grade_fun이면 말맛은 살리되 저속하거나 과장된 표현은 금지\n"
        "반드시 아래 스키마와 동일한 JSON 객체만 반환하세요:\n"
        "{"
        "\"hookText\":\"...\","
        "\"captions\":[\"...\",\"...\",\"...\"],"
        "\"hashtags\":[\"#...\",\"#...\",\"#...\",\"#...\",\"#...\"],"
        "\"ctaText\":\"...\","
        "\"sceneText\":{\"hook\":\"...\",\"product_name\":\"...\",\"difference\":\"...\",\"benefit\":\"...\",\"urgency\":\"...\",\"cta\":\"...\",\"region_hook\":\"...\",\"visit_reason\":\"...\",\"review_quote\":\"...\"},"
        "\"subText\":{\"hook\":\"...\",\"product_name\":\"...\",\"difference\":\"...\",\"benefit\":\"...\",\"urgency\":\"...\",\"cta\":\"...\",\"region_hook\":\"...\",\"visit_reason\":\"...\",\"review_quote\":\"...\"}"
        "}"
    )
    return {"system_instruction": system_instruction, "user_prompt": user_prompt}


def _request_openai_copy_bundle(
    *,
    api_key: str,
    model_name: str,
    prompt_package: dict[str, str],
    asset_paths: tuple[Path, ...],
    timeout_sec: int,
) -> dict[str, Any]:
    content: list[dict[str, Any]] = [{"type": "input_text", "text": prompt_package["user_prompt"]}]
    for path in asset_paths:
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        content.append({"type": "input_image", "image_url": f"data:image/png;base64,{encoded}"})

    body: dict[str, Any] = {
        "model": model_name,
        "instructions": prompt_package["system_instruction"],
        "input": [{"role": "user", "content": content}],
        "max_output_tokens": 900,
        "text": {
            "format": {"type": "json_object"},
            "verbosity": "low" if model_name.startswith("gpt-5") else "medium",
        },
    }
    if model_name.startswith("gpt-5"):
        body["reasoning"] = {"effort": "minimal"}

    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_sec) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"openai_request_failed:{exc.code}:{detail}") from exc

    text = _extract_openai_response_text(payload)
    if not text:
        raise RuntimeError("openai_empty_text")
    return _parse_json_object(text)


def _merge_llm_copy_bundle(project: sqlite3.Row, fallback_bundle: dict, llm_bundle: dict[str, Any]) -> dict:
    detail_location = str(project["detail_location"] or "").strip()
    hook_text = _choose_copy_text(llm_bundle.get("hookText"), fallback_bundle["hookText"], 38, detail_location)
    captions = _normalize_copy_list(llm_bundle.get("captions"), fallback_bundle["captions"], 3, 78, detail_location)
    hashtags = _normalize_hashtag_list(llm_bundle.get("hashtags"), fallback_bundle["hashtags"], 5)
    cta_text = _choose_copy_text(llm_bundle.get("ctaText"), fallback_bundle["ctaText"], 18, detail_location)
    scene_text = _normalize_copy_surface_map(llm_bundle.get("sceneText"), fallback_bundle["sceneText"], 38, detail_location)
    sub_text = _normalize_copy_surface_map(llm_bundle.get("subText"), fallback_bundle["subText"], 78, detail_location)
    return {
        "hookText": hook_text,
        "captions": captions,
        "hashtags": hashtags,
        "ctaText": cta_text,
        "sceneText": scene_text,
        "subText": sub_text,
    }


def _choose_copy_text(candidate: Any, fallback: str, max_length: int, detail_location: str) -> str:
    if not isinstance(candidate, str):
        return fallback
    normalized = " ".join(candidate.strip().split())
    if not normalized:
        return fallback
    if detail_location and detail_location in normalized:
        return fallback
    if any(char.isdigit() for char in normalized) and not any(char.isdigit() for char in fallback):
        return fallback
    return normalized[:max_length]


def _normalize_copy_list(candidate: Any, fallback: list[str], expected_count: int, max_length: int, detail_location: str) -> list[str]:
    if not isinstance(candidate, list):
        return fallback
    normalized: list[str] = []
    for index in range(expected_count):
        fallback_item = fallback[index] if index < len(fallback) else fallback[-1]
        value = candidate[index] if index < len(candidate) else fallback_item
        normalized.append(_choose_copy_text(value, fallback_item, max_length, detail_location))
    return normalized


def _normalize_hashtag_list(candidate: Any, fallback: list[str], expected_count: int) -> list[str]:
    if not isinstance(candidate, list):
        return fallback
    normalized: list[str] = []
    for raw_value in candidate:
        if not isinstance(raw_value, str):
            continue
        value = raw_value.strip().replace(" ", "")
        if not value:
            continue
        if not value.startswith("#"):
            value = f"#{value.lstrip('#')}"
        if value not in normalized:
            normalized.append(value[:24])
        if len(normalized) == expected_count:
            break
    for fallback_item in fallback:
        if fallback_item not in normalized:
            normalized.append(fallback_item)
        if len(normalized) == expected_count:
            break
    return normalized[:expected_count]


def _normalize_copy_surface_map(candidate: Any, fallback: dict[str, str], max_length: int, detail_location: str) -> dict[str, str]:
    if not isinstance(candidate, dict):
        return fallback
    normalized: dict[str, str] = {}
    for key, fallback_value in fallback.items():
        normalized[key] = _choose_copy_text(candidate.get(key), fallback_value, max_length, detail_location)
    return normalized


def _extract_openai_response_text(payload: dict[str, Any]) -> str:
    if isinstance(payload.get("output_text"), str) and payload["output_text"].strip():
        return payload["output_text"].strip()

    texts: list[str] = []
    for output in payload.get("output", []):
        if not isinstance(output, dict):
            continue
        for content in output.get("content", []):
            if not isinstance(content, dict):
                continue
            text_value = content.get("text")
            if isinstance(text_value, str) and text_value.strip():
                texts.append(text_value.strip())
    return "\n".join(texts).strip()


def _parse_json_object(raw_text: str) -> dict[str, Any]:
    stripped = raw_text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.startswith("json"):
            stripped = stripped[4:].strip()
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid_json:{raw_text[:200]}") from exc
    if not isinstance(parsed, dict):
        raise RuntimeError(f"invalid_payload_type:{type(parsed)!r}")
    return parsed


def _sanitize_copy_generation_error(exc: Exception) -> str:
    message = str(exc).replace("\n", " ").replace("\r", " ").strip()
    if not message:
        return exc.__class__.__name__
    return message[:160]


def _build_active_copy_policy_state(project: sqlite3.Row, copy_rule: dict, quick_options: dict, input_snapshot: dict) -> dict:
    location_policy = copy_rule.get("locationPolicy") if isinstance(copy_rule, dict) else None
    configured_surfaces: list[str] = []
    if isinstance(location_policy, dict):
        for surface in location_policy.get("forbiddenDetailLocationSurfaces", []):
            if isinstance(surface, str) and surface not in configured_surfaces:
                configured_surfaces.append(surface)

    detail_location_present = bool(str(project["detail_location"] or "").strip())
    emphasize_region_requested = bool(quick_options.get("emphasizeRegion") or input_snapshot.get("emphasizeRegion"))
    guard_active = bool(detail_location_present and configured_surfaces)

    return {
        "detailLocationPolicyId": location_policy.get("policyId") if isinstance(location_policy, dict) else None,
        "forbiddenDetailLocationSurfaces": configured_surfaces,
        "guardActive": guard_active,
        "emphasizeRegionRequested": emphasize_region_requested,
        "detailLocationPresent": detail_location_present,
    }


def _load_manifest_json(template_spec_root: Path, manifest_name: str) -> dict | None:
    manifest_path = template_spec_root / "manifests" / manifest_name
    if not manifest_path.exists():
        return None
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _normalize_quick_option_state(quick_options: dict, input_snapshot: dict) -> dict[str, bool]:
    return {
        "highlightPrice": bool(quick_options.get("highlightPrice") or input_snapshot.get("highlightPrice")),
        "shorterCopy": bool(quick_options.get("shorterCopy") or input_snapshot.get("shorterCopy")),
        "emphasizeRegion": bool(quick_options.get("emphasizeRegion") or input_snapshot.get("emphasizeRegion")),
    }


def _collect_experiment_ids(*sources: object) -> list[str]:
    experiment_ids: list[str] = []

    def add_value(value: object) -> None:
        if isinstance(value, str) and value.startswith("EXP-") and value not in experiment_ids:
            experiment_ids.append(value)

    for source in sources:
        if isinstance(source, dict):
            for value in source.values():
                add_value(value)
        elif isinstance(source, list):
            for value in source:
                add_value(value)
        else:
            add_value(source)

    return experiment_ids


def _scenario_matches_prompt_context(scenario: dict, prompt_context: dict) -> bool:
    if str(scenario.get("purpose") or "") != prompt_context["purpose"]:
        return False
    if str(scenario.get("templateId") or "") != prompt_context["templateId"]:
        return False
    if str(scenario.get("styleId") or "") != prompt_context["styleId"]:
        return False

    scenario_quick_options = scenario.get("quickOptions", {})
    if isinstance(scenario_quick_options, dict):
        for key, value in scenario_quick_options.items():
            if isinstance(value, bool) and prompt_context["quickOptions"].get(key) is not value:
                return False

    return True


def _build_prompt_baseline_profile_summary(
    *,
    profile_id: str,
    label: str,
    profile_kind: str,
    status: str,
    source_type: str,
    selected_scenario: dict,
    selected_model: dict,
    prompt_preset: dict,
    evaluation_policy: dict,
    usage_guidance: list[str],
    evidence_ids: list[str],
    snapshot_experiment_id: str | None,
    prompt_variant_id: str | None,
    prompt_context: dict,
) -> dict:
    applicable = _scenario_matches_prompt_context(selected_scenario, prompt_context)

    required_score = evaluation_policy.get("requiredScore") if isinstance(evaluation_policy, dict) else None
    if not isinstance(required_score, (int, float)):
        required_score = None

    scenario_quick_options = selected_scenario.get("quickOptions", {}) if isinstance(selected_scenario, dict) else {}
    if not isinstance(scenario_quick_options, dict):
        scenario_quick_options = {}

    return {
        "profileId": profile_id,
        "label": label,
        "profileKind": profile_kind,
        "status": status,
        "sourceType": source_type,
        "evidenceExperimentIds": evidence_ids,
        "snapshotExperimentId": snapshot_experiment_id,
        "promptVariantId": prompt_variant_id,
        "scenarioId": selected_scenario.get("scenarioId") if isinstance(selected_scenario, dict) else None,
        "purpose": str(selected_scenario.get("purpose") or ""),
        "templateId": str(selected_scenario.get("templateId") or ""),
        "styleId": str(selected_scenario.get("styleId") or ""),
        "scenarioQuickOptions": {
            "highlightPrice": bool(scenario_quick_options.get("highlightPrice")),
            "shorterCopy": bool(scenario_quick_options.get("shorterCopy")),
            "emphasizeRegion": bool(scenario_quick_options.get("emphasizeRegion")),
        },
        "model": {
            "provider": str(selected_model.get("provider") or ""),
            "modelName": str(selected_model.get("modelName") or ""),
            "role": str(selected_model.get("role") or ""),
        },
        "promptPresetId": prompt_preset.get("presetId") if isinstance(prompt_preset, dict) else None,
        "locationPolicyId": evaluation_policy.get("locationPolicyId") if isinstance(evaluation_policy, dict) else None,
        "requiredScore": required_score,
        "usageGuidance": usage_guidance,
        "applicable": applicable,
    }


def _build_model_summary(model: dict | None) -> dict:
    model = model if isinstance(model, dict) else {}
    return {
        "provider": str(model.get("provider") or ""),
        "modelName": str(model.get("modelName") or ""),
        "role": str(model.get("role") or ""),
    }


def _is_filled_model(model: dict | None) -> bool:
    return isinstance(model, dict) and bool(model.get("provider")) and bool(model.get("modelName"))


def _models_match(left: dict | None, right: dict | None) -> bool:
    if not _is_filled_model(left) or not _is_filled_model(right):
        return False
    return str(left.get("provider")) == str(right.get("provider")) and str(left.get("modelName")) == str(right.get("modelName"))


def _build_transport_recommendation(source: dict | None) -> dict | None:
    if not isinstance(source, dict):
        return None
    return {
        "mode": str(source.get("mode") or ""),
        "defaultProfileId": str(source.get("defaultProfileId") or "") or None,
        "fallbackProfileId": str(source.get("fallbackProfileId") or "") or None,
        "trigger": str(source.get("trigger") or "") or None,
    }


def _build_operational_check_summary(source: dict, prompt_context: dict, recommended_profile: dict | None) -> dict:
    model = _build_model_summary(source.get("selectedModel") if isinstance(source.get("selectedModel"), dict) else {})
    target_template_id = str(source.get("targetTemplateId") or "") or None
    target_scenario_id = str(source.get("targetScenarioId") or "") or None
    applicable_by_template = target_template_id is None or target_template_id == prompt_context["templateId"]
    applicable_by_scenario = target_scenario_id is None or target_scenario_id == (recommended_profile or {}).get("scenarioId")

    return {
        "experimentId": str(source.get("experimentId") or ""),
        "targetScenarioId": target_scenario_id,
        "targetTemplateId": target_template_id,
        "result": str(source.get("result") or ""),
        "model": model if _is_filled_model(model) else None,
        "applicable": applicable_by_template and applicable_by_scenario,
        "appliesToRecommendedModel": _models_match(model, (recommended_profile or {}).get("model") if isinstance(recommended_profile, dict) else None),
        "notes": [item for item in source.get("notes", []) if isinstance(item, str)],
        "transportRecommendation": _build_transport_recommendation(
            source.get("transportRecommendation") if isinstance(source.get("transportRecommendation"), dict) else None
        ),
    }


def _dedupe_notes(values: list[str]) -> list[str]:
    unique: list[str] = []
    for value in values:
        if value and value not in unique:
            unique.append(value)
    return unique


def _collect_profile_mismatch_dimensions(profile: dict | None, prompt_context: dict) -> list[str]:
    if not isinstance(profile, dict):
        return []

    mismatches: list[str] = []
    if str(profile.get("purpose") or "") != str(prompt_context.get("purpose") or ""):
        mismatches.append("purpose")
    if str(profile.get("templateId") or "") != str(prompt_context.get("templateId") or ""):
        mismatches.append("templateId")
    if str(profile.get("styleId") or "") != str(prompt_context.get("styleId") or ""):
        mismatches.append("styleId")

    prompt_quick_options = prompt_context.get("quickOptions", {}) if isinstance(prompt_context, dict) else {}
    if not isinstance(prompt_quick_options, dict):
        prompt_quick_options = {}
    scenario_quick_options = profile.get("scenarioQuickOptions", {}) if isinstance(profile.get("scenarioQuickOptions"), dict) else {}
    for key, value in scenario_quick_options.items():
        if isinstance(value, bool) and prompt_quick_options.get(key) is not value:
            mismatches.append(f"quickOptions.{key}")

    return mismatches


def _build_profile_distance_key(mismatches: list[str], profile: dict | None) -> tuple[int, int, int, int]:
    structural_count = sum(1 for item in mismatches if item in {"purpose", "templateId", "styleId"})
    quick_option_count = sum(1 for item in mismatches if item.startswith("quickOptions."))
    profile_kind_bias = 0 if str((profile or {}).get("profileKind") or "") == "option" else 1
    return (structural_count, quick_option_count, len(mismatches), profile_kind_bias)


def _build_execution_hint(recommended_profile: dict | None, operational_checks: list[dict]) -> dict:
    if not isinstance(recommended_profile, dict):
        return {
            "status": "coverage_gap",
            "summary": "현재 컨텍스트와 exact match되는 prompt profile이 없어 baseline reference만 존재합니다.",
            "recommendedProfileId": None,
            "recommendedModel": None,
            "notes": ["현재 결과는 profile coverage 밖이므로, main baseline은 참고용으로만 보셔야 합니다."],
            "transportRecommendation": None,
        }

    matched_operational_check = next(
        (
            item
            for item in operational_checks
            if item.get("applicable") and item.get("appliesToRecommendedModel") and item.get("transportRecommendation")
        ),
        None,
    )
    status = "default_match" if recommended_profile.get("profileKind") == "default" else "option_match"
    notes = _dedupe_notes(
        [
            "현재 컨텍스트는 main baseline과 exact match됩니다."
            if status == "default_match"
            else "현재 컨텍스트는 main baseline exact match가 아니라 option profile 기준으로 권장됩니다.",
            *[item for item in recommended_profile.get("usageGuidance", []) if isinstance(item, str)][:2],
            *([matched_operational_check["notes"][0]] if matched_operational_check and matched_operational_check.get("notes") else []),
        ]
    )

    return {
        "status": status,
        "summary": (
            "현재 컨텍스트는 main baseline을 그대로 참고할 수 있습니다."
            if status == "default_match"
            else "현재 컨텍스트는 option profile을 우선 참고하는 편이 맞습니다."
        ),
        "recommendedProfileId": recommended_profile.get("profileId"),
        "recommendedModel": recommended_profile.get("model") if _is_filled_model(recommended_profile.get("model")) else None,
        "notes": notes,
        "transportRecommendation": (
            {
                **matched_operational_check["transportRecommendation"],
                "sourceExperimentId": matched_operational_check.get("experimentId"),
            }
            if matched_operational_check and isinstance(matched_operational_check.get("transportRecommendation"), dict)
            else None
        ),
        }


def _build_coverage_hint(
    recommended_profile: dict | None,
    default_profile: dict | None,
    candidate_profiles: list[dict],
    prompt_context: dict,
) -> dict | None:
    if isinstance(recommended_profile, dict):
        return None

    profiles = [profile for profile in [default_profile, *candidate_profiles] if isinstance(profile, dict)]
    if not profiles:
        return {
            "summary": "비교 가능한 prompt profile이 아직 등록되지 않아 coverage gap 원인을 계산할 수 없습니다.",
            "nearestProfileId": None,
            "nearestProfileKind": None,
            "mismatchDimensions": [],
        }

    nearest_profile: dict | None = None
    nearest_mismatches: list[str] | None = None
    nearest_distance_key: tuple[int, int, int, int] | None = None
    for profile in profiles:
        mismatches = _collect_profile_mismatch_dimensions(profile, prompt_context)
        distance_key = _build_profile_distance_key(mismatches, profile)
        if nearest_distance_key is None or distance_key < nearest_distance_key:
            nearest_profile = profile
            nearest_mismatches = mismatches
            nearest_distance_key = distance_key

    mismatch_dimensions = nearest_mismatches or []
    nearest_profile_id = str((nearest_profile or {}).get("profileId") or "") or None
    nearest_profile_kind = str((nearest_profile or {}).get("profileKind") or "") or None
    mismatch_label = ", ".join(mismatch_dimensions[:3]) if mismatch_dimensions else "미기록"
    structural_mismatch = any(item in {"purpose", "templateId", "styleId"} for item in mismatch_dimensions)
    quick_option_only = bool(mismatch_dimensions) and all(item.startswith("quickOptions.") for item in mismatch_dimensions)

    if quick_option_only and not structural_mismatch:
        gap_class = "quick_option_gap"
        recommended_action = "consider_option_profile"
        summary = (
            f"현재 컨텍스트와 exact match되는 prompt profile은 없고, 가장 가까운 profile은 {nearest_profile_id or '미기록'}입니다. "
            f"현재 mismatch 축은 {mismatch_label}이며, quick option 차이로 보여 option profile 후보로 검토하는 편이 맞습니다."
        )
    elif structural_mismatch:
        gap_class = "scenario_gap"
        recommended_action = "run_new_scenario_experiment"
        summary = (
            f"현재 컨텍스트와 exact match되는 prompt profile은 없고, 가장 가까운 profile은 {nearest_profile_id or '미기록'}입니다. "
            f"현재 mismatch 축은 {mismatch_label}이며, scenario 축 차이로 보여 새 scenario 실험이 먼저입니다."
        )
    else:
        gap_class = "mixed_gap"
        recommended_action = "keep_manual_review"
        summary = (
            f"현재 컨텍스트와 exact match되는 prompt profile은 없고, 가장 가까운 profile은 {nearest_profile_id or '미기록'}입니다. "
            f"현재 mismatch 축은 {mismatch_label}이며, 혼합 mismatch라서 우선 manual review로 두는 편이 맞습니다."
        )

    return {
        "summary": summary,
        "nearestProfileId": nearest_profile_id,
        "nearestProfileKind": nearest_profile_kind if nearest_profile_kind in {"default", "option"} else None,
        "mismatchDimensions": mismatch_dimensions,
        "gapClass": gap_class,
        "recommendedAction": recommended_action,
    }


def _build_policy_hint(execution_hint: dict | None) -> dict | None:
    if not isinstance(execution_hint, dict):
        return None

    status = str(execution_hint.get("status") or "coverage_gap")
    recommended_model = execution_hint.get("recommendedModel") if _is_filled_model(execution_hint.get("recommendedModel")) else None
    transport_recommendation = (
        execution_hint.get("transportRecommendation")
        if isinstance(execution_hint.get("transportRecommendation"), dict)
        else None
    )
    notes = [item for item in execution_hint.get("notes", []) if isinstance(item, str)]

    if status == "default_match":
        return {
            "policyState": "main_reference",
            "recommendedAction": "use_main_profile_reference",
            "requiresManualReview": False,
            "summary": "현재 컨텍스트는 main baseline 기준으로 운영 판단을 이어가면 됩니다.",
            "recommendedProfileId": execution_hint.get("recommendedProfileId"),
            "recommendedModel": recommended_model,
            "transportRecommendation": transport_recommendation,
            "notes": notes,
        }

    if status == "option_match":
        return {
            "policyState": "option_reference",
            "recommendedAction": "use_option_profile_reference",
            "requiresManualReview": False,
            "summary": "현재 컨텍스트는 option profile 기준으로 운영 판단을 이어가는 편이 맞습니다.",
            "recommendedProfileId": execution_hint.get("recommendedProfileId"),
            "recommendedModel": recommended_model,
            "transportRecommendation": transport_recommendation,
            "notes": notes,
        }

    return {
        "policyState": "coverage_gap",
        "recommendedAction": "manual_review_required",
        "requiresManualReview": True,
        "summary": "현재 컨텍스트는 baseline coverage 밖이라 자동 정책 판단보다 수동 검토가 먼저입니다.",
        "recommendedProfileId": None,
        "recommendedModel": None,
        "transportRecommendation": None,
        "notes": notes,
    }


def _build_prompt_baseline_summary(
    template_spec_root: Path,
    *,
    purpose: str,
    template_id: str,
    style_id: str,
    quick_options: dict,
    input_snapshot: dict,
) -> dict | None:
    manifest = _load_manifest_json(template_spec_root, "prompt-baseline-v1.json")
    if not isinstance(manifest, dict):
        return None

    prompt_context = {
        "purpose": purpose,
        "templateId": template_id,
        "styleId": style_id,
        "quickOptions": _normalize_quick_option_state(quick_options, input_snapshot),
    }

    default_profile = _build_prompt_baseline_profile_summary(
        profile_id="main_baseline",
        label=str(manifest.get("baselineId") or "main_baseline"),
        profile_kind="default",
        status=str(manifest.get("status") or "unknown"),
        source_type="baseline_manifest",
        selected_scenario=manifest.get("selectedScenario") if isinstance(manifest.get("selectedScenario"), dict) else {},
        selected_model=manifest.get("selectedModel") if isinstance(manifest.get("selectedModel"), dict) else {},
        prompt_preset=manifest.get("promptPreset") if isinstance(manifest.get("promptPreset"), dict) else {},
        evaluation_policy=manifest.get("evaluationPolicy") if isinstance(manifest.get("evaluationPolicy"), dict) else {},
        usage_guidance=[item for item in manifest.get("usageGuidance", []) if isinstance(item, str)],
        evidence_ids=_collect_experiment_ids(manifest.get("sourceEvidence")),
        snapshot_experiment_id=None,
        prompt_variant_id=None,
        prompt_context=prompt_context,
    )

    candidate_profiles: list[dict] = []
    for option in manifest.get("baselineOptions", []):
        if not isinstance(option, dict):
            continue
        candidate_profiles.append(
            _build_prompt_baseline_profile_summary(
                profile_id=str(option.get("profileId") or option.get("label") or "candidate_profile"),
                label=str(option.get("label") or option.get("profileId") or "candidate_profile"),
                profile_kind="option",
                status=str(option.get("status") or manifest.get("status") or "candidate"),
                source_type=str(option.get("sourceType") or "baseline_option"),
                selected_scenario=option.get("selectedScenario") if isinstance(option.get("selectedScenario"), dict) else {},
                selected_model=option.get("selectedModel") if isinstance(option.get("selectedModel"), dict) else {},
                prompt_preset=option.get("promptPreset") if isinstance(option.get("promptPreset"), dict) else {},
                evaluation_policy=option.get("evaluationPolicy") if isinstance(option.get("evaluationPolicy"), dict) else {},
                usage_guidance=[item for item in option.get("usageGuidance", []) if isinstance(item, str)],
                evidence_ids=_collect_experiment_ids(option.get("sourceExperimentId"), option.get("sourceEvidence")),
                snapshot_experiment_id=str(option.get("snapshotExperimentId") or "") or None,
                prompt_variant_id=str(option.get("promptVariantId") or "") or None,
                prompt_context=prompt_context,
            )
        )

    recommended_profile = default_profile if default_profile.get("applicable") else next(
        (profile for profile in candidate_profiles if profile.get("applicable")),
        None,
    )
    operational_checks: list[dict] = []
    for item in manifest.get("operationalChecks", []):
        if not isinstance(item, dict):
            continue
        operational_checks.append(_build_operational_check_summary(item, prompt_context, recommended_profile))
    execution_hint = _build_execution_hint(recommended_profile, operational_checks)
    coverage_hint = _build_coverage_hint(recommended_profile, default_profile, candidate_profiles, prompt_context)

    return {
        "baselineId": str(manifest.get("baselineId") or ""),
        "status": str(manifest.get("status") or "unknown"),
        "scope": str(manifest.get("scope") or "prompt_generation"),
        "recommendationOnly": True,
        "context": prompt_context,
        "defaultProfile": default_profile,
        "recommendedProfile": recommended_profile,
        "candidateProfiles": candidate_profiles,
        "executionHint": execution_hint,
        "coverageHint": coverage_hint,
        "policyHint": _build_policy_hint(execution_hint),
        "operationalChecks": operational_checks,
    }


def _build_copy_deck(template_spec_root: Path, template_id: str, copy_bundle: dict) -> dict | None:
    manifest = _load_manifest_json(template_spec_root, "slot-layer-map.json")
    if not isinstance(manifest, dict):
        return None
    template_defs = manifest.get("templates", [])
    template_def = next((item for item in template_defs if item.get("templateId") == template_id), None)
    if not isinstance(template_def, dict):
        return None

    slot_groups = template_def.get("slotGroups", {})
    hook_def = slot_groups.get("hook", {})
    body_def = slot_groups.get("body", {})
    body_blocks = []

    for block in body_def.get("bodyBlocks", []):
        if not isinstance(block, dict):
            continue
        text_role = str(block.get("textRole") or "")
        if not text_role:
            continue
        body_blocks.append(
            {
                "blockId": str(block.get("blockId") or text_role),
                "textRole": text_role,
                "uiLabel": str(block.get("uiLabel") or text_role),
                "primaryLine": str(copy_bundle.get("sceneText", {}).get(text_role, "")),
                "supportLine": copy_bundle.get("subText", {}).get(text_role),
            }
        )

    hook_support = copy_bundle.get("captions", [None])[0] if hook_def.get("recommendedSupportField") else None

    return {
        "templateId": template_id,
        "hook": {
            "primaryLine": copy_bundle.get("hookText", ""),
            "supportLine": hook_support,
        },
        "body": {
            "blocks": body_blocks,
        },
        "cta": {
            "primaryLine": copy_bundle.get("ctaText", ""),
            "supportLine": None,
        },
    }


def _build_scene_layer_summary(template_spec_root: Path, template_id: str) -> dict | None:
    manifest = _load_manifest_json(template_spec_root, "slot-layer-map.json")
    if not isinstance(manifest, dict):
        return None
    template_defs = manifest.get("templates", [])
    template_def = next((item for item in template_defs if item.get("templateId") == template_id), None)
    if not isinstance(template_def, dict):
        return None

    text_role_map = manifest.get("textRoleToLayer", {})
    slot_groups = template_def.get("slotGroups", {})
    items: list[dict] = []

    hook_def = slot_groups.get("hook", {})
    hook_text_roles = hook_def.get("textRoles", [])
    hook_text_role = hook_text_roles[0] if hook_text_roles else "hook"
    hook_label = text_role_map.get(hook_text_role, {}).get("uiLabel", "후킹 문장")
    for scene_id in hook_def.get("sceneIds", []):
        items.append(
            {
                "sceneId": scene_id,
                "slotGroup": "hook",
                "textRole": hook_text_role,
                "uiLabel": hook_label,
            }
        )

    body_def = slot_groups.get("body", {})
    body_scene_ids = body_def.get("sceneIds", [])
    body_blocks = body_def.get("bodyBlocks", [])
    body_text_roles = body_def.get("textRoles", [])
    for index, scene_id in enumerate(body_scene_ids):
        block = body_blocks[index] if index < len(body_blocks) else {}
        text_role = block.get("textRole") or (body_text_roles[index] if index < len(body_text_roles) else "body")
        ui_label = block.get("uiLabel") or text_role_map.get(text_role, {}).get("uiLabel", "본문")
        items.append(
            {
                "sceneId": scene_id,
                "slotGroup": "body",
                "textRole": text_role,
                "uiLabel": ui_label,
            }
        )

    cta_def = slot_groups.get("cta", {})
    cta_text_roles = cta_def.get("textRoles", [])
    cta_text_role = cta_text_roles[0] if cta_text_roles else "cta"
    cta_label = text_role_map.get(cta_text_role, {}).get("uiLabel", "행동 유도")
    for scene_id in cta_def.get("sceneIds", []):
        items.append(
            {
                "sceneId": scene_id,
                "slotGroup": "cta",
                "textRole": cta_text_role,
                "uiLabel": cta_label,
            }
        )

    return {
        "templateId": template_id,
        "items": items,
    }


def _build_change_impact_summary(run_type: str, quick_options: dict) -> dict:
    actions: list[dict] = []

    def add_action(action_id: str, label: str, affected_layers: list[str], note: str) -> None:
        actions.append(
            {
                "actionId": action_id,
                "label": label,
                "affectedLayers": affected_layers,
                "note": note,
            }
        )

    if quick_options.get("shorterCopy"):
        add_action("shorterCopy", "문구 더 짧게", ["hook", "body", "cta"], "전체 카피 길이를 줄여 hook/body/cta 전반에 영향을 줍니다.")
    if quick_options.get("highlightPrice"):
        add_action("highlightPrice", "가격 더 크게", ["body"], "혜택이나 가격 설명이 들어가는 body block을 우선적으로 바꿉니다.")
    if quick_options.get("emphasizeRegion"):
        add_action("emphasizeRegion", "지역명 강조", ["hook", "body"], "regionName 노출을 더 세게 만들어 hook과 body 문구에 영향을 줍니다.")

    style_override = quick_options.get("styleOverride")
    if isinstance(style_override, str) and style_override:
        add_action("styleOverride", "스타일 변경", ["visual"], f"스타일을 `{style_override}`로 바꿔 시각 톤과 말투에 영향을 줍니다.")

    template_override = quick_options.get("templateId")
    if isinstance(template_override, str) and template_override:
        add_action("templateId", "템플릿 변경", ["hook", "body", "cta", "structure"], f"템플릿을 `{template_override}`로 바꿔 scene 구조와 카피 슬롯 전체에 영향을 줍니다.")

    impact_layers: list[str] = []
    for action in actions:
        for layer in action["affectedLayers"]:
            if layer not in impact_layers:
                impact_layers.append(layer)

    return {
        "runType": "regenerate" if run_type == "regenerate" else "initial",
        "impactLayers": impact_layers,
        "activeActions": actions,
    }


def _set_step(conn: sqlite3.Connection, generation_run_id: str, step_name: str, status: str) -> None:
    now = utc_now()
    conn.execute(
        """
        UPDATE generation_run_steps
        SET status = ?, started_at = COALESCE(started_at, ?), finished_at = CASE WHEN ? = 'completed' THEN ? ELSE finished_at END, updated_at = ?, error_code = NULL
        WHERE generation_run_id = ? AND step_name = ?
        """,
        (status, now, status, now, now, generation_run_id, step_name),
    )


def _complete_step(conn: sqlite3.Connection, generation_run_id: str, step_name: str) -> None:
    _set_step(conn, generation_run_id, step_name, "completed")


def _mark_generation_failed(conn: sqlite3.Connection, project_id: str, generation_run_id: str, error_code: str, _detail: str) -> None:
    now = utc_now()
    conn.execute(
        "UPDATE generation_runs SET status = ?, finished_at = ?, error_code = ? WHERE id = ?",
        ("failed", now, error_code, generation_run_id),
    )
    conn.execute(
        "UPDATE content_projects SET current_status = ?, updated_at = ? WHERE id = ?",
        ("failed", now, project_id),
    )
    conn.execute(
        """
        UPDATE generation_run_steps
        SET status = CASE WHEN status = 'processing' THEN 'failed' ELSE status END,
            finished_at = CASE WHEN status = 'processing' THEN ? ELSE finished_at END,
            updated_at = ?,
            error_code = CASE WHEN status = 'processing' THEN ? ELSE error_code END
        WHERE generation_run_id = ?
        """,
        (now, now, error_code, generation_run_id),
    )
