from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ErrorEnvelope(ApiModel):
    error: dict[str, Any]


class UserPayload(ApiModel):
    id: str
    email: str
    name: str


class RegisterRequest(ApiModel):
    email: str
    password: str = Field(min_length=10, max_length=1024)
    name: str = Field(min_length=1, max_length=100)
    birthDate: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    agreedToTerms: Literal[True]
    agreedToPrivacy: Literal[True]
    agreedToAge14: Literal[True]
    agreedToOverseasTransfer: Literal[True]


class LoginRequest(ApiModel):
    email: str
    password: str = Field(min_length=1)


class AuthResponse(ApiModel):
    accessToken: str
    user: UserPayload


class SessionResponse(ApiModel):
    user: UserPayload


class VerifyEmailRequest(ApiModel):
    token: str


class PasswordResetRequest(ApiModel):
    email: str


class PasswordResetConfirmRequest(ApiModel):
    token: str
    newPassword: str = Field(min_length=10, max_length=1024)


class ChangePasswordRequest(ApiModel):
    currentPassword: str = Field(min_length=1)
    newPassword: str = Field(min_length=10, max_length=1024)


class AccountDeleteResponse(ApiModel):
    deleted: Literal[True]


class StoreProfileRequest(ApiModel):
    businessType: Literal["cafe", "restaurant"]
    regionName: str = Field(min_length=2, max_length=20)
    detailLocation: str | None = Field(default=None, max_length=30)
    defaultStyle: Literal["default", "friendly", "b_grade_fun"] | None = None


class StoreProfileResponse(ApiModel):
    storeProfileId: str
    businessType: Literal["cafe", "restaurant"]
    regionName: str
    detailLocation: str | None = None
    defaultStyle: Literal["default", "friendly", "b_grade_fun"] | None = None


class UpdateStoreProfileResponse(ApiModel):
    storeProfileId: str
    updated: Literal[True]


class CreateProjectRequest(ApiModel):
    businessType: Literal["cafe", "restaurant"]
    regionName: str = Field(min_length=2, max_length=20)
    detailLocation: str | None = Field(default=None, max_length=30)
    purpose: Literal["new_menu", "promotion", "review", "location_push"]
    style: Literal["default", "friendly", "b_grade_fun"]
    channels: list[Literal["instagram", "youtube_shorts", "tiktok"]] = Field(min_length=1)


class CreateProjectResponse(ApiModel):
    projectId: str
    status: Literal["draft"]
    createdAt: datetime


class ProjectSummary(ApiModel):
    projectId: str
    businessType: str
    purpose: str
    style: str
    status: str
    createdAt: datetime


class ProjectListResponse(ApiModel):
    items: list[ProjectSummary]
    nextCursor: str | None
    hasNext: bool


class ProjectDetailResponse(ApiModel):
    projectId: str
    businessType: str
    regionName: str
    detailLocation: str | None
    purpose: str
    style: str
    channels: list[str]
    status: str
    assetCount: int


class AssetItem(ApiModel):
    assetId: str
    fileName: str
    width: int
    height: int
    warnings: list[str]


class UploadAssetsResponse(ApiModel):
    projectId: str
    assets: list[AssetItem]


class QuickOptions(ApiModel):
    highlightPrice: bool | None = None
    shorterCopy: bool | None = None
    emphasizeRegion: bool | None = None


class GenerateRequest(ApiModel):
    assetIds: list[str] = Field(min_length=1)
    templateId: str
    quickOptions: QuickOptions | None = None
    approvedHybridSourceCandidateKey: str | None = None


class RegenerateChangeSet(ApiModel):
    highlightPrice: bool | None = None
    shorterCopy: bool | None = None
    emphasizeRegion: bool | None = None
    templateId: str | None = None
    styleOverride: Literal["default", "friendly", "b_grade_fun"] | None = None
    approvedHybridSourceCandidateKey: str | None = None


class RegenerateRequest(ApiModel):
    changeSet: RegenerateChangeSet


class GenerationRunResponse(ApiModel):
    generationRunId: str
    projectId: str
    status: Literal["queued"]


class GenerationStep(ApiModel):
    name: str
    status: str


class GenerationResult(ApiModel):
    generationRunId: str
    variantId: str
    videoId: str
    postId: str
    copySetId: str
    previewVideoUrl: str
    previewImageUrl: str
    ctaText: str


class GenerationStatusResponse(ApiModel):
    projectId: str
    projectStatus: str
    steps: list[GenerationStep] | None = None
    result: GenerationResult | None = None
    error: dict[str, Any] | None = None


class ProjectResultResponse(ApiModel):
    projectId: str
    generationRunId: str
    variantId: str
    video: dict[str, Any]
    post: dict[str, Any]
    copySet: dict[str, Any]
    scenePlan: dict[str, Any] | None = None
    sceneLayerSummary: dict[str, Any] | None = None
    changeImpactSummary: dict[str, Any] | None = None
    copyPolicy: dict[str, Any] | None = None
    copyDeck: dict[str, Any] | None = None
    copyGeneration: dict[str, Any] | None = None
    promptBaselineSummary: dict[str, Any] | None = None
    rendererSummary: dict[str, Any] | None = None


class ApprovedHybridInventoryResponse(ApiModel):
    itemCount: int
    laneCounts: dict[str, int]
    labelCounts: dict[str, int]
    approvalSourceCounts: dict[str, int]
    recommendedByLane: dict[str, Any]
    recommendedByLabel: dict[str, Any]
    items: list[dict[str, Any]]


class PublishRequest(ApiModel):
    variantId: str
    channel: Literal["instagram", "youtube_shorts", "tiktok"]
    publishMode: Literal["auto", "assist"]
    captionOverride: str | None = None
    hashtags: list[str] | None = None
    thumbnailText: str | None = None


class AssistPackage(ApiModel):
    mediaUrl: str
    caption: str
    hashtags: list[str]
    thumbnailText: str | None = None


class PublishResponse(ApiModel):
    uploadJobId: str
    projectId: str
    status: Literal["queued", "assist_required"]
    assistPackage: AssistPackage | None = None


class UploadJobResponse(ApiModel):
    uploadJobId: str
    projectId: str
    channel: str
    status: str
    assistPackage: AssistPackage | None = None
    error: dict[str, Any] | None = None


class AssistCompleteRequest(ApiModel):
    confirmedByUser: Literal[True]
    completedAt: datetime


class AssistCompleteResponse(ApiModel):
    uploadJobId: str
    status: Literal["assisted_completed"]


class SocialAccountSummary(ApiModel):
    channel: str
    status: str
    accountName: str | None = None
    lastSyncedAt: datetime | None = None


class SocialAccountsResponse(ApiModel):
    items: list[SocialAccountSummary]


class ConnectSocialAccountResponse(ApiModel):
    channel: str
    status: Literal["connecting"]
    redirectUrl: str


class SocialAccountCallbackResponse(ApiModel):
    channel: str
    status: Literal["connected"]
    socialAccountId: str
