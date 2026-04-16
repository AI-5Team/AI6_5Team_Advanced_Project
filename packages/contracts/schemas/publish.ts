import type { Channel } from "../enums/channel";
import type { UploadJobStatus } from "../enums/status";
import type { ErrorResponse } from "./common";
import type { AssistPackage } from "./uploadAssist";

export type PublishMode = "auto" | "assist";

export interface PublishProjectRequest {
  variantId: string;
  channel: Channel;
  publishMode: PublishMode;
  captionOverride?: string | null;
  hashtags?: string[];
  thumbnailText?: string | null;
}

export interface PublishProjectResponse {
  uploadJobId: string;
  projectId: string;
  status: "queued" | "assist_required";
  assistPackage?: AssistPackage;
}

export interface UploadJobResponse {
  uploadJobId: string;
  projectId: string;
  channel: Channel;
  status: UploadJobStatus;
  assistPackage?: AssistPackage | null;
  error: ErrorResponse["error"] | null;
}
