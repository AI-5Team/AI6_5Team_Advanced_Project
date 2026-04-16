import type {
  AuthResponse,
  CreateProjectRequest,
  CreateProjectResponse,
  GenerationStatusResponse,
  GetProjectResponse,
  LoginRequest,
  MeResponse,
  ProjectResultResponse,
  ProjectSummary,
  PublishProjectRequest,
  PublishProjectResponse,
  RegisterRequest,
  SocialAccountsResponse,
  StoreProfileResponse,
  UpdateStoreProfileRequest,
  UploadAssetsResponse,
  UploadedAssetItem,
  UploadJobResponse,
  GenerateProjectRequest,
  RegenerateProjectRequest,
  ApprovedHybridInventoryResponse,
} from "./contracts";
import { buildAuthHeaders } from "@/lib/auth";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim() ?? "";

function urlFor(path: string) {
  if (!apiBaseUrl) return path;
  return `${apiBaseUrl.replace(/\/$/, "")}${path.startsWith("/") ? path : `/${path}`}`;
}

function buildRequestHeaders(init?: RequestInit) {
  const headers = new Headers(init?.headers);
  const authHeaders = buildAuthHeaders();
  Object.entries(authHeaders).forEach(([key, value]) => {
    headers.set(key, value);
  });
  if (!(init?.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  return headers;
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(urlFor(path), {
    ...init,
    headers: buildRequestHeaders(init),
    cache: "no-store",
  });

  if (!response.ok) {
    const data = (await response.json().catch(() => null)) as { error?: { message?: string } } | null;
    throw new Error(data?.error?.message ?? `HTTP ${response.status}`);
  }

  return (await response.json()) as T;
}

export function getApiSourceLabel() {
  return apiBaseUrl ? apiBaseUrl : "local demo API";
}

export function registerUser(payload: RegisterRequest) {
  return requestJson<AuthResponse>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function loginUser(payload: LoginRequest) {
  return requestJson<AuthResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getMe() {
  return requestJson<MeResponse>("/api/me");
}

export async function logoutUser() {
  const response = await fetch(urlFor("/api/auth/logout"), {
    method: "POST",
    headers: new Headers(buildAuthHeaders()),
    cache: "no-store",
  });
  if (!response.ok && response.status !== 204) {
    const data = (await response.json().catch(() => null)) as { error?: { message?: string } } | null;
    throw new Error(data?.error?.message ?? `HTTP ${response.status}`);
  }
}

export function listProjects(status?: string) {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return requestJson<{ items: ProjectSummary[]; nextCursor: string | null; hasNext: boolean }>(`/api/projects${query}`);
}

export function createProject(payload: CreateProjectRequest) {
  return requestJson<CreateProjectResponse>("/api/projects", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getProjectDetail(projectId: string) {
  return requestJson<GetProjectResponse>(`/api/projects/${projectId}`);
}

export function getProjectAssets(projectId: string) {
  return requestJson<{ projectId: string; assets: UploadedAssetItem[] }>(`/api/projects/${projectId}/assets`);
}

export function uploadAssets(projectId: string, files: File[]) {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  return requestJson<UploadAssetsResponse>(`/api/projects/${projectId}/assets`, {
    method: "POST",
    body: formData,
  });
}

export function startGeneration(projectId: string, payload: GenerateProjectRequest) {
  return requestJson<{ generationRunId: string; projectId: string; status: "queued" }>(`/api/projects/${projectId}/generate`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function regenerateProject(projectId: string, payload: RegenerateProjectRequest) {
  return requestJson<{ generationRunId: string; projectId: string; status: "queued" }>(`/api/projects/${projectId}/regenerate`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listApprovedHybridCandidates(params?: { label?: string; serviceLane?: string }) {
  const query = new URLSearchParams();
  if (params?.label) query.set("label", params.label);
  if (params?.serviceLane) query.set("serviceLane", params.serviceLane);
  const suffix = query.size ? `?${query.toString()}` : "";
  return requestJson<ApprovedHybridInventoryResponse>(`/api/hybrid-candidates/approved${suffix}`);
}

export function getGenerationStatus(projectId: string) {
  return requestJson<GenerationStatusResponse>(`/api/projects/${projectId}/status`);
}

export function getProjectResult(projectId: string) {
  return requestJson<ProjectResultResponse>(`/api/projects/${projectId}/result`);
}

export function publishProject(projectId: string, payload: PublishProjectRequest) {
  return requestJson<PublishProjectResponse>(`/api/projects/${projectId}/publish`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getUploadJob(jobId: string) {
  return requestJson<UploadJobResponse>(`/api/upload-jobs/${jobId}`);
}

export async function getLatestUploadJobForProject(projectId: string) {
  const response = await fetch(`/api/projects/${projectId}/latest-upload-job`, {
    headers: new Headers(buildAuthHeaders()),
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return (await response.json()) as UploadJobResponse | null;
}

export async function listProjectUploadJobs(projectId: string) {
  const response = await fetch(`/api/projects/${projectId}/upload-jobs`, {
    headers: new Headers(buildAuthHeaders()),
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return (await response.json()) as { items: UploadJobResponse[] };
}

export function completeAssist(jobId: string) {
  return requestJson<UploadJobResponse>(`/api/upload-jobs/${jobId}/assist-complete`, {
    method: "POST",
  });
}

export function getSocialAccounts() {
  return requestJson<SocialAccountsResponse>("/api/social-accounts");
}

export function connectSocialAccount(channel: string) {
  return requestJson<{ channel: string; status: "connecting"; redirectUrl: string }>(`/api/social-accounts/${channel}/connect`, {
    method: "POST",
  });
}

export function callbackSocialAccount(channel: string, params?: { code?: string; state?: string }) {
  const query = new URLSearchParams();
  if (params?.code) query.set("code", params.code);
  if (params?.state) query.set("state", params.state);
  const suffix = query.size ? `?${query.toString()}` : "";
  return requestJson<{ channel: string; status: "connected"; socialAccountId: string }>(`/api/social-accounts/${channel}/callback${suffix}`);
}

export function getStoreProfile() {
  return requestJson<StoreProfileResponse>("/api/store-profile");
}

export function updateStoreProfile(payload: UpdateStoreProfileRequest) {
  return requestJson<StoreProfileResponse>("/api/store-profile", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}
