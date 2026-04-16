import type {
  ErrorCode,
  GenerationStepName,
  GenerationRunStatus,
  GenerationStepStatus,
  ProjectStatus,
  ScheduleJobStatus,
  SocialAccountStatus,
  UploadJobStatus,
} from "../enums/status";
import type { Channel, ChannelSupportTier } from "../enums/channel";
import type { BusinessType } from "../enums/businessType";
import type { Purpose } from "../enums/purpose";
import type { Style } from "../enums/style";

export interface ErrorResponse {
  error: {
    code: ErrorCode;
    message: string;
    details?: Record<string, unknown>;
  };
}

export interface PaginationRequest {
  cursor?: string | null;
  limit?: number;
}

export interface PaginationResponse<T> {
  items: T[];
  nextCursor: string | null;
  hasNext: boolean;
}

export interface GenerationStep {
  name: GenerationStepName;
  status: GenerationStepStatus;
}

export interface SocialAccountSummary {
  channel: Channel;
  status: SocialAccountStatus;
  accountName: string | null;
  lastSyncedAt: string | null;
  tier?: ChannelSupportTier;
}

export interface UploadJobSummary {
  uploadJobId: string;
  projectId: string;
  channel: Channel;
  status: UploadJobStatus;
  error: ErrorResponse["error"] | null;
}

export interface ScheduleJobSummary {
  scheduleJobId: string;
  projectId: string;
  channel: Channel;
  status: ScheduleJobStatus;
  publishAt: string;
  error?: ErrorResponse["error"] | null;
}

export interface ProjectSummary {
  projectId: string;
  businessType: BusinessType;
  purpose: Purpose;
  style: Style;
  status: ProjectStatus;
  createdAt: string;
}

export interface GenerationRunSummary {
  generationRunId: string;
  projectId: string;
  status: GenerationRunStatus;
  templateId?: string;
  startedAt?: string | null;
  finishedAt?: string | null;
  error?: ErrorResponse["error"] | null;
}
