import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

export type ScenePlanScene = {
  sceneId: string;
  slot: string;
  textRole: string;
  mediaRole: string;
  sceneRole: string;
  durationSec: number;
  asset: {
    storagePath: string;
    derivativeType: string;
  };
  copy: {
    primaryText: string;
    secondaryText: string;
    headline: string;
    body: string;
    kicker: string;
    cta: string;
    badgeText: string;
    stampText: string;
  };
  renderHints: {
    layoutHint: string;
    effects: string[];
    motionPreset?: string | null;
    captionLength?: string | null;
    safeArea?: Record<string, number>;
    palette?: {
      background?: string | null;
      surface?: string | null;
      accent?: string | null;
      textPrimary?: string | null;
      textOnSurface?: string | null;
    };
    typography?: {
      headlineSize?: number | null;
      bodySize?: number | null;
      ctaSize?: number | null;
      fontFamily?: string | null;
    };
  };
};

export type ScenePlanPayload = {
  sceneSpecVersion: string;
  templateId: string;
  templateTitle: string;
  purpose: string;
  styleId: string;
  businessType: string;
  regionName: string;
  durationSec: number;
  sceneCount: number;
  scenes: ScenePlanScene[];
};

type ProjectResultScenePlanMeta = {
  url: string;
  sceneCount?: number | null;
  sceneSpecVersion?: string | null;
};

type ProjectResultCopyPolicyMeta = {
  detailLocationPolicyId: string | null;
  forbiddenDetailLocationSurfaces: string[];
  guardActive: boolean;
  emphasizeRegionRequested: boolean;
  detailLocationPresent: boolean;
};

type ProjectResultSceneLayerSummary = {
  templateId: string;
  items: Array<{
    sceneId: string;
    slotGroup: "hook" | "body" | "cta";
    textRole: string;
    uiLabel: string;
  }>;
};

type ProjectResultPayload = {
  projectId: string;
  scenePlan?: ProjectResultScenePlanMeta | null;
  sceneLayerSummary?: ProjectResultSceneLayerSummary | null;
  copyPolicy?: ProjectResultCopyPolicyMeta | null;
};

type PromptArtifact = {
  results?: Array<{
    variant_id: string;
    scene_plan?: ScenePlanPayload;
  }>;
};

type ScenePlanArtifactDefinition = {
  title: string;
  templateId: string;
  purpose: string;
  artifactPath: string;
  variantId: string;
  recommendedSceneIds: string[];
};

const REPO_ROOT = resolve(process.cwd(), "..", "..");

const SCENE_PLAN_ARTIFACTS = {
  "exp15-promotion-bgrade-tone": {
    title: "T02 Promotion · B급 톤",
    templateId: "T02",
    purpose: "promotion",
    artifactPath: "docs/experiments/artifacts/exp-15-gemma-4-prompt-lever-experiment-service-aligned-b-grade-tone.json",
    variantId: "explicit_b_grade_tone_guidance",
    recommendedSceneIds: ["s1", "s4"],
  },
  "exp18-review-region-repeat": {
    title: "T04 Review · 지역 반복 제약",
    templateId: "T04",
    purpose: "review",
    artifactPath: "docs/experiments/artifacts/exp-18-gemma-4-prompt-lever-experiment-review-region-repeat-constraint.json",
    variantId: "explicit_review_region_repeat_constraint",
    recommendedSceneIds: ["s1", "s3"],
  },
  "exp19-review-cta-strength": {
    title: "T04 Review · CTA 강도",
    templateId: "T04",
    purpose: "review",
    artifactPath: "docs/experiments/artifacts/exp-19-gemma-4-prompt-lever-experiment-review-cta-strength.json",
    variantId: "explicit_review_cta_strength",
    recommendedSceneIds: ["s1", "s3"],
  },
} satisfies Record<string, ScenePlanArtifactDefinition>;

export type ScenePlanArtifactKey = keyof typeof SCENE_PLAN_ARTIFACTS;

export function listScenePlanArtifacts() {
  return Object.entries(SCENE_PLAN_ARTIFACTS).map(([key, value]) => ({
    key,
    ...value,
  }));
}

export async function loadScenePlanArtifact(key: string) {
  const artifact = SCENE_PLAN_ARTIFACTS[key as ScenePlanArtifactKey];
  if (!artifact) {
    return null;
  }

  const filePath = resolve(REPO_ROOT, artifact.artifactPath);
  const payload = JSON.parse(await readFile(filePath, "utf8")) as PromptArtifact;
  const result = payload.results?.find((item) => item.variant_id === artifact.variantId);

  if (!result?.scene_plan) {
    return null;
  }

  return {
    key,
    ...artifact,
    scenePlan: result.scene_plan,
  };
}

function normalizeBaseUrl(baseUrl: string) {
  return baseUrl.replace(/\/$/, "");
}

export function resolveProjectApiBaseUrl(requestBaseUrl: string) {
  return normalizeBaseUrl(process.env.NEXT_PUBLIC_API_BASE_URL?.trim() || requestBaseUrl);
}

export async function loadProjectScenePlan(projectId: string, requestBaseUrl: string) {
  const requestOrigin = normalizeBaseUrl(requestBaseUrl);
  const resultUrl = new URL(`/api/projects/${projectId}/result`, `${requestOrigin}/`).toString();
  const resultResponse = await fetch(resultUrl, { cache: "no-store" });
  if (!resultResponse.ok) {
    return null;
  }

  const result = (await resultResponse.json()) as ProjectResultPayload;
  if (!result.scenePlan?.url) {
    return null;
  }

  const scenePlanUrl = new URL(result.scenePlan.url, `${requestOrigin}/`).toString();
  const scenePlanResponse = await fetch(scenePlanUrl, { cache: "no-store" });
  if (!scenePlanResponse.ok) {
    return null;
  }

  return {
    projectId,
    apiBaseUrl: requestOrigin,
    scenePlanUrl,
    scenePlan: (await scenePlanResponse.json()) as ScenePlanPayload,
    sceneLayerSummary: result.sceneLayerSummary ?? null,
    copyPolicy: result.copyPolicy ?? null,
  };
}
