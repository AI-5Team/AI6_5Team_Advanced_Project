from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from PIL import Image, ImageFilter, ImageStat

from datetime import date

from app.core.config import get_settings
from app.core.database import get_connection, utc_now
from app.core.errors import api_error
from app.core.security import hash_password, verify_password
from app.services.audit import log_event
from app.services.consent import record_signup_consents
from app.services.crypto import encrypt_token
from app.services.session import issue_session, revoke_session_by_token, verify_session
from app.services.token_svc import consume_token, issue_email_verify, issue_password_reset
from services.worker.pipelines.generation import run_generation_job
from services.worker.pipelines.publish import run_publish_job


DEMO_EMAIL = "demo-owner@example.com"
DEMO_PASSWORD = "secret123!"
CHANNEL_TIERS = {
    "instagram": "ready",
    "youtube_shorts": "experimental",
    "tiktok": "experimental",
}
STEP_NAMES = [
    "preprocessing",
    "copy_generation",
    "video_rendering",
    "post_rendering",
    "packaging",
]


def _utc_now_dt() -> datetime:
    return datetime.now(timezone.utc)


def _supported_channel(channel: str) -> None:
    if channel not in CHANNEL_TIERS:
        raise api_error(400, "UNSUPPORTED_CHANNEL", "지원하지 않는 채널입니다.")


def _is_token_expired(value: str | None) -> bool:
    if not value:
        return False
    try:
        expires_at = datetime.fromisoformat(value)
    except ValueError:
        return False
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at <= _utc_now_dt()


def _settings():
    return get_settings()


def _json_loads(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        return json.loads(value)
    return value


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _select_recommended_item(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not items:
        return None

    def sort_key(item: dict[str, Any]) -> tuple[int, float, float, str]:
        selection_mode = str(item.get("selectionMode") or "")
        selection_rank = 0 if selection_mode == "benchmark_gate" else 1
        return (
            selection_rank,
            -float(item.get("motionAvgRgbDiff") or 0.0),
            float(item.get("midFrameMse") or 0.0),
            str(item.get("provider") or ""),
        )

    return sorted(items, key=sort_key)[0]


def _build_inventory_view(report: dict[str, Any], *, label: str | None = None, service_lane: str | None = None) -> dict[str, Any]:
    items = report.get("items")
    filtered_items = [item for item in items if isinstance(item, dict)] if isinstance(items, list) else []
    if label:
        filtered_items = [item for item in filtered_items if str(item.get("label") or "") == label]
    if service_lane:
        filtered_items = [item for item in filtered_items if str(item.get("serviceLane") or "") == service_lane]

    lane_counts: dict[str, int] = {}
    label_counts: dict[str, int] = {}
    approval_source_counts: dict[str, int] = {}
    recommended_by_lane: dict[str, Any] = {}
    recommended_by_label: dict[str, Any] = {}

    grouped_by_lane: dict[str, list[dict[str, Any]]] = {}
    grouped_by_label: dict[str, list[dict[str, Any]]] = {}
    for item in filtered_items:
        lane = str(item.get("serviceLane") or "")
        current_label = str(item.get("label") or "")
        approval_source = str(item.get("approvalSource") or "")
        lane_counts[lane] = lane_counts.get(lane, 0) + 1
        label_counts[current_label] = label_counts.get(current_label, 0) + 1
        approval_source_counts[approval_source] = approval_source_counts.get(approval_source, 0) + 1
        grouped_by_lane.setdefault(lane, []).append(item)
        grouped_by_label.setdefault(current_label, []).append(item)

    for lane, lane_items in grouped_by_lane.items():
        recommended = _select_recommended_item(lane_items)
        if recommended is not None:
            recommended_by_lane[lane] = recommended
    for current_label, label_items in grouped_by_label.items():
        recommended = _select_recommended_item(label_items)
        if recommended is not None:
            recommended_by_label[current_label] = recommended

    return {
        "itemCount": len(filtered_items),
        "laneCounts": lane_counts,
        "labelCounts": label_counts,
        "approvalSourceCounts": approval_source_counts,
        "recommendedByLane": recommended_by_lane,
        "recommendedByLabel": recommended_by_label,
        "items": filtered_items,
    }


def get_approved_hybrid_inventory(*, label: str | None = None, service_lane: str | None = None) -> dict[str, Any]:
    report_path = _settings().approved_hybrid_inventory_report_path
    if not report_path.exists():
        raise api_error(404, "HYBRID_INVENTORY_NOT_READY", "승인된 hybrid inventory artifact를 찾을 수 없습니다.")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if not isinstance(report, dict):
        raise api_error(422, "HYBRID_INVENTORY_INVALID", "승인된 hybrid inventory artifact 형식이 올바르지 않습니다.")
    return _build_inventory_view(report, label=label, service_lane=service_lane)


def _load_promoted_hybrid_decision(candidate_key: str) -> tuple[dict[str, Any], Path] | None:
    decisions_root = _settings().manual_review_decisions_dir
    if not decisions_root.exists():
        return None

    matches: list[tuple[str, Path, dict[str, Any]]] = []
    for decision_path in decisions_root.rglob("decision.json"):
        try:
            decision = json.loads(decision_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if decision.get("candidateKey") != candidate_key:
            continue
        decided_at = str(decision.get("decidedAt") or "")
        matches.append((decided_at, decision_path, decision))

    if not matches:
        return None

    _, decision_path, decision = sorted(matches, key=lambda item: (item[0], str(item[1])))[-1]
    if decision.get("finalDecision") != "promote":
        return None
    packet = decision.get("packet")
    if not isinstance(packet, dict):
        return None
    return decision, decision_path


def _build_promoted_hybrid_source_selection(
    decision: dict[str, Any],
    decision_path: Path,
    source_video_path: Path,
    staged_public_path: str,
) -> dict[str, Any]:
    packet = decision.get("packet") if isinstance(decision.get("packet"), dict) else {}
    return {
        "selectionMode": "promoted_manual_review",
        "candidateKey": decision.get("candidateKey"),
        "benchmarkId": packet.get("benchmarkId"),
        "label": packet.get("label"),
        "provider": packet.get("provider"),
        "gateDecision": packet.get("decision"),
        "gateReason": packet.get("gateReason"),
        "reviewCategory": packet.get("reviewCategory"),
        "recommendedAction": packet.get("recommendedAction"),
        "reviewFinalDecision": decision.get("finalDecision"),
        "reviewDecisionPath": str(decision_path),
        "reviewer": decision.get("reviewer"),
        "reviewDecidedAt": decision.get("decidedAt"),
        "sourceVideoPath": str(source_video_path),
        "stagedHybridSourceVideoPath": staged_public_path,
        "contactSheetPath": packet.get("contactSheetPath"),
        "summaryPath": packet.get("summaryPath"),
        "midFrameMse": packet.get("midFrameMse"),
        "motionAvgRgbDiff": packet.get("motionAvgRgbDiff"),
    }


def _attach_approved_hybrid_source(project_id: str, run_id: str, input_snapshot: dict[str, Any]) -> dict[str, Any]:
    candidate_key = input_snapshot.get("approvedHybridSourceCandidateKey")
    if not isinstance(candidate_key, str) or not candidate_key:
        return input_snapshot

    match = _load_promoted_hybrid_decision(candidate_key)
    if match is None:
        raise api_error(422, "HYBRID_SOURCE_NOT_APPROVED", "승격된 hybrid source 후보를 찾을 수 없습니다.")

    decision, decision_path = match
    packet = decision["packet"]
    source_video_path = Path(str(packet.get("sourceVideoPath") or ""))
    if not source_video_path.exists():
        raise api_error(422, "HYBRID_SOURCE_NOT_FOUND", "승격 후보의 원본 비디오를 찾을 수 없습니다.")

    staged_dir = _settings().storage_dir / "projects" / project_id / "hybrid" / run_id
    staged_dir.mkdir(parents=True, exist_ok=True)
    staged_name = source_video_path.name or "approved-hybrid-source.mp4"
    staged_path = staged_dir / staged_name
    shutil.copyfile(source_video_path, staged_path)
    staged_public_path = f"/projects/{project_id}/hybrid/{run_id}/{staged_name}"

    snapshot = dict(input_snapshot)
    snapshot["hybridSourceVideoPath"] = staged_public_path
    snapshot["hybridSourceSelection"] = _build_promoted_hybrid_source_selection(
        decision,
        decision_path,
        source_video_path,
        staged_public_path,
    )
    return snapshot


def _demo_user_id(connection) -> str:
    row = connection.execute("SELECT id FROM users WHERE email = ?", (DEMO_EMAIL,)).fetchone()
    if row is None:
        user_id = str(uuid4())
        now = utc_now()
        connection.execute(
            """
            INSERT INTO users (id, email, password_hash, name, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, DEMO_EMAIL, hash_password(DEMO_PASSWORD), "데모 운영자", now, now),
        )
        return user_id
    return row["id"]


def ensure_demo_state() -> None:
    with get_connection() as connection:
        user_id = _demo_user_id(connection)
        profile = connection.execute("SELECT id FROM store_profiles WHERE user_id = ?", (user_id,)).fetchone()
        if profile is None:
            now = utc_now()
            connection.execute(
                """
                INSERT INTO store_profiles (id, user_id, business_type, region_name, detail_location, default_style, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (str(uuid4()), user_id, "cafe", "성수동", "서울숲 근처", "friendly", now, now),
            )
        for channel, tier in CHANNEL_TIERS.items():
            row = connection.execute(
                "SELECT id FROM social_accounts WHERE user_id = ? AND channel = ?",
                (user_id, channel),
            ).fetchone()
            if row is None:
                now = utc_now()
                status = "connected" if channel == "instagram" else ("expired" if channel == "tiktok" else "not_connected")
                account_name = "demo_store_official" if channel == "instagram" else (f"{channel}_demo" if channel == "tiktok" else None)
                token_expires_at = (
                    (_utc_now_dt() + timedelta(days=7)).isoformat()
                    if channel == "instagram"
                    else (_utc_now_dt() - timedelta(days=1)).isoformat()
                    if channel == "tiktok"
                    else None
                )
                connection.execute(
                    """
                    INSERT INTO social_accounts (
                        id, user_id, channel, account_name, status, access_token_ref,
                        refresh_token_ref, token_expires_at, last_synced_at, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(uuid4()),
                        user_id,
                        channel,
                        account_name,
                        status,
                        f"{channel}-token" if status in {"connected", "expired"} else None,
                        None,
                        token_expires_at,
                        now if status in {"connected", "expired"} else None,
                        now,
                        now,
                    ),
                )


def get_demo_user() -> dict[str, Any]:
    with get_connection() as connection:
        ensure_demo_state()
        row = connection.execute("SELECT * FROM users WHERE email = ?", (DEMO_EMAIL,)).fetchone()
        return dict(row)


def _validate_age_14(birth_date_str: str) -> None:
    try:
        birth = date.fromisoformat(birth_date_str)
    except ValueError:
        raise api_error(400, "INVALID_INPUT", "생년월일 형식이 올바르지 않습니다.")
    today = date.today()
    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    if age < 14:
        raise api_error(403, "AGE_RESTRICTION", "만 14세 이상만 가입할 수 있습니다.")


def register_user(
    email: str,
    password: str,
    name: str,
    birth_date: str,
    ip: str = "unknown",
    user_agent: str | None = None,
) -> dict[str, Any]:
    _validate_age_14(birth_date)
    with get_connection() as connection:
        existing = connection.execute(
            "SELECT id FROM users WHERE email = ? AND deleted_at IS NULL", (email,)
        ).fetchone()
        if existing:
            raise api_error(409, "INVALID_INPUT", "이미 등록된 이메일입니다.")
        user_id = str(uuid4())
        now = utc_now()
        connection.execute(
            """
            INSERT INTO users (id, email, password_hash, name, birth_date, status, failed_login_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 'active', 0, ?, ?)
            """,
            (user_id, email, hash_password(password), name, birth_date, now, now),
        )
        for channel in CHANNEL_TIERS:
            connection.execute(
                """
                INSERT INTO social_accounts (
                    id, user_id, channel, account_name, status, access_token_ref,
                    refresh_token_ref, token_expires_at, last_synced_at, created_at, updated_at
                )
                VALUES (?, ?, ?, NULL, 'not_connected', NULL, NULL, NULL, NULL, ?, ?)
                """,
                (str(uuid4()), user_id, channel, now, now),
            )
    record_signup_consents(user_id=user_id, ip=ip, user_agent=user_agent)
    log_event(event_type="register", user_id=user_id, ip=ip, user_agent=user_agent)
    session_token = issue_session(user_id=user_id, ip=ip, user_agent=user_agent)
    return {"sessionToken": session_token, "user": {"id": user_id, "email": email, "name": name}}


def login_user(
    email: str,
    password: str,
    ip: str = "unknown",
    user_agent: str | None = None,
) -> dict[str, Any]:
    ensure_demo_state()
    _failure_event: dict[str, Any] | None = None
    _failure_error: Exception | None = None
    row = None

    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE email = ? AND deleted_at IS NULL", (email,)
        ).fetchone()
        if row is None:
            _failure_event = {"event_type": "login_failure", "ip": ip, "user_agent": user_agent,
                              "metadata": {"reason": "user_not_found"}}
            _failure_error = api_error(401, "INVALID_CREDENTIALS", "이메일 또는 비밀번호가 올바르지 않습니다.")
        elif row["locked_until"] and row["locked_until"] > utc_now():
            _failure_event = {"event_type": "login_failure", "user_id": row["id"], "ip": ip,
                              "metadata": {"reason": "account_locked"}}
            _failure_error = api_error(423, "ACCOUNT_LOCKED", "로그인 시도가 너무 많습니다. 잠시 후 다시 시도해 주세요.")
        elif not verify_password(password, row["password_hash"]):
            failed_count = (row["failed_login_count"] or 0) + 1
            locked_until = None
            if failed_count >= 5:
                locked_until = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
            connection.execute(
                "UPDATE users SET failed_login_count = ?, locked_until = ?, updated_at = ? WHERE id = ?",
                (failed_count, locked_until, utc_now(), row["id"]),
            )
            _failure_event = {"event_type": "login_failure", "user_id": row["id"], "ip": ip,
                              "metadata": {"failed_count": failed_count}}
            _failure_error = api_error(401, "INVALID_CREDENTIALS", "이메일 또는 비밀번호가 올바르지 않습니다.")
        else:
            connection.execute(
                "UPDATE users SET failed_login_count = 0, locked_until = NULL, updated_at = ? WHERE id = ?",
                (utc_now(), row["id"]),
            )
            # Auto-rehash legacy PBKDF2 → argon2id on successful login
            if not row["password_hash"].startswith("$argon2"):
                new_hash = hash_password(password)
                if new_hash.startswith("$argon2"):
                    connection.execute(
                        "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
                        (new_hash, utc_now(), row["id"]),
                    )

    if _failure_event:
        log_event(**_failure_event)
    if _failure_error:
        raise _failure_error

    log_event(event_type="login_success", user_id=row["id"], ip=ip, user_agent=user_agent)
    session_token = issue_session(user_id=row["id"], ip=ip, user_agent=user_agent)
    return {
        "sessionToken": session_token,
        "user": {"id": row["id"], "email": row["email"], "name": row["name"]},
    }


def me_from_session(session_token: str | None) -> dict[str, Any]:
    if not session_token:
        raise api_error(401, "AUTH_REQUIRED", "로그인이 필요합니다.")
    session = verify_session(session_token)
    if session is None:
        raise api_error(401, "AUTH_REQUIRED", "세션이 만료되었습니다. 다시 로그인해 주세요.")
    return {"id": session["userId"], "email": session["email"], "name": session["name"]}


def logout_user(session_token: str | None, user_id: str | None, ip: str = "unknown") -> None:
    if session_token:
        revoke_session_by_token(session_token)
    log_event(event_type="logout", user_id=user_id, ip=ip)


def verify_email_token(token: str) -> dict[str, Any]:
    try:
        user_id = consume_token(token, "verify_email")
    except ValueError as exc:
        raise api_error(400, "INVALID_TOKEN", "유효하지 않은 인증 토큰입니다.") from exc
    with get_connection() as connection:
        connection.execute(
            "UPDATE users SET email_verified_at = ?, updated_at = ? WHERE id = ?",
            (utc_now(), utc_now(), user_id),
        )
    log_event(event_type="email_verify", user_id=user_id)
    return {"verified": True}


def request_password_reset(email: str, ip: str = "unknown") -> dict[str, Any]:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id FROM users WHERE email = ? AND deleted_at IS NULL", (email,)
        ).fetchone()
    if row:
        reset_token = issue_password_reset(row["id"])
        log_event(event_type="password_reset_request", user_id=row["id"], ip=ip)
        # 실제 서비스에서는 이메일 발송. 여기서는 토큰 반환 (개발 편의)
        return {"message": "비밀번호 재설정 이메일을 발송했습니다.", "devToken": reset_token}
    # 존재하지 않는 이메일도 동일 응답 (이메일 열거 방지)
    return {"message": "비밀번호 재설정 이메일을 발송했습니다."}


def confirm_password_reset(token: str, new_password: str) -> dict[str, Any]:
    try:
        user_id = consume_token(token, "reset_password")
    except ValueError as exc:
        raise api_error(400, "INVALID_TOKEN", "유효하지 않은 재설정 토큰입니다.") from exc
    with get_connection() as connection:
        connection.execute(
            "UPDATE users SET password_hash = ?, failed_login_count = 0, locked_until = NULL, updated_at = ? WHERE id = ?",
            (hash_password(new_password), utc_now(), user_id),
        )
    from app.services.session import revoke_all_sessions
    revoke_all_sessions(user_id)
    log_event(event_type="password_reset_complete", user_id=user_id)
    return {"reset": True}


def change_password(
    user_id: str,
    current_password: str,
    new_password: str,
    session_token: str | None = None,
) -> dict[str, Any]:
    with get_connection() as connection:
        row = connection.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,)).fetchone()
        if row is None or not verify_password(current_password, row["password_hash"]):
            raise api_error(401, "INVALID_CREDENTIALS", "현재 비밀번호가 올바르지 않습니다.")
        connection.execute(
            "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
            (hash_password(new_password), utc_now(), user_id),
        )
    from app.services.session import revoke_all_sessions, verify_session
    except_session_id = None
    if session_token:
        session_data = verify_session(session_token)
        if session_data:
            except_session_id = session_data["sessionId"]
    revoke_all_sessions(user_id, except_session_id=except_session_id)
    log_event(event_type="password_change", user_id=user_id)
    return {"changed": True}


def delete_account(user_id: str, ip: str = "unknown") -> dict[str, Any]:
    now = utc_now()
    hard_delete_at = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    anon_email = f"deleted_{user_id}@deleted.local"
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE users
            SET deleted_at = ?, hard_delete_at = ?, email = ?, status = 'pending_deletion', updated_at = ?
            WHERE id = ?
            """,
            (now, hard_delete_at, anon_email, now, user_id),
        )
        connection.execute("DELETE FROM social_accounts WHERE user_id = ?", (user_id,))
    from app.services.session import revoke_all_sessions
    revoke_all_sessions(user_id)
    log_event(event_type="account_deleted", user_id=user_id, ip=ip)
    return {"deleted": True, "scheduledDeletionAt": hard_delete_at, "message": "회원 탈퇴 신청이 완료되었습니다. 30일 후 데이터가 완전 삭제됩니다."}


def get_store_profile(user_id: str) -> dict[str, Any]:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM store_profiles WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (user_id,)).fetchone()
        if row is None:
            return {
                "storeProfileId": None,
                "businessType": None,
                "regionName": None,
                "detailLocation": None,
                "defaultStyle": None,
            }
        return {
            "storeProfileId": row["id"],
            "businessType": row["business_type"],
            "regionName": row["region_name"],
            "detailLocation": row["detail_location"],
            "defaultStyle": row["default_style"],
        }


def update_store_profile(payload: dict[str, Any], user_id: str) -> dict[str, Any]:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM store_profiles WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (user_id,)).fetchone()
        now = utc_now()
        if row is None:
            profile_id = str(uuid4())
            connection.execute(
                """
                INSERT INTO store_profiles (id, user_id, business_type, region_name, detail_location, default_style, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    profile_id,
                    user_id,
                    payload["businessType"],
                    payload["regionName"],
                    payload.get("detailLocation"),
                    payload.get("defaultStyle"),
                    now,
                    now,
                ),
            )
        else:
            profile_id = row["id"]
            connection.execute(
                """
                UPDATE store_profiles
                SET business_type = ?, region_name = ?, detail_location = ?, default_style = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    payload["businessType"],
                    payload["regionName"],
                    payload.get("detailLocation"),
                    payload.get("defaultStyle"),
                    now,
                    profile_id,
                ),
            )
        return {"storeProfileId": profile_id, "updated": True}


def list_projects(user_id: str, status: str | None = None) -> dict[str, Any]:
    with get_connection() as connection:
        query = "SELECT * FROM content_projects WHERE user_id = ?"
        params: list[Any] = [user_id]
        if status:
            query += " AND current_status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC"
        rows = connection.execute(query, params).fetchall()
        items = [
            {
                "projectId": row["id"],
                "businessType": row["business_type"],
                "purpose": row["purpose"],
                "style": row["style"],
                "status": row["current_status"],
                "createdAt": row["created_at"],
            }
            for row in rows
        ]
        return {"items": items, "nextCursor": None, "hasNext": False}


def create_project(payload: dict[str, Any], user_id: str) -> dict[str, Any]:
    with get_connection() as connection:
        project_id = str(uuid4())
        now = utc_now()
        connection.execute(
            """
            INSERT INTO content_projects (
                id, user_id, business_type, purpose, style, region_name, detail_location,
                selected_channels_json, latest_generation_run_id, current_status, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, 'draft', ?, ?)
            """,
            (
                project_id,
                user_id,
                payload["businessType"],
                payload["purpose"],
                payload["style"],
                payload["regionName"],
                payload.get("detailLocation"),
                _json_dumps(payload["channels"]),
                now,
                now,
            ),
        )
        return {"projectId": project_id, "status": "draft", "createdAt": now}


def get_project_detail(project_id: str, user_id: str) -> dict[str, Any]:
    with get_connection() as connection:
        row = _get_project_for_user(connection, project_id, user_id)
        asset_count = connection.execute("SELECT COUNT(*) AS count FROM project_assets WHERE project_id = ?", (project_id,)).fetchone()["count"]
        return {
            "projectId": row["id"],
            "businessType": row["business_type"],
            "regionName": row["region_name"],
            "detailLocation": row["detail_location"],
            "purpose": row["purpose"],
            "style": row["style"],
            "channels": _json_loads(row["selected_channels_json"]) or [],
            "status": row["current_status"],
            "assetCount": asset_count,
        }


def _get_project_for_user(connection, project_id: str, user_id: str):
    row = connection.execute(
        "SELECT * FROM content_projects WHERE id = ? AND user_id = ?",
        (project_id, user_id),
    ).fetchone()
    if row is None:
        raise api_error(404, "PROJECT_NOT_FOUND", "프로젝트를 찾을 수 없습니다.")
    return row


def list_assets(project_id: str, user_id: str) -> list[dict[str, Any]]:
    with get_connection() as connection:
        _get_project_for_user(connection, project_id, user_id)
        rows = connection.execute("SELECT * FROM project_assets WHERE project_id = ? ORDER BY created_at ASC", (project_id,)).fetchall()
        return [
            {
                "assetId": row["id"],
                "fileName": row["original_file_name"],
                "width": row["width"],
                "height": row["height"],
                "warnings": _json_loads(row["warnings_json"]) or [],
            }
            for row in rows
        ]


def _get_social_account(connection, user_id: str, channel: str):
    _supported_channel(channel)
    account = connection.execute(
        "SELECT * FROM social_accounts WHERE user_id = ? AND channel = ?",
        (user_id, channel),
    ).fetchone()
    if account is None:
        raise api_error(404, "PROJECT_NOT_FOUND", "연동 대상을 찾을 수 없습니다.")
    if _is_token_expired(account["token_expires_at"]) and account["status"] == "connected":
        now = utc_now()
        connection.execute(
            "UPDATE social_accounts SET status = 'expired', updated_at = ? WHERE id = ?",
            (now, account["id"]),
        )
        account = connection.execute("SELECT * FROM social_accounts WHERE id = ?", (account["id"],)).fetchone()
    return account


def _image_warnings(image: Image.Image) -> list[str]:
    warnings: list[str] = []
    grayscale = image.convert("L")
    brightness = ImageStat.Stat(grayscale).mean[0]
    if brightness < 75:
        warnings.append("LOW_BRIGHTNESS")
    if min(image.width, image.height) < 900:
        warnings.append("LOW_RESOLUTION")
    blur_score = ImageStat.Stat(grayscale.filter(ImageFilter.FIND_EDGES)).var[0]
    if blur_score < 120:
        warnings.append("POSSIBLE_BLUR")
    return warnings


_IMAGE_MAGIC: list[tuple[bytes, str]] = [
    (b"\xff\xd8\xff", "jpeg"),
    (b"\x89PNG\r\n\x1a\n", "png"),
]


def _check_image_magic(data: bytes) -> None:
    for magic, _ in _IMAGE_MAGIC:
        if data[: len(magic)] == magic:
            return
    raise api_error(400, "ASSET_VALIDATION_FAILED", "파일 내용이 jpg 또는 png 형식이 아닙니다.")


def upload_assets(project_id: str, files: list[tuple[str, bytes, str]], user_id: str) -> dict[str, Any]:
    settings = _settings()
    with get_connection() as connection:
        _get_project_for_user(connection, project_id, user_id)
        project_root = settings.storage_dir / "projects" / project_id / "raw"
        project_root.mkdir(parents=True, exist_ok=True)
        uploaded = []
        for file_name, file_bytes, mime_type in files:
            if not file_name.lower().endswith((".jpg", ".jpeg", ".png")):
                raise api_error(400, "ASSET_VALIDATION_FAILED", "jpg, jpeg, png만 업로드할 수 있습니다.")
            _check_image_magic(file_bytes)
            asset_id = str(uuid4())
            suffix = Path(file_name).suffix or ".png"
            storage_path = project_root / f"{asset_id}{suffix}"
            storage_path.write_bytes(file_bytes)
            image = Image.open(storage_path).convert("RGB")
            warnings = _image_warnings(image)
            now = utc_now()
            connection.execute(
                """
                INSERT INTO project_assets (
                    id, project_id, original_file_name, mime_type, file_size_bytes,
                    width, height, storage_path, warnings_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    asset_id,
                    project_id,
                    file_name,
                    mime_type,
                    len(file_bytes),
                    image.width,
                    image.height,
                    f"/projects/{project_id}/raw/{asset_id}{suffix}",
                    _json_dumps(warnings),
                    now,
                ),
            )
            uploaded.append({"assetId": asset_id, "fileName": file_name, "width": image.width, "height": image.height, "warnings": warnings})
        return {"projectId": project_id, "assets": uploaded}


def _ensure_assets_belong_to_project(connection, project_id: str, asset_ids: list[str]) -> None:
    if not asset_ids:
        return
    placeholders = ",".join("?" for _ in asset_ids)
    rows = connection.execute(
        f"SELECT id FROM project_assets WHERE project_id = ? AND id IN ({placeholders})",
        [project_id, *asset_ids],
    ).fetchall()
    found_ids = {row["id"] for row in rows}
    if found_ids != set(asset_ids):
        raise api_error(422, "INVALID_STATE_TRANSITION", "프로젝트에 속하지 않는 자산이 포함되어 있습니다.")


def _ensure_template_supported(project: dict[str, Any], template_id: str) -> None:
    manifest_path = _settings().template_spec_dir / "manifests" / "template-map.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    template = next((item for item in manifest["templates"] if item["templateId"] == template_id), None)
    if template is None:
        raise api_error(400, "INVALID_INPUT", "알 수 없는 템플릿입니다.")
    if project["purpose"] not in template["purposes"] or project["style"] not in template["styles"]:
        raise api_error(422, "INVALID_STATE_TRANSITION", "선택한 템플릿이 현재 프로젝트와 호환되지 않습니다.")


def _create_generation_run(
    project_id: str,
    template_id: str,
    input_snapshot: dict[str, Any],
    quick_options: dict[str, Any],
    run_type: str,
    user_id: str,
) -> dict[str, Any]:
    with get_connection() as connection:
        project_row = _get_project_for_user(connection, project_id, user_id)
        _ensure_assets_belong_to_project(connection, project_id, input_snapshot.get("assetIds", []))
        project = {"purpose": project_row["purpose"], "style": project_row["style"]}
        _ensure_template_supported(project, template_id)
        run_id = str(uuid4())
        input_snapshot = _attach_approved_hybrid_source(project_id, run_id, input_snapshot)
        now = utc_now()
        connection.execute(
            """
            INSERT INTO generation_runs (
                id, project_id, run_type, trigger_source, template_id,
                input_snapshot_json, quick_options_snapshot_json, status, error_code,
                started_at, finished_at, created_at
            )
            VALUES (?, ?, ?, 'user', ?, ?, ?, 'queued', NULL, NULL, NULL, ?)
            """,
            (run_id, project_id, run_type, template_id, _json_dumps(input_snapshot), _json_dumps(quick_options), now),
        )
        for step_name in STEP_NAMES:
            connection.execute(
                """
                INSERT INTO generation_run_steps (id, generation_run_id, step_name, status, error_code, started_at, finished_at, updated_at)
                VALUES (?, ?, ?, 'pending', NULL, NULL, NULL, ?)
                """,
                (str(uuid4()), run_id, step_name, now),
            )
        connection.execute(
            "UPDATE content_projects SET latest_generation_run_id = ?, current_status = 'queued', updated_at = ? WHERE id = ?",
            (run_id, now, project_id),
        )
        return {"generationRunId": run_id, "projectId": project_id, "status": "queued"}


def start_generation(project_id: str, payload: dict[str, Any], user_id: str) -> dict[str, Any]:
    if not payload["assetIds"]:
        raise api_error(400, "INVALID_INPUT", "최소 1개의 자산이 필요합니다.")
    input_snapshot = {"assetIds": payload["assetIds"], "templateId": payload["templateId"]}
    approved_candidate_key = payload.get("approvedHybridSourceCandidateKey")
    if isinstance(approved_candidate_key, str) and approved_candidate_key:
        input_snapshot["approvedHybridSourceCandidateKey"] = approved_candidate_key
    return _create_generation_run(project_id, payload["templateId"], input_snapshot, payload.get("quickOptions") or {}, "initial", user_id)


def regenerate_project(project_id: str, payload: dict[str, Any], user_id: str) -> dict[str, Any]:
    with get_connection() as connection:
        project_row = _get_project_for_user(connection, project_id, user_id)
        assets = connection.execute("SELECT id FROM project_assets WHERE project_id = ? ORDER BY created_at ASC", (project_id,)).fetchall()
        latest_run_id = project_row["latest_generation_run_id"]
        template_row = connection.execute("SELECT template_id FROM generation_runs WHERE id = ?", (latest_run_id,)).fetchone() if latest_run_id else None
        template_id = payload["changeSet"].get("templateId") or (template_row["template_id"] if template_row else "T01")
        input_snapshot = {"assetIds": [asset["id"] for asset in assets], "templateId": template_id, **payload["changeSet"]}
    return _create_generation_run(project_id, template_id, input_snapshot, payload["changeSet"], "regenerate", user_id)


def run_generation_background(project_id: str, generation_run_id: str) -> None:
    settings = _settings()
    run_generation_job(settings.db_path, settings.storage_dir, settings.template_spec_dir, project_id, generation_run_id)


def get_generation_status(project_id: str, user_id: str) -> dict[str, Any]:
    with get_connection() as connection:
        project = _get_project_for_user(connection, project_id, user_id)
        run_id = project["latest_generation_run_id"]
        if not run_id:
            return {"projectId": project_id, "projectStatus": project["current_status"], "steps": [], "error": None}
        steps = connection.execute(
            "SELECT step_name, status FROM generation_run_steps WHERE generation_run_id = ? ORDER BY rowid ASC",
            (run_id,),
        ).fetchall()
        run = connection.execute("SELECT * FROM generation_runs WHERE id = ?", (run_id,)).fetchone()
        result = None
        if project["current_status"] == "generated":
            variant = connection.execute(
                """
                SELECT gv.*, cp.cta_text
                FROM generated_variants gv
                JOIN copy_sets cp ON cp.id = gv.copy_set_id
                WHERE gv.generation_run_id = ? AND gv.is_selected = 1
                ORDER BY gv.created_at DESC LIMIT 1
                """,
                (run_id,),
            ).fetchone()
            if variant:
                result = {
                    "generationRunId": run_id,
                    "variantId": variant["id"],
                    "videoId": variant["id"],
                    "postId": variant["id"],
                    "copySetId": variant["copy_set_id"],
                    "previewVideoUrl": f"/media/{variant['video_path'].lstrip('/')}",
                    "previewImageUrl": f"/media/{variant['post_image_path'].lstrip('/')}",
                    "ctaText": variant["cta_text"],
                }
        error = None
        if run and run["status"] == "failed":
            error = {"code": run["error_code"] or "RENDER_FAILED", "message": "숏폼 렌더링에 실패했습니다. 다시 시도해 주세요."}
        return {
            "projectId": project_id,
            "projectStatus": project["current_status"],
            "steps": [{"name": step["step_name"], "status": step["status"]} for step in steps],
            "result": result,
            "error": error,
        }


def get_project_result(project_id: str, user_id: str) -> dict[str, Any]:
    with get_connection() as connection:
        project = _get_project_for_user(connection, project_id, user_id)
        run_id = project["latest_generation_run_id"]
        variant = connection.execute(
            """
            SELECT gv.*, cp.hook_text, cp.caption_options_json, cp.hashtags_json, cp.cta_text
            FROM generated_variants gv
            JOIN copy_sets cp ON cp.id = gv.copy_set_id
            WHERE gv.generation_run_id = ? AND gv.is_selected = 1
            ORDER BY gv.created_at DESC LIMIT 1
            """,
            (run_id,),
        ).fetchone()
        if variant is None:
            raise api_error(422, "INVALID_STATE_TRANSITION", "아직 결과가 준비되지 않았습니다.")
        template_id = connection.execute("SELECT template_id FROM generation_runs WHERE id = ?", (run_id,)).fetchone()["template_id"]
        render_meta = _json_loads(variant["render_meta_json"]) or {}
        scene_plan = None
        if render_meta.get("scenePlanPath"):
            scene_plan = {
                "url": f"/media/{str(render_meta['scenePlanPath']).lstrip('/')}",
                "sceneCount": render_meta.get("sceneCount"),
                "sceneSpecVersion": render_meta.get("sceneSpecVersion"),
            }
        return {
            "projectId": project_id,
            "generationRunId": run_id,
            "variantId": variant["id"],
            "video": {
                "videoId": variant["id"],
                "url": f"/media/{variant['video_path'].lstrip('/')}",
                "durationSec": variant["duration_sec"],
                "templateId": template_id,
            },
            "post": {"postId": variant["id"], "url": f"/media/{variant['post_image_path'].lstrip('/')}"},
            "copySet": {
                "copySetId": variant["copy_set_id"],
                "hookText": variant["hook_text"],
                "captions": _json_loads(variant["caption_options_json"]) or [],
                "hashtags": _json_loads(variant["hashtags_json"]) or [],
                "ctaText": variant["cta_text"],
            },
            "scenePlan": scene_plan,
            "sceneLayerSummary": render_meta.get("sceneLayerSummary"),
            "changeImpactSummary": render_meta.get("changeImpactSummary"),
            "copyPolicy": render_meta.get("copyPolicy"),
            "copyDeck": render_meta.get("copyDeck"),
            "copyGeneration": render_meta.get("copyGeneration"),
            "promptBaselineSummary": render_meta.get("promptBaselineSummary"),
            "rendererSummary": {
                "videoSourceMode": render_meta.get("rendererVideoSourceMode"),
                "motionMode": render_meta.get("rendererMotionMode"),
                "framingMode": render_meta.get("rendererFramingMode"),
                "durationStrategy": render_meta.get("rendererHybridDurationStrategy"),
                "targetDurationSec": render_meta.get("rendererHybridTargetDurationSec"),
                "hybridSourceSelectionMode": (render_meta.get("rendererHybridSourceSelection") or {}).get("selectionMode")
                if isinstance(render_meta.get("rendererHybridSourceSelection"), dict)
                else None,
                "hybridSourceCandidateKey": (render_meta.get("rendererHybridSourceSelection") or {}).get("candidateKey")
                if isinstance(render_meta.get("rendererHybridSourceSelection"), dict)
                else None,
            },
        }


def _build_assist_package(connection, variant_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    variant = connection.execute(
        """
        SELECT gv.video_path, cp.caption_options_json, cp.hashtags_json, cp.cta_text
        FROM generated_variants gv
        JOIN copy_sets cp ON cp.id = gv.copy_set_id
        WHERE gv.id = ?
        """,
        (variant_id,),
    ).fetchone()
    if variant is None:
        raise api_error(404, "PROJECT_NOT_FOUND", "결과 variant를 찾을 수 없습니다.")
    captions = _json_loads(variant["caption_options_json"]) or []
    hashtags = payload.get("hashtags") or _json_loads(variant["hashtags_json"]) or []
    caption = payload.get("captionOverride") or (captions[0] if captions else variant["cta_text"])
    return {
        "mediaUrl": f"/media/{variant['video_path'].lstrip('/')}",
        "caption": caption,
        "hashtags": hashtags,
        "thumbnailText": payload.get("thumbnailText"),
    }


def publish_project(project_id: str, payload: dict[str, Any], user_id: str) -> dict[str, Any]:
    with get_connection() as connection:
        project = connection.execute(
            "SELECT * FROM content_projects WHERE id = ? AND user_id = ?",
            (project_id, user_id),
        ).fetchone()
        if project is None:
            raise api_error(404, "PROJECT_NOT_FOUND", "프로젝트를 찾을 수 없습니다.")
        latest_generation_run_id = project["latest_generation_run_id"]
        if not latest_generation_run_id:
            raise api_error(422, "INVALID_STATE_TRANSITION", "게시할 결과물을 찾을 수 없습니다.")
        variant = connection.execute(
            """
            SELECT id
            FROM generated_variants
            WHERE id = ? AND generation_run_id = ? AND is_selected = 1
            """,
            (payload["variantId"], latest_generation_run_id),
        ).fetchone()
        if variant is None:
            raise api_error(422, "INVALID_STATE_TRANSITION", "게시할 결과물을 찾을 수 없습니다.")
        _supported_channel(payload["channel"])
        account = _get_social_account(connection, user_id, payload["channel"])
        assist_required = (
            payload["publishMode"] == "assist"
            or payload["channel"] != "instagram"
            or account is None
            or account["status"] != "connected"
        )
        upload_job_id = str(uuid4())
        now = utc_now()
        assist_package = _build_assist_package(connection, payload["variantId"], payload) if assist_required else None
        error_code = None
        if assist_required:
            if payload["publishMode"] == "assist":
                error_code = None
            elif account is None or account["status"] in {"not_connected", "connecting"}:
                error_code = "AUTH_REQUIRED"
            elif account["status"] == "expired":
                error_code = "SOCIAL_TOKEN_EXPIRED"
            elif account["status"] == "permission_error":
                error_code = "PUBLISH_FAILED"
            elif payload["channel"] != "instagram":
                error_code = "PUBLISH_FAILED"
        connection.execute(
            """
            INSERT INTO upload_jobs (
                id, project_id, variant_id, social_account_id, channel, status, request_payload_snapshot_json,
                external_post_id, error_code, retry_count, assist_package_path, assist_confirmed_at,
                published_at, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, NULL, ?, 0, ?, NULL, NULL, ?, ?)
            """,
            (
                upload_job_id,
                project_id,
                payload["variantId"],
                account["id"] if account else None,
                payload["channel"],
                "assist_required" if assist_required else "queued",
                _json_dumps(payload),
                error_code,
                None,
                now,
                now,
            ),
        )
        connection.execute(
            "UPDATE content_projects SET current_status = ?, updated_at = ? WHERE id = ?",
            ("upload_assist" if assist_required else "publishing", now, project_id),
        )
        response = {"uploadJobId": upload_job_id, "projectId": project_id, "status": "assist_required" if assist_required else "queued"}
        if assist_required:
            response["assistPackage"] = assist_package
        return response


def run_publish_background(upload_job_id: str) -> None:
    settings = _settings()
    run_publish_job(settings.db_path, settings.storage_dir, settings.template_spec_dir, upload_job_id)


def _get_upload_job_for_user(connection, job_id: str, user_id: str):
    row = connection.execute(
        """
        SELECT uj.*
        FROM upload_jobs uj
        JOIN content_projects cp ON cp.id = uj.project_id
        WHERE uj.id = ? AND cp.user_id = ?
        """,
        (job_id, user_id),
    ).fetchone()
    if row is None:
        raise api_error(404, "PROJECT_NOT_FOUND", "업로드 작업을 찾을 수 없습니다.")
    return row


def _upload_job_response(connection, row) -> dict[str, Any]:
    payload = _json_loads(row["request_payload_snapshot_json"]) or {}
    assist_package = _build_assist_package(connection, row["variant_id"], payload) if row["status"] == "assist_required" else None
    error = None
    if row["error_code"]:
        message = "업로드 보조 모드로 전환되었습니다."
        if row["error_code"] == "AUTH_REQUIRED":
            message = "계정 연동이 필요해 업로드 보조 모드로 전환되었습니다."
        elif row["error_code"] == "SOCIAL_TOKEN_EXPIRED":
            message = "토큰이 만료되어 재연동 또는 업로드 보조가 필요합니다."
        error = {"code": row["error_code"], "message": message}
    return {
        "uploadJobId": row["id"],
        "projectId": row["project_id"],
        "channel": row["channel"],
        "status": row["status"],
        "assistPackage": assist_package,
        "error": error,
    }


def get_upload_job(job_id: str, user_id: str) -> dict[str, Any]:
    with get_connection() as connection:
        row = _get_upload_job_for_user(connection, job_id, user_id)
        return _upload_job_response(connection, row)


def list_project_upload_jobs(project_id: str, user_id: str) -> list[dict[str, Any]]:
    with get_connection() as connection:
        _get_project_for_user(connection, project_id, user_id)
        rows = connection.execute(
            "SELECT * FROM upload_jobs WHERE project_id = ? ORDER BY updated_at DESC, created_at DESC",
            (project_id,),
        ).fetchall()
        return [_upload_job_response(connection, row) for row in rows]


def get_latest_upload_job(project_id: str, user_id: str) -> dict[str, Any] | None:
    with get_connection() as connection:
        _get_project_for_user(connection, project_id, user_id)
        row = connection.execute(
            "SELECT * FROM upload_jobs WHERE project_id = ? ORDER BY updated_at DESC, created_at DESC LIMIT 1",
            (project_id,),
        ).fetchone()
        return _upload_job_response(connection, row) if row else None


def mark_assist_complete(job_id: str, completed_at: str | None, user_id: str) -> dict[str, Any]:
    with get_connection() as connection:
        row = _get_upload_job_for_user(connection, job_id, user_id)
        when = completed_at or utc_now()
        connection.execute(
            """
            UPDATE upload_jobs
            SET status = 'assisted_completed', assist_confirmed_at = ?, published_at = ?, updated_at = ?, error_code = NULL
            WHERE id = ?
            """,
            (when, when, utc_now(), job_id),
        )
        connection.execute(
            "UPDATE content_projects SET current_status = 'published', updated_at = ? WHERE id = ?",
            (utc_now(), row["project_id"]),
        )
        return {"uploadJobId": job_id, "status": "assisted_completed"}


def list_social_accounts(user_id: str) -> dict[str, Any]:
    with get_connection() as connection:
        rows = [_get_social_account(connection, user_id, channel) for channel in sorted(CHANNEL_TIERS.keys())]
        items = []
        for row in rows:
            items.append(
                {
                    "channel": row["channel"],
                    "status": row["status"],
                    "accountName": row["account_name"],
                    "lastSyncedAt": row["last_synced_at"],
                    "tokenExpiresAt": row["token_expires_at"],
                }
            )
        return {"items": items}


def connect_social_account(channel: str, user_id: str) -> dict[str, Any]:
    with get_connection() as connection:
        _supported_channel(channel)
        now = utc_now()
        state = str(uuid4())
        connection.execute(
            """
            UPDATE social_accounts
            SET status = 'connecting', refresh_token_ref = ?, updated_at = ?
            WHERE user_id = ? AND channel = ?
            """,
            (state, now, user_id, channel),
        )
        return {"channel": channel, "status": "connecting", "redirectUrl": f"/api/social-accounts/{channel}/callback?code=demo-code&state={state}"}


def callback_social_account(channel: str, code: str | None, state: str | None, user_id: str) -> dict[str, Any]:
    with get_connection() as connection:
        row = _get_social_account(connection, user_id, channel)
        if not code or not state or row["refresh_token_ref"] != state:
            raise api_error(400, "OAUTH_CALLBACK_INVALID", "OAuth 콜백 검증에 실패했습니다.")
        if code == "permission-error":
            connection.execute(
                """
                UPDATE social_accounts
                SET status = 'permission_error', refresh_token_ref = NULL, updated_at = ?
                WHERE id = ?
                """,
                (utc_now(), row["id"]),
            )
            # Persist the degraded account state before surfacing the callback error.
            connection.commit()
            raise api_error(400, "OAUTH_CALLBACK_INVALID", "OAuth 권한 범위를 확인해 주세요.")
        connection.execute(
            """
            UPDATE social_accounts
            SET status = 'connected', account_name = COALESCE(account_name, ?), access_token_ref = ?, refresh_token_ref = NULL,
                token_expires_at = ?, last_synced_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                "demo_store_official" if channel == "instagram" else f"{channel}_demo",
                encrypt_token(f"{channel}-token"),
                (_utc_now_dt() + timedelta(days=7)).isoformat(),
                utc_now(),
                utc_now(),
                row["id"],
            ),
        )
        return {"channel": channel, "status": "connected", "socialAccountId": row["id"]}
