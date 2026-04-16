import {
  BUSINESS_TYPES,
  CHANNELS,
  CHANNEL_SUPPORT_TIERS,
  ERROR_CODES,
  GENERATION_STEP_NAMES,
  GENERATION_STEP_STATUSES,
  PROJECT_STATUSES,
  PURPOSES,
  SOCIAL_ACCOUNT_STATUSES,
  STYLES,
  UPLOAD_JOB_STATUSES,
  type AssetWarningCode,
  type AuthResponse,
  type AuthUser,
  type BusinessType,
  type Channel,
  type ConnectSocialAccountResponse,
  type CreateProjectRequest,
  type CreateProjectResponse,
  type ChangeSet as ContractChangeSet,
  type ErrorCode,
  type ErrorResponse,
  type GenerateProjectRequest as ContractGenerateProjectRequest,
  type GenerateProjectResponse as ContractGenerateProjectResponse,
  type GenerationStep,
  type GenerationStepName,
  type GenerationStepStatus,
  type GetProjectResponse,
  type LoginRequest,
  type MeResponse,
  type ProjectResultResponse,
  type ProjectStatus,
  type ProjectSummary,
  type PublishProjectRequest,
  type PublishProjectResponse,
  type Purpose,
  type RegisterRequest,
  type SocialAccountCallbackResponse,
  type SocialAccountStatus,
  type SocialAccountSummary,
  type SocialAccountsResponse,
  type StoreProfileResponse,
  type Style,
  type UpdateStoreProfileRequest,
  type UploadedAssetItem,
  type UploadAssetsResponse,
  type UploadJobResponse as ContractUploadJobResponse,
  type UploadJobStatus,
  type UploadJobSummary as ContractUploadJobSummary,
  type AssistPackage,
} from "@ai65/contracts";
import reviewCopyRule from "../../../../packages/template-spec/copy-rules/review.json";
import promotionCopyRule from "../../../../packages/template-spec/copy-rules/promotion.json";
import newMenuCopyRule from "../../../../packages/template-spec/copy-rules/new_menu.json";
import locationPushCopyRule from "../../../../packages/template-spec/copy-rules/location_push.json";
import bGradeFunStylePreset from "../../../../packages/template-spec/styles/b_grade_fun.json";
import defaultStylePreset from "../../../../packages/template-spec/styles/default.json";
import friendlyStylePreset from "../../../../packages/template-spec/styles/friendly.json";
import t01TemplateSpec from "../../../../packages/template-spec/templates/T01-new-menu.json";
import t02TemplateSpec from "../../../../packages/template-spec/templates/T02-promotion.json";
import t03TemplateSpec from "../../../../packages/template-spec/templates/T03-location-push.json";
import t04TemplateSpec from "../../../../packages/template-spec/templates/T04-review.json";

export {
  BUSINESS_TYPES,
  CHANNELS,
  ERROR_CODES,
  GENERATION_STEP_STATUSES,
  PROJECT_STATUSES,
  PURPOSES,
  SOCIAL_ACCOUNT_STATUSES,
  STYLES,
  UPLOAD_JOB_STATUSES,
};

export const STEP_NAMES = GENERATION_STEP_NAMES;
export const CHANNEL_TIERS = CHANNEL_SUPPORT_TIERS;

export type {
  AssetWarningCode,
  AuthResponse,
  AuthUser,
  BusinessType,
  Channel,
  ConnectSocialAccountResponse,
  CreateProjectRequest,
  CreateProjectResponse,
  ErrorCode,
  ErrorResponse,
  GenerationStep,
  GenerationStepName,
  GenerationStepStatus,
  GetProjectResponse,
  LoginRequest,
  MeResponse,
  ProjectResultResponse,
  ProjectStatus,
  ProjectSummary,
  PublishProjectRequest,
  PublishProjectResponse,
  Purpose,
  RegisterRequest,
  SocialAccountStatus,
  SocialAccountSummary,
  SocialAccountsResponse,
  StoreProfileResponse,
  Style,
  UpdateStoreProfileRequest,
  UploadedAssetItem,
  UploadAssetsResponse,
  UploadJobStatus,
};

export type CallbackSocialAccountResponse = SocialAccountCallbackResponse;

export const QUICK_ACTIONS = [
  { id: "highlightPrice", label: "가격 더 크게" },
  { id: "shorterCopy", label: "문구 더 짧게" },
  { id: "emphasizeRegion", label: "지역명 강조" },
  { id: "friendly", label: "더 친근하게" },
  { id: "fun", label: "더 웃기게" },
  { id: "template", label: "다른 템플릿으로" },
] as const;

export type TemplateId = "T01" | "T02" | "T03" | "T04";

export type QuickOptions = ContractGenerateProjectRequest["quickOptions"] extends infer T ? NonNullable<T> : never;

export type RegenerateChangeSet = Omit<ContractChangeSet, "templateId"> & {
  templateId?: TemplateId;
  styleOverride?: Style;
};

export type GenerateProjectRequest = Omit<ContractGenerateProjectRequest, "templateId" | "quickOptions"> & {
  assetIds: string[];
  templateId: TemplateId;
  quickOptions?: QuickOptions;
};

export type GenerateProjectResponse = ContractGenerateProjectResponse;

export interface RegenerateProjectRequest {
  changeSet: RegenerateChangeSet;
}

export type PublishAssistPackage = AssistPackage;
export type GenerateProjectInput = GenerateProjectRequest;

export interface ResultPayload {
  videoId: string;
  postId: string;
  copySetId: string;
  previewVideoUrl: string;
  previewImageUrl: string;
  ctaText: string;
}

export interface GenerationStatusResponse {
  projectId: string;
  projectStatus: ProjectStatus;
  steps: GenerationStep[];
  result?: ResultPayload | null;
  error?: ErrorResponse["error"] | null;
}

export type ResultPreview = ResultPayload;

export interface UploadJobSummary extends ContractUploadJobSummary {
  createdAt?: string | null;
  updatedAt?: string | null;
  publishedAt?: string | null;
}

export interface UploadJobResponse extends Omit<ContractUploadJobResponse, "assistPackage">, UploadJobSummary {
  assistPackage?: PublishAssistPackage | null;
}

export interface ApprovedHybridCandidateItem {
  candidateKey: string;
  serviceLane: string;
  approvalSource: string;
  selectionMode: string;
  benchmarkId: string;
  label: string;
  provider: string;
  gateDecision: string;
  gateReason: string;
  role: string;
  imagePath?: string | null;
  sourceVideoPath?: string | null;
  contactSheetPath?: string | null;
  summaryPath?: string | null;
  midFrameMse?: number | null;
  motionAvgRgbDiff?: number | null;
  reviewFinalDecision?: string | null;
  reviewDecisionPath?: string | null;
  reviewer?: string | null;
  reviewDecidedAt?: string | null;
}

export interface ApprovedHybridInventoryResponse {
  itemCount: number;
  laneCounts: Record<string, number>;
  labelCounts: Record<string, number>;
  approvalSourceCounts: Record<string, number>;
  recommendedByLane: Record<string, ApprovedHybridCandidateItem>;
  recommendedByLabel: Record<string, ApprovedHybridCandidateItem>;
  items: ApprovedHybridCandidateItem[];
}

export interface TemplateSceneSpec {
  sceneId: string;
  durationSec: number;
  slot: string;
  textRole: string;
  mediaRole: string;
  effects: string[];
}

export interface TemplateSpec {
  templateId: TemplateId;
  title: string;
  supportedBusinessTypes: BusinessType[];
  supportedPurposes: Purpose[];
  supportedStyles: Style[];
  description: string;
  durationSec: number;
  outputRatio: "9:16";
  scenes: TemplateSceneSpec[];
}

export interface StylePreset {
  styleId: Style;
  textTone: string;
  colorPreset: string;
  motionPreset: string;
  captionLength: string;
  allowedEffects: string[];
  forbiddenEffects: string[];
}

export interface CopyRule {
  purpose: Purpose;
  structure: string[];
  regionPolicy: {
    minSlots: number;
    maxRepeat: number;
  };
  locationPolicy?: {
    policyId: string;
    forbiddenDetailLocationSurfaces: string[];
  };
  templateIds?: string[];
  supportedQuickActions?: string[];
  captionRules: {
    minOptions: number;
    maxLength: number;
  };
  sampleHooks: string[];
}

export const TEMPLATES = [t01TemplateSpec, t02TemplateSpec, t03TemplateSpec, t04TemplateSpec] as TemplateSpec[];

export const STYLE_PRESETS = [defaultStylePreset, friendlyStylePreset, bGradeFunStylePreset] as StylePreset[];

export const COPY_RULES = [newMenuCopyRule, promotionCopyRule, locationPushCopyRule, reviewCopyRule] as CopyRule[];

export function findCopyRule(templateId: string | null | undefined, purpose: Purpose) {
  if (templateId) {
    const matchedByTemplate = COPY_RULES.find((rule) => rule.templateIds?.includes(templateId));
    if (matchedByTemplate) return matchedByTemplate;
  }
  return COPY_RULES.find((rule) => rule.purpose === purpose) ?? null;
}
