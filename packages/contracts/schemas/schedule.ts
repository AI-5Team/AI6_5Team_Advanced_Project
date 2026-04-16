import type { Channel } from "../enums/channel";
import type { ScheduleJobStatus } from "../enums/status";
import type { ErrorResponse } from "./common";

export interface ScheduleProjectRequest {
  variantId: string;
  channel: Channel;
  publishAt: string;
  captionOverride?: string | null;
  hashtags?: string[];
}

export interface ScheduleProjectResponse {
  scheduleJobId: string;
  projectId: string;
  status: "scheduled";
}

export interface ScheduleJobResponse {
  scheduleJobId: string;
  projectId: string;
  channel: Channel;
  status: ScheduleJobStatus;
  publishAt: string;
  error?: ErrorResponse["error"] | null;
}
