export const PROJECT_STATUSES = [
  "draft",
  "queued",
  "preprocessing",
  "generating",
  "generated",
  "upload_assist",
  "scheduled",
  "publishing",
  "published",
  "failed",
] as const;

export type ProjectStatus = (typeof PROJECT_STATUSES)[number];

export const GENERATION_RUN_STATUSES = [
  "queued",
  "processing",
  "completed",
  "failed",
] as const;

export type GenerationRunStatus = (typeof GENERATION_RUN_STATUSES)[number];

export const GENERATION_STEP_NAMES = [
  "preprocessing",
  "copy_generation",
  "video_rendering",
  "post_rendering",
  "packaging",
] as const;

export type GenerationStepName = (typeof GENERATION_STEP_NAMES)[number];

export const GENERATION_STEP_STATUSES = [
  "pending",
  "processing",
  "completed",
  "failed",
  "skipped",
] as const;

export type GenerationStepStatus = (typeof GENERATION_STEP_STATUSES)[number];

export const UPLOAD_JOB_STATUSES = [
  "queued",
  "publishing",
  "published",
  "failed",
  "retrying",
  "assist_required",
  "assisted_completed",
] as const;

export type UploadJobStatus = (typeof UPLOAD_JOB_STATUSES)[number];

export const SCHEDULE_JOB_STATUSES = [
  "scheduled",
  "queued",
  "publishing",
  "published",
  "failed",
  "cancelled",
] as const;

export type ScheduleJobStatus = (typeof SCHEDULE_JOB_STATUSES)[number];

export const SOCIAL_ACCOUNT_STATUSES = [
  "not_connected",
  "connecting",
  "connected",
  "expired",
  "permission_error",
] as const;

export type SocialAccountStatus = (typeof SOCIAL_ACCOUNT_STATUSES)[number];

export const ERROR_CODES = [
  "INVALID_INPUT",
  "INVALID_CREDENTIALS",
  "PROJECT_NOT_FOUND",
  "UNSUPPORTED_CHANNEL",
  "ASSET_VALIDATION_FAILED",
  "PREPROCESS_FAILED",
  "COPY_GENERATION_FAILED",
  "RENDER_FAILED",
  "AUTH_REQUIRED",
  "SOCIAL_TOKEN_EXPIRED",
  "PUBLISH_FAILED",
  "SCHEDULE_INVALID",
  "OAUTH_CALLBACK_INVALID",
  "IDEMPOTENCY_CONFLICT",
  "INVALID_STATE_TRANSITION",
] as const;

export type ErrorCode = (typeof ERROR_CODES)[number];
