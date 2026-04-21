from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, Header, Query, Response, UploadFile, status

from app.schemas.api import (
    ApprovedHybridInventoryResponse,
    AssistCompleteRequest,
    AssistCompleteResponse,
    AuthResponse,
    ConnectSocialAccountResponse,
    CreateProjectRequest,
    CreateProjectResponse,
    GenerateRequest,
    GenerationRunResponse,
    GenerationStatusResponse,
    LoginRequest,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectResultResponse,
    PublishRequest,
    PublishResponse,
    RegisterRequest,
    RegenerateRequest,
    SocialAccountCallbackResponse,
    SocialAccountsResponse,
    StoreProfileRequest,
    StoreProfileResponse,
    UpdateStoreProfileResponse,
    UploadAssetsResponse,
    UploadJobResponse,
)
from app.services.runtime import (
    callback_social_account,
    connect_social_account,
    create_project,
    get_approved_hybrid_inventory,
    get_current_user_from_authorization,
    get_generation_status,
    get_project_detail,
    get_project_result,
    get_store_profile,
    get_upload_job,
    list_assets,
    list_projects,
    list_social_accounts,
    login_user,
    mark_assist_complete,
    me_from_token,
    publish_project,
    register_user,
    regenerate_project,
    run_generation_background,
    run_publish_background,
    start_generation,
    update_store_profile,
    upload_assets,
)


router = APIRouter(prefix="/api")
AuthorizationHeader = Annotated[str | None, Header(alias="Authorization")]

CurrentUser = dict[str, str]

def require_current_user(authorization: AuthorizationHeader) -> CurrentUser:
    return get_current_user_from_authorization(authorization)


@router.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest):
    return register_user(payload.email, payload.password, payload.name)


@router.post("/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest):
    return login_user(payload.email, payload.password)


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout() -> Response:
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me")
def get_me(authorization: AuthorizationHeader = None):
    return me_from_token(authorization)


@router.get("/store-profile", response_model=StoreProfileResponse)
def store_profile(authorization: AuthorizationHeader = None):
    user = get_current_user_from_authorization(authorization)
    return get_store_profile(user["id"])


@router.put("/store-profile", response_model=UpdateStoreProfileResponse)
def save_store_profile(payload: StoreProfileRequest, authorization: AuthorizationHeader = None):
    user = get_current_user_from_authorization(authorization)
    return update_store_profile(payload.model_dump(), user["id"])


@router.post("/projects", response_model=CreateProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project_route(payload: CreateProjectRequest, authorization: AuthorizationHeader = None):
    user = get_current_user_from_authorization(authorization)
    return create_project(payload.model_dump(), user["id"])


@router.get("/projects", response_model=ProjectListResponse)
def list_projects_route(authorization: AuthorizationHeader = None, status: str | None = None):
    user = get_current_user_from_authorization(authorization)
    return list_projects(user["id"], status)


@router.get("/projects/{project_id}", response_model=ProjectDetailResponse)
def get_project_route(project_id: str, authorization: AuthorizationHeader = None):
    user = get_current_user_from_authorization(authorization)
    return get_project_detail(project_id, user["id"])


@router.get("/projects/{project_id}/assets", response_model=UploadAssetsResponse)
def list_assets_route(project_id: str, authorization: AuthorizationHeader = None):
    get_current_user_from_authorization(authorization)
    return {"projectId": project_id, "assets": list_assets(project_id)}


@router.post("/projects/{project_id}/assets", response_model=UploadAssetsResponse, status_code=status.HTTP_201_CREATED)
async def upload_assets_route(project_id: str, files: list[UploadFile] = File(...), authorization: AuthorizationHeader = None):
    get_current_user_from_authorization(authorization)
    payload = [(file.filename or "upload.png", await file.read(), file.content_type or "image/png") for file in files]
    return upload_assets(project_id, payload)


@router.post("/projects/{project_id}/generate", response_model=GenerationRunResponse, status_code=status.HTTP_202_ACCEPTED)
def generate_route(project_id: str, payload: GenerateRequest, background_tasks: BackgroundTasks, authorization: AuthorizationHeader = None):
    get_current_user_from_authorization(authorization)
    result = start_generation(project_id, payload.model_dump())
    background_tasks.add_task(run_generation_background, project_id, result["generationRunId"])
    return result


@router.post("/projects/{project_id}/regenerate", response_model=GenerationRunResponse, status_code=status.HTTP_202_ACCEPTED)
def regenerate_route(project_id: str, payload: RegenerateRequest, background_tasks: BackgroundTasks, authorization: AuthorizationHeader = None):
    get_current_user_from_authorization(authorization)
    result = regenerate_project(project_id, payload.model_dump())
    background_tasks.add_task(run_generation_background, project_id, result["generationRunId"])
    return result


@router.get("/projects/{project_id}/status", response_model=GenerationStatusResponse)
def generation_status_route(project_id: str, authorization: AuthorizationHeader = None):
    get_current_user_from_authorization(authorization)
    return get_generation_status(project_id)


@router.get("/projects/{project_id}/result", response_model=ProjectResultResponse)
def result_route(project_id: str, authorization: AuthorizationHeader = None):
    get_current_user_from_authorization(authorization)
    return get_project_result(project_id)


@router.post("/projects/{project_id}/publish", response_model=PublishResponse, status_code=status.HTTP_202_ACCEPTED)
def publish_route(project_id: str, payload: PublishRequest, background_tasks: BackgroundTasks, authorization: AuthorizationHeader = None):
    user = get_current_user_from_authorization(authorization)
    result = publish_project(project_id, payload.model_dump(), user["id"])
    if result["status"] == "queued":
        background_tasks.add_task(run_publish_background, result["uploadJobId"])
    return result


@router.get("/upload-jobs/{job_id}", response_model=UploadJobResponse)
def upload_job_route(job_id: str, authorization: AuthorizationHeader = None):
    get_current_user_from_authorization(authorization)
    return get_upload_job(job_id)


@router.post("/upload-jobs/{job_id}/assist-complete", response_model=AssistCompleteResponse)
def assist_complete_route(job_id: str, authorization: AuthorizationHeader = None, payload: AssistCompleteRequest | None = None):
    get_current_user_from_authorization(authorization)
    completed_at = payload.completedAt.isoformat() if payload else None
    return mark_assist_complete(job_id, completed_at)


@router.get("/social-accounts", response_model=SocialAccountsResponse)
def social_accounts_route(authorization: AuthorizationHeader = None):
    user = get_current_user_from_authorization(authorization)
    return list_social_accounts(user["id"])


@router.post("/social-accounts/{channel}/connect", response_model=ConnectSocialAccountResponse)
def social_connect_route(channel: str, authorization: AuthorizationHeader = None):
    user = get_current_user_from_authorization(authorization)
    return connect_social_account(channel, user["id"])


@router.get("/social-accounts/{channel}/callback", response_model=SocialAccountCallbackResponse)
def social_callback_route(channel: str, authorization: AuthorizationHeader = None, code: str | None = None, state: str | None = None):
    user = get_current_user_from_authorization(authorization)
    return callback_social_account(channel, code, state, user["id"])
