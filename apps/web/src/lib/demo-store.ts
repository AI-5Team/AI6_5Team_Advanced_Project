import { randomUUID } from "crypto";
import {
  CHANNELS,
  COPY_RULES,
  STYLE_PRESETS,
  STEP_NAMES,
  TEMPLATES,
  findCopyRule,
  type AssetWarningCode,
  type BusinessType,
  type CallbackSocialAccountResponse,
  type Channel,
  type ConnectSocialAccountResponse,
  type CreateProjectRequest,
  type CreateProjectResponse,
  type GenerationStatusResponse,
  type GenerationStep,
  type GenerationStepName,
  type GenerateProjectInput,
  type GetProjectResponse,
  type ProjectResultResponse,
  type ProjectStatus,
  type ProjectSummary,
  type PublishAssistPackage,
  type PublishProjectRequest,
  type PublishProjectResponse,
  type QuickOptions,
  type RegenerateChangeSet,
  type SocialAccountStatus,
  type SocialAccountsResponse,
  type SocialAccountSummary,
  type StoreProfileResponse,
  type Style,
  type TemplateId,
  type UploadJobResponse,
  type UploadJobStatus,
  type UploadJobSummary,
  type UploadedAssetItem,
  type UpdateStoreProfileRequest,
} from "./contracts";
import { buildChangeImpactSummary } from "./change-impact";
import { buildPromptBaselineSummary } from "./prompt-baseline";
import type { ScenePlanPayload } from "./scene-plan";
import slotLayerMapManifest from "../../../../packages/template-spec/manifests/slot-layer-map.json";

type AssetRecord = UploadedAssetItem & {
  mimeType: string;
  fileSizeBytes: number;
  storagePath: string;
  createdAt: string;
  contentBase64: string | null;
};

type ProjectRecord = GetProjectResponse & {
  createdAt: string;
  updatedAt: string;
  latestGenerationRunId: string | null;
  selectedTemplateId: TemplateId | null;
  selectedAssetIds: string[];
  thumbnailText: string | null;
};

type GenerationRunRecord = {
  id: string;
  projectId: string;
  runType: "initial" | "regenerate";
  templateId: TemplateId;
  status: "queued" | "processing" | "completed" | "failed";
  errorCode: string | null;
  startedAt: string | null;
  finishedAt: string | null;
  createdAt: string;
  updatedAt: string;
  quickOptionsSnapshot: QuickOptions;
  changeSetSnapshot: RegenerateChangeSet;
  result: ProjectResultResponse | null;
  steps: Record<GenerationStepName, { status: GenerationStep["status"]; startedAt: string | null; finishedAt: string | null }>;
};

type UploadJobRecord = {
  id: string;
  projectId: string;
  variantId: string;
  channel: Channel;
  socialAccountId: string | null;
  status: UploadJobStatus;
  errorCode: string | null;
  requestPayload: PublishProjectRequest;
  assistPackage: PublishAssistPackage | null;
  retryCount: number;
  publishedAt: string | null;
  createdAt: string;
  updatedAt: string;
};

type SocialAccountRecord = {
  id: string;
  channel: Channel;
  status: SocialAccountStatus;
  accountName: string | null;
  lastSyncedAt: string | null;
  pendingState: string | null;
};

type StoreState = {
  storeProfile: StoreProfileResponse;
  projects: Map<string, ProjectRecord>;
  projectAssets: Map<string, AssetRecord[]>;
  generationRuns: Map<string, GenerationRunRecord>;
  uploadJobs: Map<string, UploadJobRecord>;
  socialAccounts: Map<Channel, SocialAccountRecord>;
};

declare global {
  // eslint-disable-next-line no-var
  var __snsDemoWebStore: StoreState | undefined;
}

function nowIso() {
  return new Date().toISOString();
}

function secondsAgo(seconds: number) {
  return new Date(Date.now() - seconds * 1000).toISOString();
}

function minutesAgo(minutes: number) {
  return new Date(Date.now() - minutes * 60 * 1000).toISOString();
}

function clone<T>(value: T): T {
  return structuredClone(value);
}

const templateMap = new Map(TEMPLATES.map((template) => [template.templateId, template]));
const stylePresetMap = new Map(STYLE_PRESETS.map((preset) => [preset.styleId, preset]));

const SCENE_PLAN_PALETTES = {
  default: {
    background: "#100f0d",
    surface: "#fff7ef",
    accent: "#e56a4c",
    textPrimary: "#fff7ef",
    textOnSurface: "#1d1611",
  },
  friendly: {
    background: "#10211d",
    surface: "#f2efe8",
    accent: "#4fb488",
    textPrimary: "#fff8ef",
    textOnSurface: "#1d1611",
  },
  b_grade_fun: {
    background: "#120f12",
    surface: "#fff5ea",
    accent: "#e5ff39",
    textPrimary: "#fffdf7",
    textOnSurface: "#1d1611",
  },
} satisfies Record<Style, { background: string; surface: string; accent: string; textPrimary: string; textOnSurface: string }>;

const SCENE_PLAN_FONT_FAMILY = "'Pretendard Variable', 'Inter', sans-serif";

function chooseTemplate(project: ProjectRecord, templateId?: TemplateId | null) {
  const byId = templateId ? templateMap.get(templateId) : undefined;
  if (byId) return byId;
  return TEMPLATES.find((template) => template.supportedPurposes.includes(project.purpose)) ?? TEMPLATES[0];
}

function inferWarnings(fileName: string, size: number): AssetWarningCode[] {
  const warnings: AssetWarningCode[] = [];
  const lower = fileName.toLowerCase();
  if (lower.includes("dark")) warnings.push("LOW_BRIGHTNESS");
  if (lower.includes("blur")) warnings.push("POSSIBLE_BLUR");
  if (size < 9000) warnings.push("LOW_RESOLUTION");
  return warnings;
}

function clip(text: string, max: number) {
  return text.length <= max ? text : `${text.slice(0, max - 1)}…`;
}

function buildCopyBundle(project: ProjectRecord, templateId: TemplateId, quickOptions: QuickOptions, changeSet: RegenerateChangeSet) {
  const style: Style = changeSet.styleOverride ?? project.style;
  const region = project.regionName;
  const shorterCopy = Boolean(quickOptions.shorterCopy ?? changeSet.shorterCopy);
  const highlightPrice = Boolean(quickOptions.highlightPrice ?? changeSet.highlightPrice);
  const emphasizeRegion = Boolean(quickOptions.emphasizeRegion ?? changeSet.emphasizeRegion);
  const regionText = emphasizeRegion ? `${region}에서` : `${region} 기준으로`;
  const hookTextByPurpose: Record<ProjectRecord["purpose"], string> = {
    new_menu: `${regionText} 먼저 만나는 새 메뉴`,
    promotion: `${regionText} 오늘만 놓치기 아쉬운 혜택`,
    review: `${regionText} 다시 찾게 되는 한마디`,
    location_push: `${regionText} 가볍게 들르기 좋은 곳`,
  };

  const captions = [
    clip(`${region} ${project.businessType === "cafe" ? "카페" : "음식점"} ${shorterCopy ? "짧게" : "또렷하게"} 정리했습니다`, 80),
    clip(
      highlightPrice
        ? `${region}에서 가격이 먼저 보이도록 구성했습니다`
        : `${project.purpose === "promotion" ? "행사" : "신메뉴"} 포인트를 짧게 담았습니다`,
      80,
    ),
    clip(
      style === "b_grade_fun"
        ? `${region}에서 오늘 바로 웃기게 눈에 띄는 광고`
        : `${region} 기준으로 보기 쉬운 숏폼 구성`,
      80,
    ),
  ];

  const hashtags = [
    `#${region.replace(/\s+/g, "")}`,
    project.businessType === "cafe" ? "#카페추천" : "#음식점추천",
    project.purpose === "promotion" ? "#오늘만할인" : "#신메뉴",
    style === "b_grade_fun" ? "#웃긴광고" : "#광고콘텐츠",
  ];

  const hookBase = hookTextByPurpose[project.purpose];
  const hookText = clip(shorterCopy ? hookBase : `${hookBase} 흐름을 한 번에 보여드립니다`, 34);
  const productText =
    templateId === "T04"
      ? "사람들이 먼저 기억하는 대표 메뉴"
      : templateId === "T02"
        ? "가격과 혜택이 잘 보이는 구성"
        : "오늘의 대표 메뉴와 분위기";
  const differenceText = highlightPrice
    ? "가격 메리트가 한눈에 보입니다"
    : project.purpose === "location_push"
      ? "동네에서 바로 찾기 쉬운 포인트"
      : "짧게 봐도 느낌이 전해집니다";
  const ctaText = style === "b_grade_fun" ? "지금 바로 들러보세요" : "오늘 바로 방문해 보세요";
  const reviewQuote = `“${region}에서 다시 찾게 되는 한마디”`;
  const urgencyText = project.purpose === "promotion" ? "오늘 지나면 아쉬운 타이밍" : differenceText;
  const visitReasonText = project.purpose === "location_push" ? differenceText : "짧게 봐도 위치와 이유가 보입니다";

  return {
    hookText,
    productText,
    differenceText,
    ctaText,
    captions,
    hashtags,
    sceneText: {
      hook: hookText,
      product_name: productText,
      difference: differenceText,
      benefit: differenceText,
      urgency: urgencyText,
      cta: ctaText,
      region_hook: hookText,
      visit_reason: visitReasonText,
      review_quote: reviewQuote,
    },
    subText: {
      hook: captions[0],
      product_name: captions[1],
      difference: captions[2],
      benefit: captions[1],
      urgency: captions[2],
      cta: captions[0],
      region_hook: captions[0],
      visit_reason: captions[1],
      review_quote: captions[2],
    },
  };
}

function buildActiveCopyPolicy(project: ProjectRecord, templateId: TemplateId, quickOptions: QuickOptions, changeSet: RegenerateChangeSet) {
  const copyRule = findCopyRule(templateId, project.purpose);
  const forbiddenDetailLocationSurfaces = copyRule?.locationPolicy?.forbiddenDetailLocationSurfaces ?? [];
  const detailLocationPresent = Boolean(project.detailLocation?.trim());
  const emphasizeRegionRequested = Boolean(quickOptions.emphasizeRegion ?? changeSet.emphasizeRegion);

  return {
    detailLocationPolicyId: copyRule?.locationPolicy?.policyId ?? null,
    forbiddenDetailLocationSurfaces,
    guardActive: Boolean(detailLocationPresent && forbiddenDetailLocationSurfaces.length > 0),
    emphasizeRegionRequested,
    detailLocationPresent,
  };
}

function buildCopyDeck(project: ProjectRecord, templateId: TemplateId, quickOptions: QuickOptions, changeSet: RegenerateChangeSet) {
  const copy = buildCopyBundle(project, templateId, quickOptions, changeSet);
  const templateDef = slotLayerMapManifest.templates.find((item) => item.templateId === templateId);
  if (!templateDef) {
    return null;
  }

  return {
    templateId,
    hook: {
      primaryLine: copy.hookText,
      supportLine: templateDef.slotGroups.hook.recommendedSupportField ? copy.captions[0] ?? null : null,
    },
    body: {
      blocks: (templateDef.slotGroups.body.bodyBlocks ?? []).map((block) => ({
        blockId: block.blockId,
        textRole: block.textRole,
        uiLabel: block.uiLabel,
        primaryLine: copy.sceneText[block.textRole as keyof typeof copy.sceneText] ?? "",
        supportLine: copy.subText[block.textRole as keyof typeof copy.subText] ?? null,
      })),
    },
    cta: {
      primaryLine: copy.ctaText,
      supportLine: null,
    },
  };
}

function buildSceneLayerSummary(templateId: TemplateId) {
  const templateDef = slotLayerMapManifest.templates.find((item) => item.templateId === templateId);
  if (!templateDef) {
    return null;
  }

  const textRoleMap = slotLayerMapManifest.textRoleToLayer;
  const items = [
    ...templateDef.slotGroups.hook.sceneIds.map((sceneId) => {
      const textRole = templateDef.slotGroups.hook.textRoles[0] ?? "hook";
      return {
        sceneId,
        slotGroup: "hook" as const,
        textRole,
        uiLabel: textRoleMap[textRole as keyof typeof textRoleMap]?.uiLabel ?? "후킹 문장",
      };
    }),
    ...templateDef.slotGroups.body.sceneIds.map((sceneId, index) => {
      const block = templateDef.slotGroups.body.bodyBlocks?.[index];
      const textRole = block?.textRole ?? templateDef.slotGroups.body.textRoles[index] ?? "body";
      return {
        sceneId,
        slotGroup: "body" as const,
        textRole,
        uiLabel: block?.uiLabel ?? textRoleMap[textRole as keyof typeof textRoleMap]?.uiLabel ?? "본문",
      };
    }),
    ...templateDef.slotGroups.cta.sceneIds.map((sceneId) => {
      const textRole = templateDef.slotGroups.cta.textRoles[0] ?? "cta";
      return {
        sceneId,
        slotGroup: "cta" as const,
        textRole,
        uiLabel: textRoleMap[textRole as keyof typeof textRoleMap]?.uiLabel ?? "행동 유도",
      };
    }),
  ];

  return {
    templateId,
    items,
  };
}

function badgeTextForScene(purpose: ProjectRecord["purpose"], sceneRole: string, slot: string) {
  if (sceneRole === "closing") {
    return "CTA";
  }
  if (purpose === "promotion" && sceneRole === "opening") {
    return "TODAY DEAL";
  }
  if (purpose === "review") {
    return "REAL REVIEW";
  }
  return slot.replaceAll("_", " ").toUpperCase();
}

function stampTextForScene(purpose: ProjectRecord["purpose"], sceneRole: string, slot: string) {
  if (sceneRole === "closing") {
    return "POST READY";
  }
  if (purpose === "promotion" && slot === "benefit") {
    return "BENEFIT";
  }
  if (purpose === "promotion" && slot === "period") {
    return "LIMITED";
  }
  if (purpose === "review" && sceneRole === "review") {
    return "REVIEW CUT";
  }
  return slot.replaceAll("_", " ").toUpperCase();
}

function sceneRoleForTemplate(purpose: ProjectRecord["purpose"], textRole: string, slot: string, index: number, lastIndex: number) {
  if (index === lastIndex || textRole === "cta" || slot === "cta") {
    return "closing";
  }
  if (purpose === "review" && (textRole === "review_quote" || textRole === "product_name")) {
    return "review";
  }
  if (index === 0 || textRole === "hook" || textRole === "region_hook") {
    return "opening";
  }
  return "support";
}

function layoutHintForScene(purpose: ProjectRecord["purpose"], sceneRole: string) {
  if (sceneRole === "closing") {
    return "cta_poster";
  }
  if (purpose === "review" || sceneRole === "review") {
    return "review_poster";
  }
  if (sceneRole === "opening") {
    return "offer_poster";
  }
  return "support_panel";
}

function kickerTextForScene(
  templateTitle: string,
  purpose: ProjectRecord["purpose"],
  slot: string,
  secondaryText: string,
  sceneRole: string,
) {
  if (sceneRole === "closing") {
    return "확인 후 바로 게시로 이어지는 마지막 장면";
  }
  if (purpose === "promotion" && slot === "benefit") {
    return "혜택과 기간감이 먼저 읽히는 프로모션 구성";
  }
  if (purpose === "review") {
    return "리뷰형 장면은 다시 찾는 이유를 먼저 남깁니다";
  }
  if (secondaryText) {
    return secondaryText;
  }
  return `${templateTitle} 장면`;
}

function fallbackSceneAssetPath(project: ProjectRecord) {
  return project.businessType === "restaurant" ? "/api/sample-assets/katsu" : "/api/sample-assets/beer";
}

function resolveSceneAssetPath(projectId: string, asset?: AssetRecord) {
  if (!asset) {
    return null;
  }
  return `/api/projects/${projectId}/assets/${asset.assetId}/preview`;
}

function buildProjectScenePlan(project: ProjectRecord, run: GenerationRunRecord): ScenePlanPayload {
  const template = chooseTemplate(project, run.templateId);
  const styleId = run.changeSetSnapshot.styleOverride ?? project.style;
  const stylePreset = stylePresetMap.get(styleId) ?? stylePresetMap.get(project.style) ?? STYLE_PRESETS[0];
  const palette = SCENE_PLAN_PALETTES[styleId];
  const copy = buildCopyBundle(project, template.templateId, run.quickOptionsSnapshot, run.changeSetSnapshot);
  const assets = getStore()
    .projectAssets.get(project.projectId)
    ?.filter((asset) => project.selectedAssetIds.length === 0 || project.selectedAssetIds.includes(asset.assetId)) ?? [];
  const heroAsset = assets[0];
  const detailAssets = assets.length > 0 ? assets : heroAsset ? [heroAsset] : [];
  const lastIndex = template.scenes.length - 1;

  const scenes = template.scenes.map((scene, index) => {
    const detailAsset = detailAssets[index % Math.max(1, detailAssets.length)] ?? heroAsset;
    const preferredAsset = scene.mediaRole === "detail" ? detailAsset : heroAsset;
    const textRole = scene.textRole;
    const sceneRole = sceneRoleForTemplate(project.purpose, textRole, scene.slot, index, lastIndex);

    return {
      sceneId: scene.sceneId,
      slot: scene.slot,
      textRole,
      mediaRole: scene.mediaRole,
      sceneRole,
      durationSec: scene.durationSec,
      asset: {
        storagePath: resolveSceneAssetPath(project.projectId, preferredAsset) ?? fallbackSceneAssetPath(project),
        derivativeType: "vertical",
      },
      copy: {
        primaryText: copy.sceneText[textRole as keyof typeof copy.sceneText] ?? copy.hookText,
        secondaryText: copy.subText[textRole as keyof typeof copy.subText] ?? copy.captions[0],
        headline: copy.sceneText[textRole as keyof typeof copy.sceneText] ?? copy.hookText,
        body: copy.subText[textRole as keyof typeof copy.subText] ?? copy.captions[0],
        kicker: kickerTextForScene(
          template.title,
          project.purpose,
          scene.slot,
          copy.subText[textRole as keyof typeof copy.subText] ?? copy.captions[0],
          sceneRole,
        ),
        cta: copy.ctaText,
        badgeText: badgeTextForScene(project.purpose, sceneRole, scene.slot),
        stampText: stampTextForScene(project.purpose, sceneRole, scene.slot),
      },
      renderHints: {
        layoutHint: layoutHintForScene(project.purpose, sceneRole),
        effects: scene.effects,
        motionPreset: stylePreset.motionPreset,
        captionLength: stylePreset.captionLength,
        safeArea: { top: 96, right: 72, bottom: 112, left: 72 },
        palette,
        typography: {
          headlineSize: styleId === "b_grade_fun" ? 58 : 52,
          bodySize: 22,
          ctaSize: 34,
          fontFamily: SCENE_PLAN_FONT_FAMILY,
        },
      },
    };
  });

  return {
    sceneSpecVersion: "web-demo-v1",
    templateId: template.templateId,
    templateTitle: template.title,
    purpose: project.purpose,
    styleId,
    businessType: project.businessType,
    regionName: project.regionName,
    durationSec: template.durationSec,
    sceneCount: scenes.length,
    scenes,
  };
}

function generateResult(project: ProjectRecord, run: GenerationRunRecord) {
  const template = chooseTemplate(project, run.templateId);
  const copy = buildCopyBundle(project, template.templateId, run.quickOptionsSnapshot, run.changeSetSnapshot);
  const scenePlan = buildProjectScenePlan(project, run);
  const copyPolicy = buildActiveCopyPolicy(project, template.templateId, run.quickOptionsSnapshot, run.changeSetSnapshot);
  const copyDeck = buildCopyDeck(project, template.templateId, run.quickOptionsSnapshot, run.changeSetSnapshot);
  const sceneLayerSummary = buildSceneLayerSummary(template.templateId);
  const changeImpactSummary = buildChangeImpactSummary(run.runType, run.quickOptionsSnapshot, run.changeSetSnapshot);
  const approvedHybridSourceCandidateKey = run.changeSetSnapshot.approvedHybridSourceCandidateKey;
  const usingApprovedHybridSource = Boolean(approvedHybridSourceCandidateKey);
  const promptBaselineSummary = buildPromptBaselineSummary({
    purpose: project.purpose,
    templateId: template.templateId,
    styleId: (run.changeSetSnapshot.styleOverride ?? project.style) as Style,
    quickOptions: {
      highlightPrice: Boolean(run.quickOptionsSnapshot.highlightPrice ?? run.changeSetSnapshot.highlightPrice),
      shorterCopy: Boolean(run.quickOptionsSnapshot.shorterCopy ?? run.changeSetSnapshot.shorterCopy),
      emphasizeRegion: Boolean(run.quickOptionsSnapshot.emphasizeRegion ?? run.changeSetSnapshot.emphasizeRegion),
    },
  });
  const generationRunId = run.id;
  const variantId = randomUUID();
  const videoId = randomUUID();
  const postId = randomUUID();
  const copySetId = randomUUID();
  const result: ProjectResultResponse = {
    projectId: project.projectId,
    generationRunId,
    variantId,
    video: {
      videoId,
      url: `/media/projects/${project.projectId}/runs/${generationRunId}/video.mp4`,
      durationSec: template.durationSec,
      templateId: template.templateId,
    },
    post: {
      postId,
      url: `/media/projects/${project.projectId}/runs/${generationRunId}/post.png`,
    },
    copySet: {
      copySetId,
      hookText: copy.hookText,
      captions: copy.captions,
      hashtags: copy.hashtags,
      ctaText: copy.ctaText,
    },
    scenePlan: {
      url: `/api/projects/${project.projectId}/scene-plan`,
      sceneCount: scenePlan.sceneCount,
      sceneSpecVersion: scenePlan.sceneSpecVersion,
    },
    sceneLayerSummary,
    changeImpactSummary,
    copyPolicy,
    copyDeck,
    promptBaselineSummary,
    rendererSummary: {
      videoSourceMode: usingApprovedHybridSource ? "hybrid_generated_clip" : "scene_image_render",
      motionMode: usingApprovedHybridSource ? "hybrid_overlay_packaging" : "static_concat",
      framingMode: usingApprovedHybridSource ? "hybrid_source_video" : "preprocessed_vertical",
      durationStrategy: usingApprovedHybridSource ? "approved_inventory_reference" : null,
      targetDurationSec: usingApprovedHybridSource ? template.durationSec : null,
      hybridSourceSelectionMode: usingApprovedHybridSource ? "approved_inventory_reference" : null,
      hybridSourceCandidateKey: approvedHybridSourceCandidateKey ?? null,
    },
  };

  run.result = result;
  run.status = "completed";
  run.finishedAt = nowIso();
  run.updatedAt = nowIso();
  project.status = "generated";
  project.latestGenerationRunId = generationRunId;
  project.updatedAt = nowIso();
  return result;
}

function createGenerationRun(
  project: ProjectRecord,
  templateId: TemplateId,
  quickOptions: QuickOptions,
  changeSet: RegenerateChangeSet,
  ageOffsetSeconds = 0,
  runType: GenerationRunRecord["runType"] = Object.keys(changeSet).length > 0 ? "regenerate" : "initial",
): GenerationRunRecord {
  const id = randomUUID();
  const createdAt = ageOffsetSeconds > 0 ? secondsAgo(ageOffsetSeconds) : nowIso();
  return {
    id,
    projectId: project.projectId,
    runType,
    templateId,
    status: "queued" as const,
    errorCode: null,
    startedAt: createdAt,
    finishedAt: null,
    createdAt,
    updatedAt: createdAt,
    quickOptionsSnapshot: quickOptions,
    changeSetSnapshot: changeSet,
    result: null,
    steps: {
      preprocessing: { status: "pending", startedAt: null, finishedAt: null },
      copy_generation: { status: "pending", startedAt: null, finishedAt: null },
      video_rendering: { status: "pending", startedAt: null, finishedAt: null },
      post_rendering: { status: "pending", startedAt: null, finishedAt: null },
      packaging: { status: "pending", startedAt: null, finishedAt: null },
    },
  } satisfies GenerationRunRecord;
}

function buildSteps(elapsedMs: number) {
  const checkpoints = [700, 1500, 2700, 3500, 4200];
  return STEP_NAMES.map((name, index) => {
    const upper = checkpoints[index];
    const lower = index === 0 ? 0 : checkpoints[index - 1];
    const status = elapsedMs >= upper ? "completed" : elapsedMs >= lower ? "processing" : "pending";
    return { name, status } satisfies GenerationStep;
  });
}

function updateRunProgress(store: StoreState, run: GenerationRunRecord) {
  if (run.status === "completed" || run.status === "failed") return run;
  const startedAt = run.startedAt ? new Date(run.startedAt).getTime() : new Date(run.createdAt).getTime();
  const elapsed = Date.now() - startedAt;
  const steps = buildSteps(elapsed);
  const allDone = steps.every((step) => step.status === "completed");
  const anyProcessing = steps.some((step) => step.status === "processing");
  const project = store.projects.get(run.projectId);

  steps.forEach((step) => {
    const record = run.steps[step.name];
    record.status = step.status;
    if (step.status === "processing" && !record.startedAt) record.startedAt = nowIso();
    if (step.status === "completed") {
      record.startedAt = record.startedAt ?? nowIso();
      record.finishedAt = record.finishedAt ?? nowIso();
    }
  });

  if (project) {
    project.latestGenerationRunId = run.id;
    project.status = allDone ? "generated" : anyProcessing ? "generating" : "queued";
    project.updatedAt = nowIso();
  }

  if (allDone) {
    if (!run.result && project) {
      generateResult(project, run);
    } else {
      run.status = "completed";
      run.finishedAt = nowIso();
      run.updatedAt = nowIso();
    }
  } else {
    run.status = anyProcessing ? "processing" : "queued";
    run.updatedAt = nowIso();
  }

  return run;
}

function updateUploadJobProgress(store: StoreState, job: UploadJobRecord) {
  if (job.status === "published" || job.status === "assist_required" || job.status === "assisted_completed" || job.status === "failed") return job;
  const elapsed = Date.now() - new Date(job.createdAt).getTime();
  const project = store.projects.get(job.projectId);
  if (job.requestPayload.publishMode === "auto" && job.channel === "instagram") {
    if (elapsed >= 400 && job.status === "queued") {
      job.status = "publishing";
      job.updatedAt = nowIso();
      if (project) {
        project.status = "publishing";
        project.updatedAt = nowIso();
      }
    }
    if (elapsed >= 1400) {
      job.status = "published";
      job.publishedAt = nowIso();
      job.updatedAt = nowIso();
      if (project) {
        project.status = "published";
        project.updatedAt = nowIso();
      }
    }
  }
  return job;
}

function ensureSeedData(store: StoreState) {
  if (store.projects.size > 0) return;

  const project1: ProjectRecord = {
    projectId: "11111111-1111-4111-8111-111111111111",
    businessType: "cafe",
    regionName: "성수동",
    detailLocation: "서울숲 근처",
    purpose: "new_menu",
    style: "friendly",
    channels: ["instagram"],
    status: "generating",
    assetCount: 2,
    createdAt: minutesAgo(20),
    updatedAt: nowIso(),
    latestGenerationRunId: null,
    selectedTemplateId: "T01",
    selectedAssetIds: [],
    thumbnailText: "신메뉴 출시",
  };

  const project2: ProjectRecord = {
    projectId: "22222222-2222-4222-8222-222222222222",
    businessType: "restaurant",
    regionName: "역삼",
    detailLocation: "테헤란로",
    purpose: "promotion",
    style: "b_grade_fun",
    channels: ["instagram"],
    status: "published",
    assetCount: 3,
    createdAt: minutesAgo(90),
    updatedAt: nowIso(),
    latestGenerationRunId: null,
    selectedTemplateId: "T02",
    selectedAssetIds: [],
    thumbnailText: "오늘만 할인",
  };

  store.projects.set(project1.projectId, project1);
  store.projects.set(project2.projectId, project2);
  store.projectAssets.set(project1.projectId, []);
  store.projectAssets.set(project2.projectId, []);

  const run1 = createGenerationRun(project1, "T01", { emphasizeRegion: true }, { emphasizeRegion: true }, 3);
  const run2 = createGenerationRun(project2, "T02", { highlightPrice: true }, { highlightPrice: true }, 45);
  store.generationRuns.set(run1.id, run1);
  store.generationRuns.set(run2.id, run2);
  updateRunProgress(store, run1);
  updateRunProgress(store, run2);

  const assistJob: UploadJobRecord = {
    id: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
    projectId: project1.projectId,
    variantId: run1.result?.variantId ?? randomUUID(),
    channel: "youtube_shorts",
    socialAccountId: null,
    status: "assist_required",
    errorCode: "PUBLISH_FAILED",
    requestPayload: {
      variantId: run1.result?.variantId ?? randomUUID(),
      channel: "youtube_shorts",
      publishMode: "assist",
      captionOverride: run1.result?.copySet.captions[0] ?? "",
      hashtags: run1.result?.copySet.hashtags ?? [],
    },
    assistPackage: {
      mediaUrl: `/media/projects/${project1.projectId}/runs/${run1.id}/video.mp4`,
      caption: run1.result?.copySet.captions[0] ?? "업로드 보조용 캡션",
      hashtags: run1.result?.copySet.hashtags ?? ["#성수동", "#카페추천"],
      thumbnailText: "신메뉴 출시",
    },
    retryCount: 0,
    publishedAt: null,
    createdAt: minutesAgo(12),
    updatedAt: nowIso(),
  };
  store.uploadJobs.set(assistJob.id, assistJob);

  store.socialAccounts.set("instagram", {
    id: "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
    channel: "instagram",
    status: "connected",
    accountName: "my_store_official",
    lastSyncedAt: minutesAgo(8),
    pendingState: null,
  });
  store.socialAccounts.set("youtube_shorts", {
    id: "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee",
    channel: "youtube_shorts",
    status: "not_connected",
    accountName: null,
    lastSyncedAt: null,
    pendingState: null,
  });
  store.socialAccounts.set("tiktok", {
    id: "ffffffff-ffff-4fff-8fff-ffffffffffff",
    channel: "tiktok",
    status: "expired",
    accountName: "tiktok_demo_store",
    lastSyncedAt: minutesAgo(320),
    pendingState: null,
  });
}

function getStore(): StoreState {
  if (!globalThis.__snsDemoWebStore) {
    globalThis.__snsDemoWebStore = {
      storeProfile: {
        storeProfileId: "99999999-9999-4999-8999-999999999999",
        businessType: "cafe",
        regionName: "성수동",
        detailLocation: "서울숲 근처",
        defaultStyle: "friendly",
      },
      projects: new Map(),
      projectAssets: new Map(),
      generationRuns: new Map(),
      uploadJobs: new Map(),
      socialAccounts: new Map(),
    };
    ensureSeedData(globalThis.__snsDemoWebStore);
  } else {
    ensureSeedData(globalThis.__snsDemoWebStore);
  }
  return globalThis.__snsDemoWebStore;
}

export function listProjects(status?: ProjectStatus): ProjectSummary[] {
  const store = getStore();
  return [...store.projects.values()]
    .map((project) => {
      const run = project.latestGenerationRunId ? store.generationRuns.get(project.latestGenerationRunId) : null;
      if (run) updateRunProgress(store, run);
      return project;
    })
    .filter((project) => !status || project.status === status)
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    .map((project) => ({
      projectId: project.projectId,
      businessType: project.businessType,
      purpose: project.purpose,
      style: project.style,
      status: project.status,
      createdAt: project.createdAt,
    }));
}

export function createProject(input: CreateProjectRequest): CreateProjectResponse {
  const store = getStore();
  const projectId = randomUUID();
  const now = nowIso();
  store.projects.set(projectId, {
    projectId,
    businessType: input.businessType,
    regionName: input.regionName,
    detailLocation: input.detailLocation ?? null,
    purpose: input.purpose,
    style: input.style,
    channels: input.channels,
    status: "draft",
    assetCount: 0,
    createdAt: now,
    updatedAt: now,
    latestGenerationRunId: null,
    selectedTemplateId: null,
    selectedAssetIds: [],
    thumbnailText: null,
  });
  store.projectAssets.set(projectId, []);
  return { projectId, status: "draft", createdAt: now };
}

export function getProject(projectId: string) {
  const store = getStore();
  const project = store.projects.get(projectId);
  if (!project) throw new Error("PROJECT_NOT_FOUND");
  const run = project.latestGenerationRunId ? store.generationRuns.get(project.latestGenerationRunId) : null;
  if (run) updateRunProgress(store, run);
  return clone(project);
}

export function getProjectAssets(projectId: string) {
  const store = getStore();
  if (!store.projects.has(projectId)) throw new Error("PROJECT_NOT_FOUND");
  return (store.projectAssets.get(projectId) ?? []).map(
    ({ mimeType: _mimeType, fileSizeBytes: _fileSizeBytes, storagePath: _storagePath, createdAt: _createdAt, contentBase64: _contentBase64, ...asset }) => asset,
  );
}

export async function addProjectAssets(projectId: string, files: File[]) {
  const store = getStore();
  const project = store.projects.get(projectId);
  if (!project) throw new Error("PROJECT_NOT_FOUND");

  const assets = await Promise.all(
    files.map(async (file) => {
      const buffer = Buffer.from(await file.arrayBuffer());
      const assetId = randomUUID();
      const fileName = file.name || `asset-${assetId}.png`;
      return {
        assetId,
        fileName,
        width: 1080,
        height: 1440,
        warnings: inferWarnings(fileName, file.size),
        mimeType: file.type || "image/png",
        fileSizeBytes: file.size,
        storagePath: `/projects/${projectId}/raw/${assetId}.${fileName.split(".").pop() ?? "png"}`,
        createdAt: nowIso(),
        contentBase64: buffer.toString("base64"),
      } satisfies AssetRecord;
    }),
  );

  const current = store.projectAssets.get(projectId) ?? [];
  current.push(...assets);
  store.projectAssets.set(projectId, current);
  project.assetCount = current.length;
  project.selectedAssetIds = current.map((asset) => asset.assetId);
  project.updatedAt = nowIso();

  return {
    projectId,
    assets: assets.map(
      ({ mimeType: _mimeType, fileSizeBytes: _fileSizeBytes, storagePath: _storagePath, createdAt: _createdAt, contentBase64: _contentBase64, ...asset }) => asset,
    ),
  };
}

export function startGeneration(projectId: string, input: GenerateProjectInput) {
  const store = getStore();
  const project = store.projects.get(projectId);
  if (!project) throw new Error("PROJECT_NOT_FOUND");
  if (!input.assetIds.length) throw new Error("INVALID_INPUT");
  const run = createGenerationRun(
    project,
    input.templateId,
    input.quickOptions ?? {},
    input.approvedHybridSourceCandidateKey ? { approvedHybridSourceCandidateKey: input.approvedHybridSourceCandidateKey } : {},
    0,
    "initial",
  );
  store.generationRuns.set(run.id, run);
  project.latestGenerationRunId = run.id;
  project.selectedTemplateId = input.templateId;
  project.selectedAssetIds = input.assetIds;
  project.status = "queued";
  project.updatedAt = nowIso();
  return { generationRunId: run.id, projectId, status: "queued" as const };
}

export function regenerateProject(projectId: string, changeSet: RegenerateChangeSet) {
  const store = getStore();
  const project = store.projects.get(projectId);
  if (!project) throw new Error("PROJECT_NOT_FOUND");
  const template = chooseTemplate(project, changeSet.templateId ?? project.selectedTemplateId);
  const run = createGenerationRun(project, template.templateId, {}, changeSet, 0);
  store.generationRuns.set(run.id, run);
  project.latestGenerationRunId = run.id;
  project.selectedTemplateId = template.templateId;
  project.status = "queued";
  project.updatedAt = nowIso();
  return { generationRunId: run.id, projectId, status: "queued" as const };
}

export function getGenerationStatus(projectId: string): GenerationStatusResponse {
  const store = getStore();
  const project = store.projects.get(projectId);
  if (!project) throw new Error("PROJECT_NOT_FOUND");
  const run = project.latestGenerationRunId ? store.generationRuns.get(project.latestGenerationRunId) : null;
  if (!run) {
    return { projectId, projectStatus: project.status, steps: [], error: null, result: null };
  }
  updateRunProgress(store, run);
  const steps = STEP_NAMES.map((name) => ({ name, status: run.steps[name].status }));
  return {
    projectId,
    projectStatus: project.status,
    steps,
    result: run.result
      ? {
          videoId: run.result.video.videoId,
          postId: run.result.post.postId,
          copySetId: run.result.copySet.copySetId,
          previewVideoUrl: run.result.video.url,
          previewImageUrl: run.result.post.url,
          ctaText: run.result.copySet.ctaText,
        }
      : null,
    error: run.status === "failed" ? { code: "RENDER_FAILED", message: "생성에 실패했습니다." } : null,
  };
}

export function getProjectResult(projectId: string) {
  const store = getStore();
  const project = store.projects.get(projectId);
  if (!project) throw new Error("PROJECT_NOT_FOUND");
  const run = project.latestGenerationRunId ? store.generationRuns.get(project.latestGenerationRunId) : null;
  if (!run) throw new Error("INVALID_STATE_TRANSITION");
  updateRunProgress(store, run);
  if (!run.result) throw new Error("INVALID_STATE_TRANSITION");
  return clone(run.result);
}

export function getProjectScenePlan(projectId: string): ScenePlanPayload {
  const store = getStore();
  const project = store.projects.get(projectId);
  if (!project) throw new Error("PROJECT_NOT_FOUND");
  const run = project.latestGenerationRunId ? store.generationRuns.get(project.latestGenerationRunId) : null;
  if (!run) throw new Error("INVALID_STATE_TRANSITION");
  updateRunProgress(store, run);
  if (!run.result) throw new Error("INVALID_STATE_TRANSITION");
  return buildProjectScenePlan(project, run);
}

export function getProjectAssetPreview(projectId: string, assetId: string) {
  const store = getStore();
  const assets = store.projectAssets.get(projectId) ?? [];
  const asset = assets.find((item) => item.assetId === assetId);
  if (!asset) {
    throw new Error("PROJECT_NOT_FOUND");
  }
  if (asset.contentBase64) {
    return {
      contentType: asset.mimeType,
      body: Buffer.from(asset.contentBase64, "base64"),
    };
  }

  const placeholderSvg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1440">
      <rect width="1080" height="1440" fill="#f5ede3" />
      <rect x="96" y="96" width="888" height="1248" rx="56" fill="#fffdf8" stroke="#231a13" stroke-opacity="0.08" />
      <circle cx="280" cy="360" r="180" fill="#e5ff39" fill-opacity="0.34" />
      <circle cx="780" cy="980" r="210" fill="#ff7b3b" fill-opacity="0.22" />
      <text x="540" y="690" text-anchor="middle" fill="#231a13" font-size="84" font-weight="800" font-family="sans-serif">${asset.fileName}</text>
      <text x="540" y="792" text-anchor="middle" fill="#6a5a4d" font-size="42" font-weight="600" font-family="sans-serif">demo asset preview</text>
    </svg>
  `.trim();
  return {
    contentType: "image/svg+xml",
    body: Buffer.from(placeholderSvg, "utf8"),
  };
}

export function publishProject(projectId: string, request: PublishProjectRequest): PublishProjectResponse {
  const store = getStore();
  const project = store.projects.get(projectId);
  if (!project) throw new Error("PROJECT_NOT_FOUND");
  const run = project.latestGenerationRunId ? store.generationRuns.get(project.latestGenerationRunId) : null;
  if (!run || !run.result) throw new Error("INVALID_STATE_TRANSITION");
  updateRunProgress(store, run);
  if (!run.result || request.variantId !== run.result.variantId) throw new Error("INVALID_STATE_TRANSITION");
  const account = store.socialAccounts.get(request.channel);
  const assistPackage: PublishAssistPackage = {
    mediaUrl: run.result.video.url,
    caption: request.captionOverride ?? run.result.copySet.captions[0],
    hashtags: request.hashtags?.length ? request.hashtags : run.result.copySet.hashtags,
    thumbnailText: request.thumbnailText ?? project.thumbnailText ?? "콘텐츠 미리보기",
  };

  const shouldAssist = request.publishMode === "assist" || request.channel !== "instagram" || !account || account.status !== "connected";
  let errorCode: UploadJobRecord["errorCode"] = null;
  if (shouldAssist) {
    if (request.publishMode === "assist") {
      errorCode = null;
    } else if (!account || account.status === "not_connected" || account.status === "connecting") {
      errorCode = "AUTH_REQUIRED";
    } else if (account.status === "expired") {
      errorCode = "SOCIAL_TOKEN_EXPIRED";
    } else if (account.status === "permission_error") {
      errorCode = "PUBLISH_FAILED";
    } else if (request.channel !== "instagram") {
      errorCode = "PUBLISH_FAILED";
    }
  }
  const job: UploadJobRecord = {
    id: randomUUID(),
    projectId,
    variantId: request.variantId,
    channel: request.channel,
    socialAccountId: account?.id ?? null,
    status: shouldAssist ? "assist_required" : "queued",
    errorCode,
    requestPayload: request,
    assistPackage: shouldAssist ? assistPackage : null,
    retryCount: 0,
    publishedAt: null,
    createdAt: nowIso(),
    updatedAt: nowIso(),
  };

  store.uploadJobs.set(job.id, job);
  project.status = shouldAssist ? "upload_assist" : "publishing";
  project.updatedAt = nowIso();

  return {
    uploadJobId: job.id,
    projectId,
    status: shouldAssist ? "assist_required" : "queued",
    assistPackage: shouldAssist ? assistPackage : undefined,
  };
}

export function getUploadJob(jobId: string): UploadJobResponse {
  const store = getStore();
  const job = store.uploadJobs.get(jobId);
  if (!job) throw new Error("PROJECT_NOT_FOUND");
  updateUploadJobProgress(store, job);
  return {
    uploadJobId: job.id,
    projectId: job.projectId,
    channel: job.channel,
    status: job.status,
    error: job.errorCode
      ? {
          code: job.errorCode as any,
          message:
            job.errorCode === "AUTH_REQUIRED"
              ? "계정 연동이 필요합니다."
              : job.errorCode === "SOCIAL_TOKEN_EXPIRED"
                ? "토큰이 만료되어 재연동이 필요합니다."
              : "업로드 보조 모드로 전환되었습니다.",
        }
      : null,
    createdAt: job.createdAt,
    updatedAt: job.updatedAt,
    publishedAt: job.publishedAt,
    assistPackage: job.status === "assist_required" || job.status === "assisted_completed" ? job.assistPackage : null,
  };
}

export function getLatestUploadJobForProject(projectId: string): UploadJobResponse | null {
  const store = getStore();
  const latestJob = Array.from(store.uploadJobs.values())
    .filter((job) => job.projectId === projectId)
    .sort((left, right) => new Date(right.updatedAt).getTime() - new Date(left.updatedAt).getTime())[0];
  return latestJob ? getUploadJob(latestJob.id) : null;
}

export function listUploadJobsForProject(projectId: string): UploadJobResponse[] {
  const store = getStore();
  return Array.from(store.uploadJobs.values())
    .filter((job) => job.projectId === projectId)
    .sort((left, right) => new Date(right.updatedAt).getTime() - new Date(left.updatedAt).getTime())
    .map((job) => getUploadJob(job.id));
}

export function completeAssist(jobId: string) {
  const store = getStore();
  const job = store.uploadJobs.get(jobId);
  if (!job) throw new Error("PROJECT_NOT_FOUND");
  job.status = "assisted_completed";
  job.errorCode = null;
  job.publishedAt = nowIso();
  job.updatedAt = nowIso();
  const project = store.projects.get(job.projectId);
  if (project) {
    project.status = "published";
    project.updatedAt = nowIso();
  }
  return getUploadJob(jobId);
}

export function listSocialAccounts(): SocialAccountsResponse {
  const store = getStore();
  return {
    items: CHANNELS.map((channel) => {
      const account = store.socialAccounts.get(channel);
      return account
        ? { channel, status: account.status, accountName: account.accountName, lastSyncedAt: account.lastSyncedAt }
        : { channel, status: "not_connected", accountName: null, lastSyncedAt: null };
    }),
  };
}

export function connectSocialAccount(channel: Channel): ConnectSocialAccountResponse {
  const store = getStore();
  const pendingState = randomUUID();
  const account = store.socialAccounts.get(channel) ?? {
    id: randomUUID(),
    channel,
    status: "connecting" as const,
    accountName: null,
    lastSyncedAt: null,
    pendingState,
  };
  account.status = "connecting";
  account.lastSyncedAt = nowIso();
  account.pendingState = pendingState;
  store.socialAccounts.set(channel, account);
  return {
    channel,
    status: "connecting",
    redirectUrl: `/api/social-accounts/${channel}/callback?code=demo-code&state=${pendingState}`,
  };
}

export function callbackSocialAccount(channel: Channel, params?: { code?: string; state?: string }): CallbackSocialAccountResponse {
  const store = getStore();
  const account = store.socialAccounts.get(channel) ?? {
    id: randomUUID(),
    channel,
    status: "connected" as const,
    accountName: channel === "instagram" ? "my_store_official" : `${channel}_demo`,
    lastSyncedAt: nowIso(),
    pendingState: null,
  };
  if (!params?.code || !params.state || !account.pendingState || account.pendingState !== params.state) {
    throw new Error("OAUTH_CALLBACK_INVALID");
  }
  if (params.code === "permission-error") {
    account.status = "permission_error";
    account.lastSyncedAt = nowIso();
    account.pendingState = null;
    store.socialAccounts.set(channel, account);
    throw new Error("OAUTH_CALLBACK_INVALID");
  }
  account.status = "connected";
  account.accountName = account.accountName ?? (channel === "instagram" ? "my_store_official" : `${channel}_demo`);
  account.lastSyncedAt = nowIso();
  account.pendingState = null;
  store.socialAccounts.set(channel, account);
  return {
    channel,
    status: "connected",
    socialAccountId: account.id,
  };
}

export function getStoreProfile(): StoreProfileResponse {
  const store = getStore();
  return clone(store.storeProfile);
}

export function updateStoreProfile(input: UpdateStoreProfileRequest): StoreProfileResponse {
  const store = getStore();
  store.storeProfile = {
    storeProfileId: store.storeProfile.storeProfileId,
    businessType: input.businessType,
    regionName: input.regionName,
    detailLocation: input.detailLocation ?? null,
    defaultStyle: input.defaultStyle ?? null,
  };
  return clone(store.storeProfile);
}

export function getProjectHistory() {
  return listProjects();
}
