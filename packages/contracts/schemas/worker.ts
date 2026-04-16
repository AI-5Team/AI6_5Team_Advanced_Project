import type { BusinessType } from "../enums/businessType";
import type { Channel } from "../enums/channel";
import type { Purpose } from "../enums/purpose";
import type { Style } from "../enums/style";

export interface PreprocessJobPayload {
  jobId: string;
  projectId: string;
  assetIds: string[];
  businessType: BusinessType;
}

export interface CopyGenerationJobPayload {
  jobId: string;
  projectId: string;
  purpose: Purpose;
  style: Style;
  regionName: string;
  templateId: string;
}

export interface VideoRenderJobPayload {
  jobId: string;
  projectId: string;
  templateId: string;
  sceneSpecVersion: string;
  variantId: string;
  processedAssetIds: string[];
  copySetId: string;
}

export interface PublishJobPayload {
  uploadJobId: string;
  projectId: string;
  variantId: string;
  channel: Channel;
  publishMode: "auto" | "assist";
  mediaUrl: string;
  caption: string;
  hashtags: string[];
  thumbnailText?: string | null;
  socialAccountId: string | null;
}

export interface ScheduleDispatchJobPayload {
  scheduleJobId: string;
  projectId: string;
  variantId: string;
  channel: Channel;
  publishAt: string;
}
