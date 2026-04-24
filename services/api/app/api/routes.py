from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Cookie, File, HTTPException, Query, Request, Response, UploadFile, status

from app.core.config import get_settings
from app.core.rate_limit import allow_login, allow_password_reset, allow_register
from app.services.crypto import NotConnectedError, get_valid_access_token
from app.schemas.api import (
    AccountDeleteResponse,
    ApprovedHybridInventoryResponse,
    AssistCompleteRequest,
    AssistCompleteResponse,
    AuthResponse,
    ChangePasswordRequest,
    ConnectSocialAccountResponse,
    CreateProjectRequest,
    CreateProjectResponse,
    GenerateRequest,
    GenerationRunResponse,
    GenerationStatusResponse,
    LoginRequest,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectResultResponse,
    PublishRequest,
    PublishResponse,
    RegisterRequest,
    RegenerateRequest,
    SessionResponse,
    SocialAccountCallbackResponse,
    SocialAccountsResponse,
    StoreProfileRequest,
    StoreProfileResponse,
    UpdateStoreProfileResponse,
    UploadAssetsResponse,
    UploadJobListResponse,
    UploadJobResponse,
    UserPayload,
    VerifyEmailRequest,
)
from app.services.runtime import (
    callback_social_account,
    change_password,
    confirm_password_reset,
    connect_social_account,
    create_project,
    delete_account,
    get_approved_hybrid_inventory,
    get_generation_status,
    get_latest_upload_job,
    get_project_detail,
    get_project_result,
    get_store_profile,
    get_upload_job,
    list_assets,
    list_project_upload_jobs,
    list_projects,
    list_social_accounts,
    login_user,
    logout_user,
    mark_assist_complete,
    me_from_session,
    publish_project,
    register_user,
    regenerate_project,
    request_password_reset,
    run_generation_background,
    run_publish_background,
    start_generation,
    update_store_profile,
    upload_assets,
    verify_email_token,
)


router = APIRouter(prefix="/api")
SessionCookie = Annotated[str | None, Cookie(alias="session")]

SESSION_COOKIE_MAX_AGE = get_settings().session_ttl_sec
SESSION_COOKIE_SECURE = get_settings().cookie_secure


def _set_session_cookie(response: Response, session_token: str) -> None:
    response.set_cookie(
        key="session",
        value=session_token,
        httponly=True,
        secure=SESSION_COOKIE_SECURE,
        samesite="lax",
        max_age=SESSION_COOKIE_MAX_AGE,
        path="/",
    )


def _clear_session_cookie(response: Response) -> None:
    response.delete_cookie(key="session", path="/")


@router.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, request: Request, response: Response):
    ip = request.client.host if request.client else "unknown"
    if not allow_register(ip):
        raise HTTPException(status_code=429, detail={"error": {"code": "RATE_LIMITED", "message": "요청이 너무 많습니다. 잠시 후 다시 시도해 주세요."}})
    ua = request.headers.get("user-agent")
    result = register_user(
        email=payload.email,
        password=payload.password,
        name=payload.name,
        birth_date=payload.birthDate,
        ip=ip,
        user_agent=ua,
    )
    if "sessionToken" in result:
        _set_session_cookie(response, result.pop("sessionToken"))
    return result


@router.post("/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest, request: Request, response: Response):
    ip = request.client.host if request.client else "unknown"
    if not allow_login(ip, payload.email):
        raise HTTPException(status_code=429, detail={"error": {"code": "RATE_LIMITED", "message": "요청이 너무 많습니다. 잠시 후 다시 시도해 주세요."}})
    ua = request.headers.get("user-agent")
    result = login_user(email=payload.email, password=payload.password, ip=ip, user_agent=ua)
    if "sessionToken" in result:
        _set_session_cookie(response, result.pop("sessionToken"))
    return result


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, session: SessionCookie = None) -> Response:
    ip = request.client.host if request.client else "unknown"
    user = me_from_session(session) if session else None
    logout_user(session_token=session, user_id=user["id"] if user else None, ip=ip)
    _clear_session_cookie(response)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/auth/session", response_model=SessionResponse)
def get_session(session: SessionCookie = None):
    user = me_from_session(session)
    return {"user": {"id": user["id"], "email": user["email"], "name": user["name"]}}


@router.post("/auth/verify-email")
def verify_email(payload: VerifyEmailRequest):
    return verify_email_token(payload.token)


@router.post("/auth/password/reset-request")
def password_reset_request(payload: PasswordResetRequest, request: Request):
    ip = request.client.host if request.client else "unknown"
    if not allow_password_reset(ip, payload.email):
        raise HTTPException(status_code=429, detail={"error": {"code": "RATE_LIMITED", "message": "요청이 너무 많습니다. 잠시 후 다시 시도해 주세요."}})
    return request_password_reset(email=payload.email, ip=ip)


@router.post("/auth/password/reset-confirm")
def password_reset_confirm(payload: PasswordResetConfirmRequest, response: Response):
    result = confirm_password_reset(token=payload.token, new_password=payload.newPassword)
    _clear_session_cookie(response)
    return result


@router.post("/auth/password/change")
def password_change(payload: ChangePasswordRequest, session: SessionCookie = None):
    user = me_from_session(session)
    return change_password(
        user_id=user["id"],
        current_password=payload.currentPassword,
        new_password=payload.newPassword,
        session_token=session,
    )


@router.delete("/account/me", response_model=AccountDeleteResponse)
def account_delete(request: Request, response: Response, session: SessionCookie = None):
    user = me_from_session(session)
    ip = request.client.host if request.client else "unknown"
    result = delete_account(user_id=user["id"], ip=ip)
    _clear_session_cookie(response)
    return result


@router.get("/me")
def get_me(session: SessionCookie = None):
    user = me_from_session(session)
    return {"id": user["id"], "email": user["email"], "name": user["name"]}


@router.get("/store-profile", response_model=StoreProfileResponse)
def store_profile(session: SessionCookie = None):
    user = me_from_session(session)
    return get_store_profile(user["id"])


@router.put("/store-profile", response_model=UpdateStoreProfileResponse)
def save_store_profile(payload: StoreProfileRequest, session: SessionCookie = None):
    user = me_from_session(session)
    return update_store_profile(payload.model_dump(), user["id"])


@router.post("/projects", response_model=CreateProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project_route(payload: CreateProjectRequest, session: SessionCookie = None):
    user = me_from_session(session)
    return create_project(payload.model_dump(), user["id"])


@router.get("/projects", response_model=ProjectListResponse)
def list_projects_route(status: str | None = None, session: SessionCookie = None):
    user = me_from_session(session)
    return list_projects(user["id"], status)


@router.get("/projects/{project_id}", response_model=ProjectDetailResponse)
def get_project_route(project_id: str, session: SessionCookie = None):
    user = me_from_session(session)
    return get_project_detail(project_id, user["id"])


@router.get("/projects/{project_id}/assets", response_model=UploadAssetsResponse)
def list_assets_route(project_id: str, session: SessionCookie = None):
    user = me_from_session(session)
    return {"projectId": project_id, "assets": list_assets(project_id, user["id"])}


_MAX_UPLOAD_FILES = 5
_MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/projects/{project_id}/assets", response_model=UploadAssetsResponse, status_code=status.HTTP_201_CREATED)
async def upload_assets_route(project_id: str, files: list[UploadFile] = File(...), session: SessionCookie = None):
    user = me_from_session(session)
    if len(files) > _MAX_UPLOAD_FILES:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "ASSET_VALIDATION_FAILED", "message": f"파일은 최대 {_MAX_UPLOAD_FILES}개까지 업로드할 수 있습니다."}},
        )
    payload = []
    for file in files:
        data = await file.read()
        if len(data) > _MAX_FILE_BYTES:
            raise HTTPException(
                status_code=400,
                detail={"error": {"code": "ASSET_VALIDATION_FAILED", "message": "파일 하나의 크기는 10MB 이하여야 합니다."}},
            )
        payload.append((file.filename or "upload.png", data, file.content_type or "image/png"))
    return upload_assets(project_id, payload, user["id"])


@router.post("/projects/{project_id}/generate", response_model=GenerationRunResponse, status_code=status.HTTP_202_ACCEPTED)
def generate_route(project_id: str, payload: GenerateRequest, background_tasks: BackgroundTasks, session: SessionCookie = None):
    user = me_from_session(session)
    result = start_generation(project_id, payload.model_dump(), user["id"])
    background_tasks.add_task(run_generation_background, project_id, result["generationRunId"])
    return result


@router.post("/projects/{project_id}/regenerate", response_model=GenerationRunResponse, status_code=status.HTTP_202_ACCEPTED)
def regenerate_route(project_id: str, payload: RegenerateRequest, background_tasks: BackgroundTasks, session: SessionCookie = None):
    user = me_from_session(session)
    result = regenerate_project(project_id, payload.model_dump(), user["id"])
    background_tasks.add_task(run_generation_background, project_id, result["generationRunId"])
    return result


@router.get("/projects/{project_id}/status", response_model=GenerationStatusResponse)
def generation_status_route(project_id: str, session: SessionCookie = None):
    user = me_from_session(session)
    return get_generation_status(project_id, user["id"])


@router.get("/projects/{project_id}/result", response_model=ProjectResultResponse)
def result_route(project_id: str, session: SessionCookie = None):
    user = me_from_session(session)
    return get_project_result(project_id, user["id"])


@router.get("/hybrid-candidates/approved", response_model=ApprovedHybridInventoryResponse)
def approved_hybrid_candidates_route(
    label: str | None = None,
    service_lane: str | None = Query(default=None, alias="serviceLane"),
):
    return get_approved_hybrid_inventory(label=label, service_lane=service_lane)


@router.post("/projects/{project_id}/publish", response_model=PublishResponse, status_code=status.HTTP_202_ACCEPTED)
def publish_route(project_id: str, payload: PublishRequest, background_tasks: BackgroundTasks, session: SessionCookie = None):
    user = me_from_session(session)
    result = publish_project(project_id, payload.model_dump(), user["id"])
    if result["status"] == "queued":
        background_tasks.add_task(run_publish_background, result["uploadJobId"])
    return result


@router.get("/projects/{project_id}/latest-upload-job", response_model=UploadJobResponse | None)
def latest_upload_job_route(project_id: str, session: SessionCookie = None):
    user = me_from_session(session)
    return get_latest_upload_job(project_id, user["id"])


@router.get("/projects/{project_id}/upload-jobs", response_model=UploadJobListResponse)
def project_upload_jobs_route(project_id: str, session: SessionCookie = None):
    user = me_from_session(session)
    return {"items": list_project_upload_jobs(project_id, user["id"])}


@router.get("/upload-jobs/{job_id}", response_model=UploadJobResponse)
def upload_job_route(job_id: str, session: SessionCookie = None):
    user = me_from_session(session)
    return get_upload_job(job_id, user["id"])


@router.post("/upload-jobs/{job_id}/assist-complete", response_model=AssistCompleteResponse)
def assist_complete_route(job_id: str, payload: AssistCompleteRequest | None = None, session: SessionCookie = None):
    user = me_from_session(session)
    completed_at = payload.completedAt.isoformat() if payload else None
    return mark_assist_complete(job_id, completed_at, user["id"])


@router.get("/social-accounts", response_model=SocialAccountsResponse)
def social_accounts_route(session: SessionCookie = None):
    user = me_from_session(session)
    return list_social_accounts(user["id"])


@router.post("/social-accounts/{channel}/connect", response_model=ConnectSocialAccountResponse)
def social_connect_route(channel: str, session: SessionCookie = None):
    user = me_from_session(session)
    return connect_social_account(channel, user["id"])


@router.get("/social-accounts/{channel}/callback", response_model=SocialAccountCallbackResponse)
def social_callback_route(channel: str, code: str | None = None, state: str | None = None, session: SessionCookie = None):
    user = me_from_session(session)
    return callback_social_account(channel, code, state, user["id"])


@router.get("/social-accounts/{channel}/token")
def social_token_route(channel: str, session: SessionCookie = None):
    """
    Return a valid access token for the given channel.
    Used internally by the automation/worker team — requires an authenticated session.
    """
    user = me_from_session(session)
    try:
        token = get_valid_access_token(user["id"], channel)
        return {"channel": channel, "accessToken": token}
    except NotConnectedError as exc:
        raise HTTPException(status_code=400, detail={"error": {"code": "NOT_CONNECTED", "message": str(exc)}}) from exc
