from __future__ import annotations

import io
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient
from PIL import Image


def make_png_bytes(color: tuple[int, int, int]) -> bytes:
    image = Image.new("RGB", (1200, 1600), color)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def create_promoted_hybrid_decision_artifacts(base_dir: Path) -> tuple[Path, str]:
    from services.worker.renderers.media import render_video

    source_dir = base_dir / "approved-hybrid-source"
    source_dir.mkdir(parents=True, exist_ok=True)
    frame_path = source_dir / "source-frame.png"
    Image.new("RGB", (720, 1280), (196, 88, 52)).save(frame_path)

    source_video_path = source_dir / "approved-source.mp4"
    render_video([(frame_path, 1.4)], source_video_path)

    contact_sheet_path = source_dir / "contact-sheet.png"
    Image.new("RGB", (720, 1280), (210, 210, 210)).save(contact_sheet_path)
    summary_path = source_dir / "summary.json"
    summary_path.write_text(json.dumps({"status": "completed"}, ensure_ascii=False), encoding="utf-8")

    candidate_key = "EXP-253-approved-hybrid-source-api-path::테스트라떼::approved_demo"
    decision_root = base_dir / "manual-review-decisions"
    decision_dir = decision_root / "EXP-253-approved-demo"
    decision_dir.mkdir(parents=True, exist_ok=True)
    decision = {
        "candidateKey": candidate_key,
        "reviewer": "codex",
        "decidedAt": "2026-04-14T16:30:00+09:00",
        "finalDecision": "promote",
        "summaryNote": "API generate 경로에서 승인된 hybrid source를 재사용할 수 있도록 승격된 후보로 등록했습니다.",
        "statusCounts": {"pass": 5},
        "packet": {
            "candidateKey": candidate_key,
            "benchmarkId": "EXP-253-approved-hybrid-source-api-path",
            "label": "테스트라떼",
            "provider": "approved_demo",
            "decision": "manual_review",
            "gateReason": "approved_for_api_baseline_reuse",
            "reviewCategory": "promotion_candidate",
            "recommendedAction": "promote_for_api_generation_path",
            "sourceVideoPath": str(source_video_path),
            "contactSheetPath": str(contact_sheet_path),
            "summaryPath": str(summary_path),
            "midFrameMse": 0.0,
            "motionAvgRgbDiff": 12.5,
        },
    }
    (decision_dir / "decision.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")
    return decision_root, candidate_key


def create_approved_hybrid_inventory_report(base_dir: Path) -> Path:
    report_path = base_dir / "approved-hybrid-inventory-report.json"
    report = {
        "experimentId": "EXP-255-approved-hybrid-inventory-api-read-path",
        "items": [
            {
                "candidateKey": "EXP-238::맥주::sora2_current_best",
                "serviceLane": "drink_glass_lane",
                "approvalSource": "benchmark_accept",
                "selectionMode": "benchmark_gate",
                "benchmarkId": "EXP-238",
                "label": "맥주",
                "provider": "sora2_current_best",
                "gateDecision": "accept",
                "gateReason": "eligible_for_hybrid_packaging_lane",
                "role": "hybrid_source_candidate",
                "midFrameMse": 2898.03,
                "motionAvgRgbDiff": 7.91,
            },
            {
                "candidateKey": "EXP-239::규카츠::sora2_current_best",
                "serviceLane": "tray_full_plate_lane",
                "approvalSource": "manual_review_promote",
                "selectionMode": "promoted_manual_review",
                "benchmarkId": "EXP-239",
                "label": "규카츠",
                "provider": "sora2_current_best",
                "gateDecision": "manual_review",
                "gateReason": "motion_is_usable_but_identity_review_is_needed",
                "role": "hybrid_source_candidate",
                "midFrameMse": 3545.57,
                "motionAvgRgbDiff": 21.04,
                "reviewFinalDecision": "promote",
            },
        ],
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report_path


def create_generated_project(client: TestClient) -> tuple[str, dict]:
    create_response = client.post(
        "/api/projects",
        json={
            "businessType": "cafe",
            "regionName": "성수동",
            "detailLocation": "서울숲 근처",
            "purpose": "new_menu",
            "style": "friendly",
            "channels": ["instagram"],
        },
    )
    assert create_response.status_code == 201
    project_id = create_response.json()["projectId"]

    upload_response = client.post(
        f"/api/projects/{project_id}/assets",
        files=[
            ("files", ("asset-1.png", make_png_bytes((220, 120, 80)), "image/png")),
            ("files", ("asset-2.png", make_png_bytes((80, 130, 220)), "image/png")),
        ],
    )
    assert upload_response.status_code == 201
    asset_ids = [asset["assetId"] for asset in upload_response.json()["assets"]]

    detail_response = client.get(f"/api/projects/{project_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["assetCount"] == 2
    assert "project" not in detail_response.json()

    asset_list_response = client.get(f"/api/projects/{project_id}/assets")
    assert asset_list_response.status_code == 200
    assert len(asset_list_response.json()["assets"]) == 2

    generate_response = client.post(
        f"/api/projects/{project_id}/generate",
        json={"assetIds": asset_ids, "templateId": "T01", "quickOptions": {"emphasizeRegion": True}},
    )
    assert generate_response.status_code == 202

    result_response = client.get(f"/api/projects/{project_id}/result")
    assert result_response.status_code == 200
    return project_id, result_response.json()


def test_auth_register_login_me_and_invalid_cases(monkeypatch, tmp_path):
    runtime_dir = tmp_path / ".runtime"
    monkeypatch.setenv("APP_RUNTIME_DIR", str(runtime_dir))
    monkeypatch.setenv("APP_STORAGE_DIR", str(runtime_dir / "storage"))
    monkeypatch.setenv("APP_DB_PATH", str(runtime_dir / "app.sqlite3"))

    from app.core.config import get_settings

    get_settings.cache_clear()

    from app.main import app

    client = TestClient(app)

    register_response = client.post(
        "/api/auth/register",
        json={
            "email": "owner@example.com",
            "password": "secret123!A",
            "name": "임창현",
            "birthDate": "1990-01-01",
            "agreedToTerms": True,
            "agreedToPrivacy": True,
            "agreedToAge14": True,
            "agreedToOverseasTransfer": True,
        },
    )
    assert register_response.status_code == 201
    register_payload = register_response.json()
    assert register_payload["user"]["email"] == "owner@example.com"
    assert register_payload["accessToken"]

    me_response = client.get(
        "/api/me",
        headers={"Authorization": f"Bearer {register_payload['accessToken']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["name"] == "임창현"

    invalid_login_response = client.post(
        "/api/auth/login",
        json={
            "email": "owner@example.com",
            "password": "wrong-passwordXXX",
        },
    )
    assert invalid_login_response.status_code == 401
    assert invalid_login_response.json()["error"]["code"] == "INVALID_CREDENTIALS"

    invalid_token_response = client.get(
        "/api/me",
        headers={"Authorization": "Bearer malformed.token"},
    )
    assert invalid_token_response.status_code == 401
    assert invalid_token_response.json()["error"]["code"] == "AUTH_REQUIRED"


def test_demo_login_available(monkeypatch, tmp_path):
    runtime_dir = tmp_path / ".runtime"
    monkeypatch.setenv("APP_RUNTIME_DIR", str(runtime_dir))
    monkeypatch.setenv("APP_STORAGE_DIR", str(runtime_dir / "storage"))
    monkeypatch.setenv("APP_DB_PATH", str(runtime_dir / "app.sqlite3"))

    from app.core.config import get_settings

    get_settings.cache_clear()

    from app.main import app

    client = TestClient(app)

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "demo-owner@example.com",
            "password": "secret123!",
        },
    )
    assert login_response.status_code == 200
    payload = login_response.json()
    assert payload["user"]["email"] == "demo-owner@example.com"
    assert payload["accessToken"]


def test_phase1_smoke(monkeypatch, tmp_path):
    runtime_dir = tmp_path / ".runtime"
    monkeypatch.setenv("APP_RUNTIME_DIR", str(runtime_dir))
    monkeypatch.setenv("APP_STORAGE_DIR", str(runtime_dir / "storage"))
    monkeypatch.setenv("APP_DB_PATH", str(runtime_dir / "app.sqlite3"))

    from app.core.config import get_settings

    get_settings.cache_clear()

    from app.main import app

    client = TestClient(app)
    project_id, result_payload = create_generated_project(client)

    status_response = client.get(f"/api/projects/{project_id}/status")
    assert status_response.status_code == 200
    status_payload = status_response.json()
    assert status_payload["projectStatus"] == "generated"
    assert all(step["status"] == "completed" for step in status_payload["steps"])
    assert result_payload["video"]["url"].endswith("video.mp4")
    assert result_payload["post"]["url"].endswith("post.png")
    assert len(result_payload["copySet"]["captions"]) == 3
    assert result_payload["scenePlan"]["url"].endswith("scene-plan.json")
    assert result_payload["scenePlan"]["sceneCount"] >= 3
    assert result_payload["sceneLayerSummary"]["templateId"] == "T01"
    assert len(result_payload["sceneLayerSummary"]["items"]) == 4
    assert result_payload["changeImpactSummary"]["runType"] == "initial"
    assert result_payload["changeImpactSummary"]["activeActions"][0]["actionId"] == "emphasizeRegion"
    assert "hook" in result_payload["changeImpactSummary"]["impactLayers"]
    assert result_payload["copyPolicy"]["detailLocationPolicyId"] == "strict_all_surfaces"
    assert result_payload["copyPolicy"]["guardActive"] is True
    assert result_payload["copyPolicy"]["detailLocationPresent"] is True
    assert result_payload["copyPolicy"]["emphasizeRegionRequested"] is True
    assert result_payload["copyDeck"]["templateId"] == "T01"
    assert result_payload["copyGeneration"]["sourceMode"] == "deterministic_rule"
    assert result_payload["copyGeneration"]["provider"] == "local_rule"
    assert result_payload["copyDeck"]["hook"]["primaryLine"]
    assert len(result_payload["copyDeck"]["body"]["blocks"]) == 2
    assert result_payload["copyDeck"]["cta"]["primaryLine"]
    assert result_payload["promptBaselineSummary"]["baselineId"] == "PB-001"
    assert result_payload["promptBaselineSummary"]["defaultProfile"]["profileId"] == "main_baseline"
    assert result_payload["promptBaselineSummary"]["recommendedProfile"]["profileId"] == "new_menu_friendly_strict_region_anchor"
    assert len(result_payload["promptBaselineSummary"]["candidateProfiles"]) >= 1
    assert result_payload["promptBaselineSummary"]["executionHint"]["status"] == "option_match"
    assert result_payload["promptBaselineSummary"]["executionHint"]["recommendedProfileId"] == "new_menu_friendly_strict_region_anchor"
    assert result_payload["promptBaselineSummary"]["coverageHint"] is None
    assert result_payload["promptBaselineSummary"]["policyHint"]["policyState"] == "option_reference"
    assert result_payload["promptBaselineSummary"]["policyHint"]["recommendedAction"] == "use_option_profile_reference"
    assert result_payload["promptBaselineSummary"]["policyHint"]["requiresManualReview"] is False
    assert len(result_payload["promptBaselineSummary"]["operationalChecks"]) >= 1
    assert result_payload["rendererSummary"]["videoSourceMode"] == "scene_image_render"
    assert result_payload["rendererSummary"]["motionMode"] == "static_concat"
    assert result_payload["rendererSummary"]["framingMode"] == "preprocessed_vertical"
    assert result_payload["rendererSummary"]["durationStrategy"] is None

    publish_response = client.post(
        f"/api/projects/{project_id}/publish",
        json={
            "variantId": result_payload["variantId"],
            "channel": "instagram",
            "publishMode": "auto",
            "captionOverride": result_payload["copySet"]["captions"][0],
            "hashtags": result_payload["copySet"]["hashtags"],
        },
    )
    assert publish_response.status_code == 202
    upload_job_id = publish_response.json()["uploadJobId"]

    upload_job_response = client.get(f"/api/upload-jobs/{upload_job_id}")
    assert upload_job_response.status_code == 200
    assert upload_job_response.json()["status"] == "published"

    media_root = runtime_dir / "storage" / "projects" / project_id
    assert any(path.name == "video.mp4" for path in media_root.rglob("video.mp4"))
    assert any(path.name == "post.png" for path in media_root.rglob("post.png"))


def test_generate_with_approved_hybrid_source_candidate(monkeypatch, tmp_path):
    runtime_dir = tmp_path / ".runtime"
    decisions_root, candidate_key = create_promoted_hybrid_decision_artifacts(tmp_path)
    monkeypatch.setenv("APP_RUNTIME_DIR", str(runtime_dir))
    monkeypatch.setenv("APP_STORAGE_DIR", str(runtime_dir / "storage"))
    monkeypatch.setenv("APP_DB_PATH", str(runtime_dir / "app.sqlite3"))
    monkeypatch.setenv("APP_MANUAL_REVIEW_DECISIONS_DIR", str(decisions_root))

    from app.core.config import get_settings

    get_settings.cache_clear()

    from app.core.database import get_connection
    from app.main import app

    client = TestClient(app)

    create_response = client.post(
        "/api/projects",
        json={
            "businessType": "restaurant",
            "regionName": "성수동",
            "detailLocation": "서울숲 근처",
            "purpose": "promotion",
            "style": "b_grade_fun",
            "channels": ["instagram"],
        },
    )
    assert create_response.status_code == 201
    project_id = create_response.json()["projectId"]

    upload_response = client.post(
        f"/api/projects/{project_id}/assets",
        files=[("files", ("asset-1.png", make_png_bytes((196, 88, 52)), "image/png"))],
    )
    assert upload_response.status_code == 201
    asset_ids = [asset["assetId"] for asset in upload_response.json()["assets"]]

    generate_response = client.post(
        f"/api/projects/{project_id}/generate",
        json={
            "assetIds": asset_ids,
            "templateId": "T02",
            "approvedHybridSourceCandidateKey": candidate_key,
        },
    )
    assert generate_response.status_code == 202

    result_response = client.get(f"/api/projects/{project_id}/result")
    assert result_response.status_code == 200
    result_payload = result_response.json()
    assert result_payload["rendererSummary"]["videoSourceMode"] == "hybrid_generated_clip"
    assert result_payload["rendererSummary"]["motionMode"] == "hybrid_overlay_packaging"
    assert result_payload["rendererSummary"]["framingMode"] == "hybrid_source_video"
    assert result_payload["rendererSummary"]["hybridSourceSelectionMode"] == "promoted_manual_review"
    assert result_payload["rendererSummary"]["hybridSourceCandidateKey"] == candidate_key

    with get_connection() as connection:
        run_id = generate_response.json()["generationRunId"]
        run = connection.execute("SELECT input_snapshot_json FROM generation_runs WHERE id = ?", (run_id,)).fetchone()
        assert run is not None
        input_snapshot = json.loads(run["input_snapshot_json"])

    assert input_snapshot["approvedHybridSourceCandidateKey"] == candidate_key
    assert input_snapshot["hybridSourceSelection"]["selectionMode"] == "promoted_manual_review"
    assert input_snapshot["hybridSourceSelection"]["reviewFinalDecision"] == "promote"
    assert input_snapshot["hybridSourceSelection"]["candidateKey"] == candidate_key
    staged_hybrid_path = runtime_dir / "storage" / input_snapshot["hybridSourceVideoPath"].lstrip("/").replace("/", "\\")
    assert staged_hybrid_path.exists()


def test_list_approved_hybrid_inventory(monkeypatch, tmp_path):
    runtime_dir = tmp_path / ".runtime"
    inventory_report_path = create_approved_hybrid_inventory_report(tmp_path)
    monkeypatch.setenv("APP_RUNTIME_DIR", str(runtime_dir))
    monkeypatch.setenv("APP_STORAGE_DIR", str(runtime_dir / "storage"))
    monkeypatch.setenv("APP_DB_PATH", str(runtime_dir / "app.sqlite3"))
    monkeypatch.setenv("APP_APPROVED_HYBRID_INVENTORY_REPORT_PATH", str(inventory_report_path))

    from app.core.config import get_settings

    get_settings.cache_clear()

    from app.main import app

    client = TestClient(app)

    response = client.get("/api/hybrid-candidates/approved")
    assert response.status_code == 200
    payload = response.json()
    assert payload["itemCount"] == 2
    assert payload["laneCounts"] == {"drink_glass_lane": 1, "tray_full_plate_lane": 1}
    assert payload["approvalSourceCounts"] == {"benchmark_accept": 1, "manual_review_promote": 1}
    assert payload["recommendedByLane"]["drink_glass_lane"]["candidateKey"] == "EXP-238::맥주::sora2_current_best"
    assert payload["recommendedByLane"]["tray_full_plate_lane"]["candidateKey"] == "EXP-239::규카츠::sora2_current_best"

    tray_only_response = client.get("/api/hybrid-candidates/approved?serviceLane=tray_full_plate_lane")
    assert tray_only_response.status_code == 200
    tray_payload = tray_only_response.json()
    assert tray_payload["itemCount"] == 1
    assert tray_payload["items"][0]["label"] == "규카츠"
    assert tray_payload["recommendedByLabel"]["규카츠"]["approvalSource"] == "manual_review_promote"


def test_social_callback_validation_and_expired_publish(monkeypatch, tmp_path):
    runtime_dir = tmp_path / ".runtime"
    monkeypatch.setenv("APP_RUNTIME_DIR", str(runtime_dir))
    monkeypatch.setenv("APP_STORAGE_DIR", str(runtime_dir / "storage"))
    monkeypatch.setenv("APP_DB_PATH", str(runtime_dir / "app.sqlite3"))

    from app.core.config import get_settings

    get_settings.cache_clear()

    from app.core.database import get_connection, utc_now
    from app.main import app

    client = TestClient(app)

    invalid_callback = client.get("/api/social-accounts/instagram/callback?code=demo-code&state=wrong-state")
    assert invalid_callback.status_code == 400
    assert invalid_callback.json()["error"]["code"] == "OAUTH_CALLBACK_INVALID"

    connect_response = client.post("/api/social-accounts/instagram/connect")
    assert connect_response.status_code == 200
    parsed = urlparse(connect_response.json()["redirectUrl"])
    query = parse_qs(parsed.query)

    callback_response = client.get(
        f"/api/social-accounts/instagram/callback?code={query['code'][0]}&state={query['state'][0]}"
    )
    assert callback_response.status_code == 200
    assert callback_response.json()["status"] == "connected"

    project_id, result_payload = create_generated_project(client)

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE social_accounts
            SET status = 'connected', token_expires_at = ?, updated_at = ?
            WHERE channel = 'instagram'
            """,
            ("2000-01-01T00:00:00+00:00", utc_now()),
        )

    publish_response = client.post(
        f"/api/projects/{project_id}/publish",
        json={
            "variantId": result_payload["variantId"],
            "channel": "instagram",
            "publishMode": "auto",
            "captionOverride": result_payload["copySet"]["captions"][0],
            "hashtags": result_payload["copySet"]["hashtags"],
        },
    )
    assert publish_response.status_code == 202
    assert publish_response.json()["status"] == "assist_required"

    upload_job_id = publish_response.json()["uploadJobId"]
    upload_job_response = client.get(f"/api/upload-jobs/{upload_job_id}")
    assert upload_job_response.status_code == 200
    assert upload_job_response.json()["error"]["code"] == "SOCIAL_TOKEN_EXPIRED"

    social_accounts_response = client.get("/api/social-accounts")
    instagram_account = next(item for item in social_accounts_response.json()["items"] if item["channel"] == "instagram")
    assert instagram_account["status"] == "expired"


def test_publish_assist_flow_and_permission_error(monkeypatch, tmp_path):
    runtime_dir = tmp_path / ".runtime"
    monkeypatch.setenv("APP_RUNTIME_DIR", str(runtime_dir))
    monkeypatch.setenv("APP_STORAGE_DIR", str(runtime_dir / "storage"))
    monkeypatch.setenv("APP_DB_PATH", str(runtime_dir / "app.sqlite3"))

    from app.core.config import get_settings

    get_settings.cache_clear()

    from app.main import app

    client = TestClient(app)
    project_id, result_payload = create_generated_project(client)

    youtube_connect_response = client.post("/api/social-accounts/youtube_shorts/connect")
    assert youtube_connect_response.status_code == 200
    youtube_parsed = urlparse(youtube_connect_response.json()["redirectUrl"])
    youtube_query = parse_qs(youtube_parsed.query)
    youtube_callback_response = client.get(
        f"/api/social-accounts/youtube_shorts/callback?code={youtube_query['code'][0]}&state={youtube_query['state'][0]}"
    )
    assert youtube_callback_response.status_code == 200
    assert youtube_callback_response.json()["status"] == "connected"

    youtube_publish_response = client.post(
        f"/api/projects/{project_id}/publish",
        json={
            "variantId": result_payload["variantId"],
            "channel": "youtube_shorts",
            "publishMode": "auto",
            "captionOverride": result_payload["copySet"]["captions"][0],
            "hashtags": result_payload["copySet"]["hashtags"],
            "thumbnailText": "모바일 점검",
        },
    )
    assert youtube_publish_response.status_code == 202
    assert youtube_publish_response.json()["status"] == "assist_required"
    assert youtube_publish_response.json()["assistPackage"]["thumbnailText"] == "모바일 점검"

    upload_job_id = youtube_publish_response.json()["uploadJobId"]
    upload_job_response = client.get(f"/api/upload-jobs/{upload_job_id}")
    assert upload_job_response.status_code == 200
    assert upload_job_response.json()["status"] == "assist_required"
    assert upload_job_response.json()["error"]["code"] == "PUBLISH_FAILED"

    assist_complete_response = client.post(f"/api/upload-jobs/{upload_job_id}/assist-complete")
    assert assist_complete_response.status_code == 200
    assert assist_complete_response.json()["status"] == "assisted_completed"

    project_detail_response = client.get(f"/api/projects/{project_id}")
    assert project_detail_response.status_code == 200
    assert project_detail_response.json()["status"] == "published"

    connect_response = client.post("/api/social-accounts/instagram/connect")
    assert connect_response.status_code == 200
    parsed = urlparse(connect_response.json()["redirectUrl"])
    query = parse_qs(parsed.query)

    permission_callback = client.get(
        f"/api/social-accounts/instagram/callback?code=permission-error&state={query['state'][0]}"
    )
    assert permission_callback.status_code == 400
    assert permission_callback.json()["error"]["code"] == "OAUTH_CALLBACK_INVALID"

    project_id_2, result_payload_2 = create_generated_project(client)
    permission_publish_response = client.post(
        f"/api/projects/{project_id_2}/publish",
        json={
            "variantId": result_payload_2["variantId"],
            "channel": "instagram",
            "publishMode": "auto",
            "captionOverride": result_payload_2["copySet"]["captions"][0],
            "hashtags": result_payload_2["copySet"]["hashtags"],
        },
    )
    assert permission_publish_response.status_code == 202
    assert permission_publish_response.json()["status"] == "assist_required"

    permission_job_id = permission_publish_response.json()["uploadJobId"]
    permission_job_response = client.get(f"/api/upload-jobs/{permission_job_id}")
    assert permission_job_response.status_code == 200
    assert permission_job_response.json()["error"]["code"] == "PUBLISH_FAILED"


def test_publish_rejects_stale_variant_after_regenerate(monkeypatch, tmp_path):
    runtime_dir = tmp_path / ".runtime"
    monkeypatch.setenv("APP_RUNTIME_DIR", str(runtime_dir))
    monkeypatch.setenv("APP_STORAGE_DIR", str(runtime_dir / "storage"))
    monkeypatch.setenv("APP_DB_PATH", str(runtime_dir / "app.sqlite3"))

    from app.core.config import get_settings

    get_settings.cache_clear()

    from app.main import app

    client = TestClient(app)
    project_id, baseline_result = create_generated_project(client)

    regenerate_response = client.post(
        f"/api/projects/{project_id}/regenerate",
        json={"changeSet": {"shorterCopy": True}},
    )
    assert regenerate_response.status_code == 202

    regenerated_result_response = client.get(f"/api/projects/{project_id}/result")
    assert regenerated_result_response.status_code == 200
    regenerated_result = regenerated_result_response.json()
    assert regenerated_result["variantId"] != baseline_result["variantId"]

    stale_publish_response = client.post(
        f"/api/projects/{project_id}/publish",
        json={
            "variantId": baseline_result["variantId"],
            "channel": "youtube_shorts",
            "publishMode": "assist",
            "captionOverride": baseline_result["copySet"]["captions"][0],
            "hashtags": baseline_result["copySet"]["hashtags"],
        },
    )
    assert stale_publish_response.status_code == 422
    assert stale_publish_response.json()["error"]["code"] == "INVALID_STATE_TRANSITION"

    fresh_publish_response = client.post(
        f"/api/projects/{project_id}/publish",
        json={
            "variantId": regenerated_result["variantId"],
            "channel": "youtube_shorts",
            "publishMode": "assist",
            "captionOverride": regenerated_result["copySet"]["captions"][0],
            "hashtags": regenerated_result["copySet"]["hashtags"],
        },
    )
    assert fresh_publish_response.status_code == 202
    assert fresh_publish_response.json()["status"] == "assist_required"


def test_publish_rejects_cross_project_variant(monkeypatch, tmp_path):
    runtime_dir = tmp_path / ".runtime"
    monkeypatch.setenv("APP_RUNTIME_DIR", str(runtime_dir))
    monkeypatch.setenv("APP_STORAGE_DIR", str(runtime_dir / "storage"))
    monkeypatch.setenv("APP_DB_PATH", str(runtime_dir / "app.sqlite3"))

    from app.core.config import get_settings

    get_settings.cache_clear()

    from app.main import app

    client = TestClient(app)
    project_id_1, result_payload_1 = create_generated_project(client)
    project_id_2, result_payload_2 = create_generated_project(client)

    cross_publish_response = client.post(
        f"/api/projects/{project_id_2}/publish",
        json={
            "variantId": result_payload_1["variantId"],
            "channel": "youtube_shorts",
            "publishMode": "assist",
            "captionOverride": result_payload_1["copySet"]["captions"][0],
            "hashtags": result_payload_1["copySet"]["hashtags"],
        },
    )
    assert cross_publish_response.status_code == 422
    assert cross_publish_response.json()["error"]["code"] == "INVALID_STATE_TRANSITION"

    own_publish_response = client.post(
        f"/api/projects/{project_id_2}/publish",
        json={
            "variantId": result_payload_2["variantId"],
            "channel": "youtube_shorts",
            "publishMode": "assist",
            "captionOverride": result_payload_2["copySet"]["captions"][0],
            "hashtags": result_payload_2["copySet"]["hashtags"],
        },
    )
    assert own_publish_response.status_code == 202
    assert own_publish_response.json()["status"] == "assist_required"
