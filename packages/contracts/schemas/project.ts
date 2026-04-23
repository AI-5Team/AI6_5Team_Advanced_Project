import type { BusinessType } from "../enums/businessType";
import type { Channel } from "../enums/channel";
import type { Purpose } from "../enums/purpose";
import type { ProjectStatus } from "../enums/status";
import type { Style } from "../enums/style";
import type { PaginationResponse, ProjectSummary } from "./common";

export interface CreateProjectRequest {
  businessType: BusinessType;
  regionName: string;
  detailLocation?: string | null;
  purpose: Purpose;
  style: Style;
  channels: Channel[];
}

export interface CreateProjectResponse {
  projectId: string;
  status: Extract<ProjectStatus, "draft">;
  createdAt: string;
}

export interface GetProjectResponse {
  projectId: string;
  businessType: BusinessType;
  regionName: string;
  detailLocation: string | null;
  purpose: Purpose;
  style: Style;
  channels: Channel[];
  status: ProjectStatus;
  assetCount: number;
  latestGenerationRunId?: string | null;
  createdAt?: string;
  updatedAt?: string;
}

export interface StoreProfileResponse {
  storeProfileId: string | null;
  businessType: BusinessType | null;
  regionName: string | null;
  detailLocation: string | null;
  defaultStyle: Style | null;
}

export interface UpdateStoreProfileRequest {
  businessType: BusinessType;
  regionName: string;
  detailLocation?: string | null;
  defaultStyle?: Style | null;
}

export interface UpdateStoreProfileResponse {
  storeProfileId: string;
  updated: true;
}

export type ListProjectsResponse = PaginationResponse<ProjectSummary>;
