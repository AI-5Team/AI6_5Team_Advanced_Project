from __future__ import annotations

import io
import json
import sqlite3
import subprocess
from pathlib import Path
from uuid import uuid4

from PIL import Image

from services.worker.adapters.template_loader import load_style, load_template
from services.worker.planning.scene_plan import build_scene_plan
from services.worker.pipelines.generation import _build_copy_bundle, _build_prompt_baseline_summary, _resolve_bgrade_scene_policy, run_generation_job
from services.worker.renderers.media import render_video
from services.worker.renderers.framing import choose_prepare_mode, classify_shot_type


def make_png(path: Path, color: tuple[int, int, int]) -> None:
    image = Image.new("RGB", (1200, 1600), color)
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


def initialize_schema(db_path: Path) -> None:
    from app.core.config import get_settings as app_get_settings
    from services.api.app.core.config import get_settings
    from services.api.app.core.database import initialize_database

    app_get_settings.cache_clear()
    get_settings.cache_clear()
    initialize_database()


def test_generation_pipeline(monkeypatch, tmp_path):
    runtime_dir = tmp_path / ".runtime"
    storage_dir = runtime_dir / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)
    db_path = runtime_dir / "app.sqlite3"
    monkeypatch.setenv("APP_RUNTIME_DIR", str(runtime_dir))
    monkeypatch.setenv("APP_STORAGE_DIR", str(storage_dir))
    monkeypatch.setenv("APP_DB_PATH", str(db_path))

    from app.core.config import get_settings as app_get_settings
    from services.api.app.core.config import get_settings
    from services.api.app.core.database import initialize_database, utc_now

    app_get_settings.cache_clear()
    get_settings.cache_clear()
    initialize_database()

    project_id = str(uuid4())
    user_id = str(uuid4())
    asset_id = str(uuid4())
    run_id = str(uuid4())
    raw_dir = storage_dir / "projects" / project_id / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"{asset_id}.png"
    make_png(raw_path, (220, 120, 80))

    with sqlite3.connect(db_path) as connection:
      now = utc_now()
      connection.execute("INSERT INTO users (id, email, password_hash, name, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)", (user_id, "worker@test.com", "x", "worker", now, now))
      connection.execute(
          """
          INSERT INTO content_projects (
            id, user_id, business_type, purpose, style, region_name, detail_location,
            selected_channels_json, latest_generation_run_id, current_status, created_at, updated_at
          )
          VALUES (?, ?, 'cafe', 'new_menu', 'friendly', '성수동', '서울숲', '["instagram"]', ?, 'queued', ?, ?)
          """,
          (project_id, user_id, run_id, now, now),
      )
      connection.execute(
          """
          INSERT INTO project_assets (
            id, project_id, original_file_name, mime_type, file_size_bytes, width, height,
            storage_path, warnings_json, created_at
          )
          VALUES (?, ?, 'sample.png', 'image/png', ?, 1200, 1600, ?, '[]', ?)
          """,
          (asset_id, project_id, raw_path.stat().st_size, f"/projects/{project_id}/raw/{asset_id}.png", now),
      )
      connection.execute(
          """
          INSERT INTO generation_runs (
            id, project_id, run_type, trigger_source, template_id,
            input_snapshot_json, quick_options_snapshot_json, status, error_code, started_at, finished_at, created_at
          )
          VALUES (?, ?, 'initial', 'user', 'T01', ?, '{}', 'queued', NULL, NULL, NULL, ?)
          """,
          (run_id, project_id, '{"assetIds":["' + asset_id + '"],"templateId":"T01"}', now),
      )
      for step in ["preprocessing", "copy_generation", "video_rendering", "post_rendering", "packaging"]:
          connection.execute(
              "INSERT INTO generation_run_steps (id, generation_run_id, step_name, status, error_code, started_at, finished_at, updated_at) VALUES (?, ?, ?, 'pending', NULL, NULL, NULL, ?)",
              (str(uuid4()), run_id, step, now),
          )
      connection.commit()

    run_generation_job(db_path, storage_dir, Path(__file__).resolve().parents[3] / "packages" / "template-spec", project_id, run_id)

    with sqlite3.connect(db_path) as connection:
        run_row = connection.execute("SELECT status FROM generation_runs WHERE id = ?", (run_id,)).fetchone()
        project_row = connection.execute("SELECT current_status FROM content_projects WHERE id = ?", (project_id,)).fetchone()
        variant_row = connection.execute(
            "SELECT video_path, post_image_path, preview_thumbnail_path, duration_sec FROM generated_variants WHERE generation_run_id = ?",
            (run_id,),
        ).fetchone()
        assert run_row[0] == "completed"
        assert project_row[0] == "generated"
        assert variant_row is not None

    run_dir = storage_dir / "projects" / project_id / "runs" / run_id
    video_path = storage_dir / variant_row[0].lstrip("/")
    post_path = storage_dir / variant_row[1].lstrip("/")
    thumb_path = storage_dir / variant_row[2].lstrip("/")
    scene_dir = run_dir / "scenes"
    render_meta_path = run_dir / "render-meta.json"
    scene_plan_path = run_dir / "scene-plan.json"
    caption_options_path = run_dir / "caption_options.json"
    hashtags_path = run_dir / "hashtags.json"

    assert video_path.exists()
    assert video_path.stat().st_size > 0
    assert post_path.exists()
    assert thumb_path.exists()
    assert variant_row[3] > 0
    assert render_meta_path.exists()
    assert scene_plan_path.exists()
    assert caption_options_path.exists()
    assert hashtags_path.exists()
    assert len(list(scene_dir.glob("*.png"))) >= 3

    scene_plan = json.loads(scene_plan_path.read_text(encoding="utf-8"))
    render_meta = json.loads(render_meta_path.read_text(encoding="utf-8"))
    assert scene_plan["templateId"] == "T01"
    assert scene_plan["sceneCount"] == 4
    assert len(scene_plan["scenes"]) == 4
    assert render_meta["scenePlanPath"].endswith("scene-plan.json")
    assert render_meta["sceneCount"] == 4
    assert render_meta["sceneLayerSummary"]["templateId"] == "T01"
    assert len(render_meta["sceneLayerSummary"]["items"]) == 4
    assert render_meta["changeImpactSummary"]["runType"] == "initial"
    assert render_meta["changeImpactSummary"]["activeActions"] == []
    assert render_meta["changeImpactSummary"]["impactLayers"] == []
    assert render_meta["copyPolicy"]["detailLocationPolicyId"] == "strict_all_surfaces"
    assert render_meta["copyPolicy"]["guardActive"] is True
    assert render_meta["copyPolicy"]["detailLocationPresent"] is True
    assert render_meta["copyPolicy"]["emphasizeRegionRequested"] is False
    assert render_meta["copyDeck"]["templateId"] == "T01"
    assert render_meta["copyGeneration"]["sourceMode"] == "deterministic_rule"
    assert render_meta["copyGeneration"]["provider"] == "local_rule"
    assert render_meta["copyGeneration"]["fallbackReason"] is None
    assert render_meta["copyDeck"]["hook"]["primaryLine"]
    assert len(render_meta["copyDeck"]["body"]["blocks"]) == 2
    assert render_meta["copyDeck"]["cta"]["primaryLine"]
    assert render_meta["promptBaselineSummary"]["baselineId"] == "PB-001"
    assert render_meta["promptBaselineSummary"]["defaultProfile"]["profileId"] == "main_baseline"
    assert render_meta["promptBaselineSummary"]["recommendedProfile"] is not None
    assert len(render_meta["promptBaselineSummary"]["candidateProfiles"]) >= 1
    assert render_meta["promptBaselineSummary"]["recommendedProfile"]["profileId"] == "new_menu_friendly_minimal_region_anchor"
    assert render_meta["promptBaselineSummary"]["executionHint"]["status"] == "option_match"
    assert render_meta["promptBaselineSummary"]["executionHint"]["recommendedProfileId"] == "new_menu_friendly_minimal_region_anchor"
    assert render_meta["promptBaselineSummary"]["coverageHint"] is None
    assert render_meta["promptBaselineSummary"]["policyHint"]["policyState"] == "option_reference"
    assert render_meta["promptBaselineSummary"]["policyHint"]["recommendedAction"] == "use_option_profile_reference"
    assert render_meta["promptBaselineSummary"]["policyHint"]["requiresManualReview"] is False
    assert len(render_meta["promptBaselineSummary"]["operationalChecks"]) >= 1
    assert render_meta["rendererFramingMode"] == "preprocessed_vertical"
    assert render_meta["rendererMotionMode"] == "static_concat"
    assert render_meta["rendererMotionPresets"] == []
    assert render_meta["rendererScenePolicies"] == []

    post_image = Image.open(post_path)
    thumb_image = Image.open(thumb_path)
    assert post_image.size == (1080, 1080)
    assert thumb_image.size == (720, 1280)


def test_generation_pipeline_supports_hybrid_source_video(monkeypatch, tmp_path):
    runtime_dir = tmp_path / ".runtime"
    storage_dir = runtime_dir / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)
    db_path = runtime_dir / "app.sqlite3"
    monkeypatch.setenv("APP_RUNTIME_DIR", str(runtime_dir))
    monkeypatch.setenv("APP_STORAGE_DIR", str(storage_dir))
    monkeypatch.setenv("APP_DB_PATH", str(db_path))

    from app.core.config import get_settings as app_get_settings
    from services.api.app.core.config import get_settings
    from services.api.app.core.database import initialize_database, utc_now

    app_get_settings.cache_clear()
    get_settings.cache_clear()
    initialize_database()

    project_id = str(uuid4())
    user_id = str(uuid4())
    asset_id = str(uuid4())
    run_id = str(uuid4())
    raw_dir = storage_dir / "projects" / project_id / "raw"
    hybrid_dir = storage_dir / "projects" / project_id / "hybrid"
    raw_dir.mkdir(parents=True, exist_ok=True)
    hybrid_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"{asset_id}.png"
    hybrid_scene_a = hybrid_dir / "scene-a.png"
    hybrid_scene_b = hybrid_dir / "scene-b.png"
    hybrid_video = hybrid_dir / "source.mp4"
    make_png(raw_path, (220, 120, 80))
    make_png(hybrid_scene_a, (220, 120, 80))
    make_png(hybrid_scene_b, (90, 120, 220))
    render_video([(hybrid_scene_a, 2.0), (hybrid_scene_b, 2.0)], hybrid_video, motion_presets=["push_in_center", "push_in_top"])

    with sqlite3.connect(db_path) as connection:
        now = utc_now()
        connection.execute("INSERT INTO users (id, email, password_hash, name, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)", (user_id, "worker@test.com", "x", "worker", now, now))
        connection.execute(
            """
            INSERT INTO content_projects (
              id, user_id, business_type, purpose, style, region_name, detail_location,
              selected_channels_json, latest_generation_run_id, current_status, created_at, updated_at
            )
            VALUES (?, ?, 'restaurant', 'promotion', 'b_grade_fun', '성수동', '서울숲', '["instagram"]', ?, 'queued', ?, ?)
            """,
            (project_id, user_id, run_id, now, now),
        )
        connection.execute(
            """
            INSERT INTO project_assets (
              id, project_id, original_file_name, mime_type, file_size_bytes, width, height,
              storage_path, warnings_json, created_at
            )
            VALUES (?, ?, 'sample.png', 'image/png', ?, 1200, 1600, ?, '[]', ?)
            """,
            (asset_id, project_id, raw_path.stat().st_size, f"/projects/{project_id}/raw/{asset_id}.png", now),
        )
        input_snapshot = json.dumps(
            {
                "assetIds": [asset_id],
                "templateId": "T02",
                "hybridSourceVideoPath": f"/projects/{project_id}/hybrid/source.mp4",
                "hybridSourceSelection": {
                    "selectionMode": "benchmark_gate",
                    "benchmarkId": "EXP-239",
                    "label": "규카츠",
                    "provider": "sora2_current_best",
                    "gateDecision": "manual_review",
                },
            },
            ensure_ascii=False,
        )
        connection.execute(
            """
            INSERT INTO generation_runs (
              id, project_id, run_type, trigger_source, template_id,
              input_snapshot_json, quick_options_snapshot_json, status, error_code, started_at, finished_at, created_at
            )
            VALUES (?, ?, 'initial', 'user', 'T02', ?, '{}', 'queued', NULL, NULL, NULL, ?)
            """,
            (run_id, project_id, input_snapshot, now),
        )
        for step in ["preprocessing", "copy_generation", "video_rendering", "post_rendering", "packaging"]:
            connection.execute(
                "INSERT INTO generation_run_steps (id, generation_run_id, step_name, status, error_code, started_at, finished_at, updated_at) VALUES (?, ?, ?, 'pending', NULL, NULL, NULL, ?)",
                (str(uuid4()), run_id, step, now),
            )
        connection.commit()

    run_generation_job(db_path, storage_dir, Path(__file__).resolve().parents[3] / "packages" / "template-spec", project_id, run_id)

    with sqlite3.connect(db_path) as connection:
        variant_row = connection.execute(
            "SELECT video_path, preview_thumbnail_path, render_meta_json FROM generated_variants WHERE generation_run_id = ?",
            (run_id,),
        ).fetchone()
        assert variant_row is not None

    video_path = storage_dir / variant_row[0].lstrip("/")
    thumb_path = storage_dir / variant_row[1].lstrip("/")
    render_meta = json.loads(variant_row[2])

    assert video_path.exists()
    assert video_path.stat().st_size > 0
    assert thumb_path.exists()
    assert render_meta["rendererVideoSourceMode"] == "hybrid_generated_clip"
    assert render_meta["rendererMotionMode"] == "hybrid_overlay_packaging"
    assert render_meta["rendererFramingMode"] == "hybrid_source_video"
    assert render_meta["rendererHybridSourceVideo"].endswith("/hybrid/source.mp4")
    assert render_meta["rendererHybridSourceSelection"]["provider"] == "sora2_current_best"
    assert render_meta["rendererHybridSourceSelection"]["gateDecision"] == "manual_review"
    assert render_meta["rendererHybridDurationStrategy"] == "freeze_last_frame"
    assert render_meta["rendererHybridTargetDurationSec"] == 6.4
    assert len(render_meta["rendererHybridOverlayTimeline"]) == 4
    assert probe_duration(video_path) >= 6.3


def test_build_copy_bundle_uses_openai_when_enabled(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("WORKER_COPY_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("WORKER_COPY_OPENAI_MODEL", "gpt-5-mini")

    source_path = tmp_path / "hero.png"
    make_png(source_path, (180, 110, 70))

    def fake_request_openai_copy_bundle(**kwargs):
        assert kwargs["model_name"] == "gpt-5-mini"
        assert len(kwargs["asset_paths"]) == 1
        return {
            "hookText": "성수동 신메뉴 한입컷",
            "captions": ["오늘 올리기 좋은 신메뉴 컷입니다.", "짧게 봐도 메뉴 매력이 바로 보입니다.", "방문 전에 저장하기 좋게 정리했습니다."],
            "hashtags": ["#성수동", "#카페홍보", "#신메뉴홍보", "#지역마케팅", "#숏폼광고"],
            "ctaText": "지금 저장해보세요",
            "sceneText": {
                "hook": "성수동 신메뉴 한입컷",
                "product_name": "대표 메뉴를 한 번에 소개",
                "difference": "신메뉴 포인트를 짧게 정리",
                "benefit": "짧게 봐도 장점이 남습니다",
                "urgency": "이번 주 업로드용으로 바로 사용",
                "cta": "지금 저장해보세요",
                "region_hook": "성수동 신메뉴 한입컷",
                "visit_reason": "방문 전에 보기 좋은 한 컷",
                "review_quote": "\"짧게 봐도 기억나는 컷\"",
            },
            "subText": {
                "hook": "오늘 올리기 좋은 신메뉴 컷입니다.",
                "product_name": "짧게 봐도 메뉴 매력이 바로 보입니다.",
                "difference": "방문 전에 저장하기 좋게 정리했습니다.",
                "benefit": "방문 전에 저장하기 좋게 정리했습니다.",
                "urgency": "방문 전에 저장하기 좋게 정리했습니다.",
                "cta": "지금 저장해보세요",
                "region_hook": "오늘 올리기 좋은 신메뉴 컷입니다.",
                "visit_reason": "짧게 봐도 메뉴 매력이 바로 보입니다.",
                "review_quote": "짧게 봐도 메뉴 매력이 바로 보입니다.",
            },
        }

    monkeypatch.setattr("services.worker.pipelines.generation._request_openai_copy_bundle", fake_request_openai_copy_bundle)

    bundle = _build_copy_bundle(
        {
            "region_name": "성수동",
            "business_type": "cafe",
            "purpose": "new_menu",
            "detail_location": "서울숲 근처",
        },
        {"title": "신메뉴 템플릿", "scenes": [{"textRole": "hook"}, {"textRole": "product_name"}, {"textRole": "cta"}]},
        {"sampleHooks": ["성수동 먼저 만나는 신메뉴"]},
        "friendly",
        {"emphasizeRegion": True},
        {"shorterCopy": True},
        [{"source": source_path}],
    )

    assert bundle["hookText"] == "성수동 신메뉴 한입컷"
    assert bundle["captions"][0] == "오늘 올리기 좋은 신메뉴 컷입니다."
    assert bundle["copyGeneration"]["sourceMode"] == "openai_live"
    assert bundle["copyGeneration"]["provider"] == "openai"
    assert bundle["copyGeneration"]["model"] == "gpt-5-mini"


def test_build_copy_bundle_falls_back_when_openai_output_breaks_policy(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("WORKER_COPY_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    source_path = tmp_path / "hero.png"
    make_png(source_path, (120, 120, 210))

    def fake_request_openai_copy_bundle(**kwargs):
        return {
            "hookText": "서울숲 근처 신메뉴 9900원",
            "captions": ["서울숲 근처에서 바로 보이는 9900원 메뉴", "지금 확인하세요", "오늘 저장하세요"],
            "hashtags": ["성수동", "#카페홍보", "#신메뉴홍보", "#지역마케팅", "#숏폼광고"],
            "ctaText": "9900원 확인",
            "sceneText": {"hook": "서울숲 근처 신메뉴 9900원"},
            "subText": {"hook": "서울숲 근처에서 바로 보이는 9900원 메뉴"},
        }

    monkeypatch.setattr("services.worker.pipelines.generation._request_openai_copy_bundle", fake_request_openai_copy_bundle)

    bundle = _build_copy_bundle(
        {
            "region_name": "성수동",
            "business_type": "cafe",
            "purpose": "new_menu",
            "detail_location": "서울숲 근처",
        },
        {"title": "신메뉴 템플릿", "scenes": [{"textRole": "hook"}, {"textRole": "product_name"}, {"textRole": "cta"}]},
        {"sampleHooks": ["성수동 먼저 만나는 신메뉴"]},
        "friendly",
        {"emphasizeRegion": True},
        {"shorterCopy": True},
        [{"source": source_path}],
    )

    assert "서울숲 근처" not in bundle["hookText"]
    assert "9900" not in bundle["hookText"]
    assert bundle["copyGeneration"]["sourceMode"] == "openai_live"
    assert bundle["ctaText"] != "9900원 확인"


def test_scene_plan_maps_promotion_and_review_templates(tmp_path: Path) -> None:
    asset_a = tmp_path / "asset-a.png"
    asset_b = tmp_path / "asset-b.png"
    make_png(asset_a, (240, 120, 80))
    make_png(asset_b, (90, 120, 220))
    processed_assets = [{"vertical": asset_a, "square": asset_a}, {"vertical": asset_b, "square": asset_b}]
    template_root = Path(__file__).resolve().parents[3] / "packages" / "template-spec"

    promotion_plan = build_scene_plan(
        project={"business_type": "restaurant", "purpose": "promotion", "region_name": "성수동"},
        template=load_template(template_root, "T02"),
        style=load_style(template_root, "b_grade_fun"),
        copy_bundle={
            "hookText": "오늘만 2천원 할인",
            "captions": ["혜택 먼저", "프로모션 설명", "마감 CTA"],
            "hashtags": [],
            "ctaText": "지금 바로 방문",
            "sceneText": {
                "hook": "오늘만 2천원 할인",
                "benefit": "세트 메뉴 바로 적용",
                "urgency": "이번 주 안에 반응 옵니다",
                "cta": "지금 바로 방문",
            },
            "subText": {
                "hook": "혜택 먼저",
                "benefit": "프로모션 설명",
                "urgency": "기간감 강조",
                "cta": "마감 CTA",
            },
        },
        processed_assets=processed_assets,
        storage_root=tmp_path,
    )
    assert [scene["sceneRole"] for scene in promotion_plan["scenes"]] == ["opening", "support", "support", "closing"]
    assert promotion_plan["scenes"][0]["renderHints"]["layoutHint"] == "offer_poster"
    assert promotion_plan["scenes"][-1]["renderHints"]["layoutHint"] == "cta_poster"

    review_plan = build_scene_plan(
        project={"business_type": "restaurant", "purpose": "review", "region_name": "성수동"},
        template=load_template(template_root, "T04"),
        style=load_style(template_root, "b_grade_fun"),
        copy_bundle={
            "hookText": "또 생각나는 한 그릇",
            "captions": ["후기형 문구", "라멘 소개", "CTA"],
            "hashtags": [],
            "ctaText": "오늘 저녁 메뉴로 저장",
            "sceneText": {
                "review_quote": "\"또 생각나는 라멘\"",
                "product_name": "국물 밸런스 좋은 라멘",
                "cta": "오늘 저녁 메뉴로 저장",
            },
            "subText": {
                "review_quote": "후기형 문구",
                "product_name": "라멘 소개",
                "cta": "CTA",
            },
        },
        processed_assets=processed_assets,
        storage_root=tmp_path,
    )
    assert [scene["sceneRole"] for scene in review_plan["scenes"]] == ["review", "review", "closing"]
    assert review_plan["scenes"][0]["renderHints"]["layoutHint"] == "review_poster"
    assert review_plan["scenes"][-1]["copy"]["cta"] == "오늘 저녁 메뉴로 저장"


def test_bgrade_scene_policy_matches_sample_class_baselines() -> None:
    template_root = Path(__file__).resolve().parents[3] / "packages" / "template-spec"
    repo_root = Path(__file__).resolve().parents[3]
    promotion_template = load_template(template_root, "T02")
    review_template = load_template(template_root, "T04")
    beer_path = repo_root / "docs" / "sample" / "음식사진샘플(맥주).jpg"
    gyukatsu_path = repo_root / "docs" / "sample" / "음식사진샘플(규카츠).jpg"
    coffee_path = repo_root / "docs" / "sample" / "음식사진샘플(커피).jpg"

    assert classify_shot_type(beer_path) == "glass_drink_candidate"
    assert choose_prepare_mode(beer_path) == "cover_bottom"
    assert classify_shot_type(gyukatsu_path) == "tray_full_plate"
    assert choose_prepare_mode(gyukatsu_path) == "cover_center"
    assert classify_shot_type(coffee_path) == "glass_drink_candidate"
    assert choose_prepare_mode(coffee_path) == "cover_top"
    assert classify_shot_type(repo_root / "docs" / "sample" / "음식사진샘플(라멘).jpg") == "preserve_shot"
    assert choose_prepare_mode(repo_root / "docs" / "sample" / "음식사진샘플(라멘).jpg") == "cover_center"

    assert _resolve_bgrade_scene_policy(beer_path, promotion_template["scenes"][0]) == {
        "shotType": "glass_drink_candidate",
        "prepareMode": "cover_bottom",
        "motionPreset": "push_in_bottom",
    }
    assert _resolve_bgrade_scene_policy(beer_path, promotion_template["scenes"][2]) == {
        "shotType": "glass_drink_candidate",
        "prepareMode": "cover_center",
        "motionPreset": "push_in_center",
    }
    assert _resolve_bgrade_scene_policy(gyukatsu_path, promotion_template["scenes"][2]) == {
        "shotType": "tray_full_plate",
        "prepareMode": "cover_top",
        "motionPreset": "push_in_top",
    }
    assert _resolve_bgrade_scene_policy(coffee_path, review_template["scenes"][0]) == {
        "shotType": "glass_drink_candidate",
        "prepareMode": "cover_top",
        "motionPreset": "push_in_top",
    }
    assert _resolve_bgrade_scene_policy(repo_root / "docs" / "sample" / "음식사진샘플(라멘).jpg", promotion_template["scenes"][0]) == {
        "shotType": "preserve_shot",
        "prepareMode": "cover_center",
        "motionPreset": "push_in_center",
    }
    assert _resolve_bgrade_scene_policy(repo_root / "docs" / "sample" / "음식사진샘플(라멘).jpg", promotion_template["scenes"][2]) == {
        "shotType": "preserve_shot",
        "prepareMode": "cover_top",
        "motionPreset": "push_in_top",
    }


def test_prompt_baseline_coverage_hint_matches_review_style_gap() -> None:
    template_root = Path(__file__).resolve().parents[3] / "packages" / "template-spec"
    summary = _build_prompt_baseline_summary(
        template_root,
        purpose="review",
        template_id="T04",
        style_id="friendly",
        quick_options={"highlightPrice": False, "shorterCopy": True, "emphasizeRegion": False},
        input_snapshot={},
    )

    assert summary is not None
    assert summary["recommendedProfile"] is None
    assert summary["coverageHint"]["nearestProfileId"] == "review_strict_fallback_surface_lock"
    assert summary["coverageHint"]["nearestProfileKind"] == "option"
    assert summary["coverageHint"]["mismatchDimensions"] == ["styleId"]
    assert summary["coverageHint"]["gapClass"] == "scenario_gap"
    assert summary["coverageHint"]["recommendedAction"] == "run_new_scenario_experiment"


def test_prompt_baseline_summary_matches_promotion_combined_region_anchor_profile() -> None:
    template_root = Path(__file__).resolve().parents[3] / "packages" / "template-spec"
    summary = _build_prompt_baseline_summary(
        template_root,
        purpose="promotion",
        template_id="T02",
        style_id="b_grade_fun",
        quick_options={"highlightPrice": False, "shorterCopy": False, "emphasizeRegion": True},
        input_snapshot={},
    )

    assert summary is not None
    assert summary["recommendedProfile"] is not None
    assert summary["recommendedProfile"]["profileId"] == "promotion_surface_lock_highlight_price_off_shorter_copy_off_region_anchor"
    assert summary["executionHint"]["status"] == "option_match"
    assert summary["executionHint"]["recommendedProfileId"] == "promotion_surface_lock_highlight_price_off_shorter_copy_off_region_anchor"
    assert summary["executionHint"]["transportRecommendation"]["fallbackProfileId"] == "timeout_90s_retry1"
    assert summary["coverageHint"] is None
    assert summary["policyHint"]["policyState"] == "option_reference"
    assert summary["policyHint"]["recommendedAction"] == "use_option_profile_reference"


def test_prompt_baseline_summary_matches_promotion_highlight_price_off_region_anchor_profile() -> None:
    template_root = Path(__file__).resolve().parents[3] / "packages" / "template-spec"
    summary = _build_prompt_baseline_summary(
        template_root,
        purpose="promotion",
        template_id="T02",
        style_id="b_grade_fun",
        quick_options={"highlightPrice": False, "shorterCopy": True, "emphasizeRegion": True},
        input_snapshot={},
    )

    assert summary is not None
    assert summary["recommendedProfile"] is not None
    assert summary["recommendedProfile"]["profileId"] == "promotion_surface_lock_highlight_price_off_region_anchor"
    assert summary["executionHint"]["status"] == "option_match"
    assert summary["executionHint"]["recommendedProfileId"] == "promotion_surface_lock_highlight_price_off_region_anchor"
    assert summary["executionHint"]["transportRecommendation"]["fallbackProfileId"] == "timeout_90s_retry1"
    assert summary["coverageHint"] is None
    assert summary["policyHint"]["policyState"] == "option_reference"
    assert summary["policyHint"]["recommendedAction"] == "use_option_profile_reference"


def test_prompt_baseline_summary_matches_promotion_shorter_copy_off_region_anchor_profile() -> None:
    template_root = Path(__file__).resolve().parents[3] / "packages" / "template-spec"
    summary = _build_prompt_baseline_summary(
        template_root,
        purpose="promotion",
        template_id="T02",
        style_id="b_grade_fun",
        quick_options={"highlightPrice": True, "shorterCopy": False, "emphasizeRegion": True},
        input_snapshot={},
    )

    assert summary is not None
    assert summary["recommendedProfile"] is not None
    assert summary["recommendedProfile"]["profileId"] == "promotion_surface_lock_shorter_copy_off_region_anchor"
    assert summary["executionHint"]["status"] == "option_match"
    assert summary["executionHint"]["recommendedProfileId"] == "promotion_surface_lock_shorter_copy_off_region_anchor"
    assert summary["executionHint"]["transportRecommendation"]["fallbackProfileId"] == "timeout_90s_retry1"
    assert summary["coverageHint"] is None
    assert summary["policyHint"]["policyState"] == "option_reference"
    assert summary["policyHint"]["recommendedAction"] == "use_option_profile_reference"


def test_prompt_baseline_summary_matches_promotion_region_anchor_profile() -> None:
    template_root = Path(__file__).resolve().parents[3] / "packages" / "template-spec"
    summary = _build_prompt_baseline_summary(
        template_root,
        purpose="promotion",
        template_id="T02",
        style_id="b_grade_fun",
        quick_options={"highlightPrice": True, "shorterCopy": True, "emphasizeRegion": True},
        input_snapshot={},
    )

    assert summary is not None
    assert summary["recommendedProfile"] is not None
    assert summary["recommendedProfile"]["profileId"] == "promotion_surface_lock_region_anchor"
    assert summary["executionHint"]["status"] == "option_match"
    assert summary["executionHint"]["recommendedProfileId"] == "promotion_surface_lock_region_anchor"
    assert summary["executionHint"]["transportRecommendation"]["fallbackProfileId"] == "timeout_90s_retry1"
    assert summary["coverageHint"] is None
    assert summary["policyHint"]["policyState"] == "option_reference"
    assert summary["policyHint"]["recommendedAction"] == "use_option_profile_reference"


def test_prompt_baseline_summary_matches_new_menu_shorter_copy_profile() -> None:
    template_root = Path(__file__).resolve().parents[3] / "packages" / "template-spec"
    summary = _build_prompt_baseline_summary(
        template_root,
        purpose="new_menu",
        template_id="T01",
        style_id="friendly",
        quick_options={"highlightPrice": False, "shorterCopy": True, "emphasizeRegion": True},
        input_snapshot={},
    )

    assert summary is not None
    assert summary["recommendedProfile"] is not None
    assert summary["recommendedProfile"]["profileId"] == "new_menu_friendly_region_anchor_shorter_copy"
    assert summary["executionHint"]["status"] == "option_match"
    assert summary["executionHint"]["recommendedProfileId"] == "new_menu_friendly_region_anchor_shorter_copy"
    assert summary["coverageHint"] is None
    assert summary["policyHint"]["policyState"] == "option_reference"
    assert summary["policyHint"]["recommendedAction"] == "use_option_profile_reference"


def test_prompt_baseline_summary_matches_new_menu_minimal_region_anchor_profile() -> None:
    template_root = Path(__file__).resolve().parents[3] / "packages" / "template-spec"
    summary = _build_prompt_baseline_summary(
        template_root,
        purpose="new_menu",
        template_id="T01",
        style_id="friendly",
        quick_options={"highlightPrice": False, "shorterCopy": False, "emphasizeRegion": False},
        input_snapshot={},
    )

    assert summary is not None
    assert summary["recommendedProfile"] is not None
    assert summary["recommendedProfile"]["profileId"] == "new_menu_friendly_minimal_region_anchor"
    assert summary["executionHint"]["status"] == "option_match"
    assert summary["executionHint"]["recommendedProfileId"] == "new_menu_friendly_minimal_region_anchor"
    assert summary["coverageHint"] is None
    assert summary["policyHint"]["policyState"] == "option_reference"
    assert summary["policyHint"]["recommendedAction"] == "use_option_profile_reference"


def test_prompt_baseline_summary_matches_new_menu_minimal_region_anchor_shorter_copy_profile() -> None:
    template_root = Path(__file__).resolve().parents[3] / "packages" / "template-spec"
    summary = _build_prompt_baseline_summary(
        template_root,
        purpose="new_menu",
        template_id="T01",
        style_id="friendly",
        quick_options={"highlightPrice": False, "shorterCopy": True, "emphasizeRegion": False},
        input_snapshot={},
    )

    assert summary is not None
    assert summary["recommendedProfile"] is not None
    assert summary["recommendedProfile"]["profileId"] == "new_menu_friendly_minimal_region_anchor_shorter_copy"
    assert summary["executionHint"]["status"] == "option_match"
    assert summary["executionHint"]["recommendedProfileId"] == "new_menu_friendly_minimal_region_anchor_shorter_copy"
    assert summary["coverageHint"] is None
    assert summary["policyHint"]["policyState"] == "option_reference"
    assert summary["policyHint"]["recommendedAction"] == "use_option_profile_reference"


def test_prompt_baseline_summary_matches_new_menu_minimal_region_anchor_highlight_price_profile() -> None:
    template_root = Path(__file__).resolve().parents[3] / "packages" / "template-spec"
    summary = _build_prompt_baseline_summary(
        template_root,
        purpose="new_menu",
        template_id="T01",
        style_id="friendly",
        quick_options={"highlightPrice": True, "shorterCopy": False, "emphasizeRegion": False},
        input_snapshot={},
    )

    assert summary is not None
    assert summary["recommendedProfile"] is not None
    assert summary["recommendedProfile"]["profileId"] == "new_menu_friendly_minimal_region_anchor_highlight_price"
    assert summary["executionHint"]["status"] == "option_match"
    assert summary["executionHint"]["recommendedProfileId"] == "new_menu_friendly_minimal_region_anchor_highlight_price"
    assert summary["coverageHint"] is None
    assert summary["policyHint"]["policyState"] == "option_reference"
    assert summary["policyHint"]["recommendedAction"] == "use_option_profile_reference"


def test_prompt_baseline_summary_matches_new_menu_minimal_region_anchor_highlight_price_shorter_copy_profile() -> None:
    template_root = Path(__file__).resolve().parents[3] / "packages" / "template-spec"
    summary = _build_prompt_baseline_summary(
        template_root,
        purpose="new_menu",
        template_id="T01",
        style_id="friendly",
        quick_options={"highlightPrice": True, "shorterCopy": True, "emphasizeRegion": False},
        input_snapshot={},
    )

    assert summary is not None
    assert summary["recommendedProfile"] is not None
    assert summary["recommendedProfile"]["profileId"] == "new_menu_friendly_minimal_region_anchor_highlight_price_shorter_copy"
    assert summary["executionHint"]["status"] == "option_match"
    assert summary["executionHint"]["recommendedProfileId"] == "new_menu_friendly_minimal_region_anchor_highlight_price_shorter_copy"
    assert summary["coverageHint"] is None
    assert summary["policyHint"]["policyState"] == "option_reference"
    assert summary["policyHint"]["recommendedAction"] == "use_option_profile_reference"


def test_prompt_baseline_summary_matches_new_menu_highlight_price_profile() -> None:
    template_root = Path(__file__).resolve().parents[3] / "packages" / "template-spec"
    summary = _build_prompt_baseline_summary(
        template_root,
        purpose="new_menu",
        template_id="T01",
        style_id="friendly",
        quick_options={"highlightPrice": True, "shorterCopy": False, "emphasizeRegion": True},
        input_snapshot={},
    )

    assert summary is not None
    assert summary["recommendedProfile"] is not None
    assert summary["recommendedProfile"]["profileId"] == "new_menu_friendly_region_anchor_highlight_price"
    assert summary["executionHint"]["status"] == "option_match"
    assert summary["executionHint"]["recommendedProfileId"] == "new_menu_friendly_region_anchor_highlight_price"
    assert summary["coverageHint"] is None
    assert summary["policyHint"]["policyState"] == "option_reference"
    assert summary["policyHint"]["recommendedAction"] == "use_option_profile_reference"


def test_prompt_baseline_summary_matches_new_menu_highlight_price_shorter_copy_profile() -> None:
    template_root = Path(__file__).resolve().parents[3] / "packages" / "template-spec"
    summary = _build_prompt_baseline_summary(
        template_root,
        purpose="new_menu",
        template_id="T01",
        style_id="friendly",
        quick_options={"highlightPrice": True, "shorterCopy": True, "emphasizeRegion": True},
        input_snapshot={},
    )

    assert summary is not None
    assert summary["recommendedProfile"] is not None
    assert summary["recommendedProfile"]["profileId"] == "new_menu_friendly_region_anchor_highlight_price_shorter_copy"
    assert summary["executionHint"]["status"] == "option_match"
    assert summary["executionHint"]["recommendedProfileId"] == "new_menu_friendly_region_anchor_highlight_price_shorter_copy"
    assert summary["coverageHint"] is None
    assert summary["policyHint"]["policyState"] == "option_reference"
    assert summary["policyHint"]["recommendedAction"] == "use_option_profile_reference"


def test_prompt_baseline_summary_matches_review_shorter_copy_off_profile() -> None:
    template_root = Path(__file__).resolve().parents[3] / "packages" / "template-spec"
    summary = _build_prompt_baseline_summary(
        template_root,
        purpose="review",
        template_id="T04",
        style_id="b_grade_fun",
        quick_options={"highlightPrice": False, "shorterCopy": False, "emphasizeRegion": False},
        input_snapshot={},
    )

    assert summary is not None
    assert summary["recommendedProfile"] is not None
    assert summary["recommendedProfile"]["profileId"] == "review_strict_fallback_surface_lock_shorter_copy_off"
    assert summary["executionHint"]["status"] == "option_match"
    assert summary["executionHint"]["recommendedProfileId"] == "review_strict_fallback_surface_lock_shorter_copy_off"
    assert summary["coverageHint"] is None
    assert summary["policyHint"]["policyState"] == "option_reference"
    assert summary["policyHint"]["recommendedAction"] == "use_option_profile_reference"


def test_prompt_baseline_summary_matches_review_region_anchor_profile() -> None:
    template_root = Path(__file__).resolve().parents[3] / "packages" / "template-spec"
    summary = _build_prompt_baseline_summary(
        template_root,
        purpose="review",
        template_id="T04",
        style_id="b_grade_fun",
        quick_options={"highlightPrice": False, "shorterCopy": True, "emphasizeRegion": True},
        input_snapshot={},
    )

    assert summary is not None
    assert summary["recommendedProfile"] is not None
    assert summary["recommendedProfile"]["profileId"] == "review_strict_fallback_surface_lock_region_anchor"
    assert summary["executionHint"]["status"] == "option_match"
    assert summary["executionHint"]["recommendedProfileId"] == "review_strict_fallback_surface_lock_region_anchor"
    assert summary["coverageHint"] is None
    assert summary["policyHint"]["policyState"] == "option_reference"
    assert summary["policyHint"]["recommendedAction"] == "use_option_profile_reference"


def test_prompt_baseline_summary_matches_review_shorter_copy_off_region_anchor_profile() -> None:
    template_root = Path(__file__).resolve().parents[3] / "packages" / "template-spec"
    summary = _build_prompt_baseline_summary(
        template_root,
        purpose="review",
        template_id="T04",
        style_id="b_grade_fun",
        quick_options={"highlightPrice": False, "shorterCopy": False, "emphasizeRegion": True},
        input_snapshot={},
    )

    assert summary is not None
    assert summary["recommendedProfile"] is not None
    assert summary["recommendedProfile"]["profileId"] == "review_strict_fallback_surface_lock_shorter_copy_off_region_anchor"
    assert summary["executionHint"]["status"] == "option_match"
    assert summary["executionHint"]["recommendedProfileId"] == "review_strict_fallback_surface_lock_shorter_copy_off_region_anchor"
    assert summary["coverageHint"] is None
    assert summary["policyHint"]["policyState"] == "option_reference"
    assert summary["policyHint"]["recommendedAction"] == "use_option_profile_reference"


def test_prompt_baseline_summary_matches_review_highlight_price_shorter_copy_off_profile() -> None:
    template_root = Path(__file__).resolve().parents[3] / "packages" / "template-spec"
    summary = _build_prompt_baseline_summary(
        template_root,
        purpose="review",
        template_id="T04",
        style_id="b_grade_fun",
        quick_options={"highlightPrice": True, "shorterCopy": False, "emphasizeRegion": False},
        input_snapshot={},
    )

    assert summary is not None
    assert summary["recommendedProfile"] is not None
    assert summary["recommendedProfile"]["profileId"] == "review_strict_fallback_surface_lock_highlight_price_shorter_copy_off"
    assert summary["executionHint"]["status"] == "option_match"
    assert summary["executionHint"]["recommendedProfileId"] == "review_strict_fallback_surface_lock_highlight_price_shorter_copy_off"
    assert summary["coverageHint"] is None
    assert summary["policyHint"]["policyState"] == "option_reference"
    assert summary["policyHint"]["recommendedAction"] == "use_option_profile_reference"


def test_prompt_baseline_summary_matches_review_highlight_price_shorter_copy_off_region_anchor_profile() -> None:
    template_root = Path(__file__).resolve().parents[3] / "packages" / "template-spec"
    summary = _build_prompt_baseline_summary(
        template_root,
        purpose="review",
        template_id="T04",
        style_id="b_grade_fun",
        quick_options={"highlightPrice": True, "shorterCopy": False, "emphasizeRegion": True},
        input_snapshot={},
    )

    assert summary is not None
    assert summary["recommendedProfile"] is not None
    assert summary["recommendedProfile"]["profileId"] == "review_strict_fallback_surface_lock_highlight_price_shorter_copy_off_region_anchor"
    assert summary["executionHint"]["status"] == "option_match"
    assert summary["executionHint"]["recommendedProfileId"] == "review_strict_fallback_surface_lock_highlight_price_shorter_copy_off_region_anchor"
    assert summary["coverageHint"] is None
    assert summary["policyHint"]["policyState"] == "option_reference"
    assert summary["policyHint"]["recommendedAction"] == "use_option_profile_reference"


def test_prompt_baseline_summary_matches_review_highlight_price_profile() -> None:
    template_root = Path(__file__).resolve().parents[3] / "packages" / "template-spec"
    summary = _build_prompt_baseline_summary(
        template_root,
        purpose="review",
        template_id="T04",
        style_id="b_grade_fun",
        quick_options={"highlightPrice": True, "shorterCopy": True, "emphasizeRegion": False},
        input_snapshot={},
    )

    assert summary is not None
    assert summary["recommendedProfile"] is not None
    assert summary["recommendedProfile"]["profileId"] == "review_strict_fallback_surface_lock_highlight_price"
    assert summary["executionHint"]["status"] == "option_match"
    assert summary["executionHint"]["recommendedProfileId"] == "review_strict_fallback_surface_lock_highlight_price"
    assert summary["coverageHint"] is None
    assert summary["policyHint"]["policyState"] == "option_reference"
    assert summary["policyHint"]["recommendedAction"] == "use_option_profile_reference"


def test_prompt_baseline_summary_matches_review_highlight_price_region_anchor_profile() -> None:
    template_root = Path(__file__).resolve().parents[3] / "packages" / "template-spec"
    summary = _build_prompt_baseline_summary(
        template_root,
        purpose="review",
        template_id="T04",
        style_id="b_grade_fun",
        quick_options={"highlightPrice": True, "shorterCopy": True, "emphasizeRegion": True},
        input_snapshot={},
    )

    assert summary is not None
    assert summary["recommendedProfile"] is not None
    assert summary["recommendedProfile"]["profileId"] == "review_strict_fallback_surface_lock_highlight_price_region_anchor"
    assert summary["executionHint"]["status"] == "option_match"
    assert summary["executionHint"]["recommendedProfileId"] == "review_strict_fallback_surface_lock_highlight_price_region_anchor"
    assert summary["coverageHint"] is None
    assert summary["policyHint"]["policyState"] == "option_reference"
    assert summary["policyHint"]["recommendedAction"] == "use_option_profile_reference"
