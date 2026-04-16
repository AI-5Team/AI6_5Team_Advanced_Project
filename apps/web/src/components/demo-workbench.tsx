"use client";

import { useEffect, useRef, useState, useTransition } from "react";
import { useSearchParams } from "next/navigation";
import {
  completeAssist,
  createProject,
  getGenerationStatus,
  getProjectDetail,
  getProjectAssets,
  getProjectResult,
  getUploadJob,
  listApprovedHybridCandidates,
  listProjects,
  publishProject,
  regenerateProject,
  startGeneration,
  uploadAssets,
} from "@/lib/api";
import {
  BUSINESS_TYPES,
  CHANNELS,
  CHANNEL_TIERS,
  QUICK_ACTIONS,
  STYLES,
  TEMPLATES,
  type AssetWarningCode,
  type BusinessType,
  type Channel,
  type ApprovedHybridCandidateItem,
  type ApprovedHybridInventoryResponse,
  type GenerationStep,
  type GenerationStatusResponse,
  type GetProjectResponse,
  type ProjectResultResponse,
  type ProjectSummary,
  type Purpose,
  type PublishAssistPackage,
  type Style,
  type TemplateId,
  type UploadedAssetItem,
} from "@/lib/contracts";
import { resolveMediaUrl } from "@/lib/media-url";
import { describeQuickActionPreview } from "@/lib/change-impact";
import { recommendQuickActions } from "@/lib/quick-action-recommendation";
import { inferHybridLaneHint } from "@/lib/hybrid-lane-hint";
import { ResultMediaPreview } from "@/components/result-media-preview";
import { ScenePlanPreviewLinks } from "@/components/scene-plan-preview-links";
import { UploadAssistPanel } from "@/components/upload-assist-panel";
import { CopyPolicySummary } from "@/components/copy-policy-summary";
import { PromptBaselineSummary } from "@/components/prompt-baseline-summary";
import { CopyDeckSummary } from "@/components/copy-deck-summary";
import { ChangeImpactSummary } from "@/components/change-impact-summary";

const PURPOSE_LABELS: Record<Purpose, { title: string; hint: string }> = {
  new_menu: { title: "신메뉴", hint: "새 메뉴를 바로 보여줍니다." },
  promotion: { title: "할인/행사", hint: "오늘만 혜택을 강조합니다." },
  review: { title: "후기", hint: "짧은 반응을 전면에 둡니다." },
  location_push: { title: "방문 유도", hint: "동네와 위치를 함께 보여줍니다." },
};

const BUSINESS_LABELS: Record<BusinessType, string> = {
  cafe: "카페",
  restaurant: "음식점",
};

const STYLE_LABELS: Record<Style, { title: string; hint: string }> = {
  default: { title: "기본", hint: "짧고 또렷하게 정리합니다." },
  friendly: { title: "친근함", hint: "부드럽고 권유하는 톤입니다." },
  b_grade_fun: { title: "하찮고 웃김", hint: "짧고 과장된 한마디가 강합니다." },
};

const CHANNEL_LABELS: Record<Channel, { title: string; tier: string }> = {
  instagram: { title: "instagram", tier: CHANNEL_TIERS.instagram },
  youtube_shorts: { title: "youtube_shorts", tier: CHANNEL_TIERS.youtube_shorts },
  tiktok: { title: "tiktok", tier: CHANNEL_TIERS.tiktok },
};

const HYBRID_LANE_LABELS: Record<string, string> = {
  drink_glass_lane: "drink lane",
  tray_full_plate_lane: "tray/full-plate lane",
};

const HYBRID_APPROVAL_SOURCE_LABELS: Record<string, string> = {
  benchmark_accept: "gate accept",
  manual_review_promote: "manual review promote",
};

const DEFAULT_TEMPLATE_ID = (TEMPLATES[0]?.templateId ?? "T01") as TemplateId;
const TEMPLATE_SEQUENCE = TEMPLATES.map((template) => template.templateId) as TemplateId[];

type MobileWorkspaceSection = "recent" | "wizard" | "result";

function defaultWizard() {
  return {
    businessType: "cafe" as BusinessType,
    regionName: "성수동",
    detailLocation: "서울숲 근처",
    purpose: "new_menu" as Purpose,
    style: "friendly" as Style,
    channels: ["instagram"] as Channel[],
    templateId: DEFAULT_TEMPLATE_ID,
    thumbnailText: "신메뉴 출시",
  };
}

type WizardState = ReturnType<typeof defaultWizard>;

function templateForPurpose(purpose: Purpose) {
  return (TEMPLATES.find((template) => template.supportedPurposes.includes(purpose))?.templateId ?? DEFAULT_TEMPLATE_ID) as TemplateId;
}

function statusTone(status?: string | null) {
  if (!status) return "neutral";
  if (status === "published" || status === "connected" || status === "completed" || status === "assisted_completed") return "good";
  if (status === "failed" || status === "assist_required") return "danger";
  if (status === "queued" || status === "processing" || status === "publishing" || status === "generating") return "warning";
  return "neutral";
}

function statusLabel(status?: string | null) {
  switch (status) {
    case "pending":
      return "대기";
    case "processing":
      return "진행 중";
    case "completed":
      return "완료";
    case "draft":
      return "초안";
    case "queued":
      return "대기";
    case "preprocessing":
      return "전처리";
    case "generating":
      return "생성 중";
    case "generated":
      return "완료";
    case "upload_assist":
      return "보조 필요";
    case "publishing":
      return "게시 중";
    case "published":
      return "게시 완료";
    case "failed":
      return "실패";
    case "assist_required":
      return "보조 필요";
    case "assisted_completed":
      return "수동 완료";
    default:
      return status ?? "대기";
  }
}

function stepTitle(stepName: GenerationStep["name"]) {
  switch (stepName) {
    case "preprocessing":
      return "사진 정리";
    case "copy_generation":
      return "문구 만들기";
    case "video_rendering":
      return "영상 조합";
    case "post_rendering":
      return "게시글 만들기";
    case "packaging":
      return "업로드 준비";
  }
}

function stepMessage(stepName: GenerationStep["name"]) {
  switch (stepName) {
    case "preprocessing":
      return "사진을 더 보기 좋게 다듬는 중입니다.";
    case "copy_generation":
      return "가게에 맞는 문구를 작성하는 중입니다.";
    case "video_rendering":
      return "숏폼 영상을 조합하는 중입니다.";
    case "post_rendering":
      return "게시글 이미지를 정리하는 중입니다.";
    case "packaging":
      return "업로드용 결과를 묶는 중입니다.";
  }
}

function normalizeHashtagDraft(text: string) {
  const normalized = text
    .split(/[\s,\n]+/)
    .map((item) => item.trim())
    .filter(Boolean)
    .map((item) => (item.startsWith("#") ? item : `#${item.replace(/^#+/, "")}`));
  return Array.from(new Set(normalized)).slice(0, 30);
}

function assetWarningText(code: AssetWarningCode) {
  switch (code) {
    case "LOW_BRIGHTNESS":
      return "너무 어두움";
    case "LOW_RESOLUTION":
      return "해상도 낮음";
    case "POSSIBLE_BLUR":
      return "흔들림 가능성";
    case "OFF_CENTER_SUBJECT":
      return "피사체 중심 불명확";
  }
}

function templateLabel(templateId: TemplateId) {
  const template = TEMPLATES.find((item) => item.templateId === templateId);
  return `${templateId} · ${template?.title ?? templateId}`;
}

function nextTemplateId(currentTemplateId: TemplateId) {
  const currentIndex = TEMPLATE_SEQUENCE.indexOf(currentTemplateId);
  if (currentIndex === -1) {
    return DEFAULT_TEMPLATE_ID;
  }
  return TEMPLATE_SEQUENCE[(currentIndex + 1) % TEMPLATE_SEQUENCE.length] ?? DEFAULT_TEMPLATE_ID;
}

function makeSvgFile(title: string, accent: string, bg: string) {
  const svg = `
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1440">
    <defs>
      <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
        <stop offset="0%" stop-color="${bg}" />
        <stop offset="100%" stop-color="#fffaf4" />
      </linearGradient>
    </defs>
    <rect width="1080" height="1440" fill="url(#bg)" />
    <circle cx="238" cy="330" r="178" fill="${accent}" opacity="0.18" />
    <circle cx="792" cy="1040" r="212" fill="${accent}" opacity="0.12" />
    <rect x="118" y="175" width="844" height="1090" rx="56" fill="white" opacity="0.78" />
    <rect x="210" y="325" width="660" height="430" rx="36" fill="${accent}" opacity="0.14" />
    <path d="M420 862c0 48 40 88 90 88s90-40 90-88" fill="none" stroke="${accent}" stroke-width="16" stroke-linecap="round" />
    <circle cx="540" cy="578" r="108" fill="${accent}" opacity="0.28" />
    <rect x="440" y="476" width="200" height="72" rx="36" fill="white" opacity="0.78" />
    <text x="540" y="150" text-anchor="middle" fill="#1d1611" font-size="54" font-weight="800" font-family="sans-serif">${title}</text>
    <text x="540" y="1235" text-anchor="middle" fill="#226b5f" font-size="34" font-weight="700" font-family="sans-serif">SNS 콘텐츠 생성 데모</text>
  </svg>`;

  return new File([svg], `${title}.svg`, { type: "image/svg+xml" });
}

function demoFiles() {
  return [makeSvgFile("아메리카노", "#e56a4c", "#fde7d8"), makeSvgFile("샌드위치", "#226b5f", "#e6f1ec")];
}

export function DemoWorkbench() {
  const searchParams = useSearchParams();
  const requestedProjectId = searchParams.get("projectId");
  const requestedUploadJobId = searchParams.get("uploadJobId");
  const [isPending, startTransition] = useTransition();
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [selectedProject, setSelectedProject] = useState<ProjectEditorState | null>(null);
  const [generationStatus, setGenerationStatus] = useState<GenerationStatusResponse | null>(null);
  const [activeResult, setActiveResult] = useState<ProjectResultResponse | null>(null);
  const [activeUploadJobId, setActiveUploadJobId] = useState<string | null>(null);
  const [uploadJob, setUploadJob] = useState<{
    uploadJobId: string;
    projectId: string;
    channel: Channel;
    status: string;
    assistPackage?: PublishAssistPackage | null;
    error?: { code: string; message: string } | null;
  } | null>(null);
  const [feedback, setFeedback] = useState("대기 중입니다.");
  const [wizard, setWizard] = useState(defaultWizard());
  const [draftFiles, setDraftFiles] = useState<File[]>([]);
  const [approvedHybridInventory, setApprovedHybridInventory] = useState<ApprovedHybridInventoryResponse | null>(null);
  const [selectedHybridServiceLane, setSelectedHybridServiceLane] = useState("");
  const [selectedApprovedHybridCandidateKey, setSelectedApprovedHybridCandidateKey] = useState("");
  const [publishChannel, setPublishChannel] = useState<Channel>("instagram");
  const [publishCaptionDraft, setPublishCaptionDraft] = useState("");
  const [publishHashtagDraft, setPublishHashtagDraft] = useState("");
  const [publishThumbnailDraft, setPublishThumbnailDraft] = useState("콘텐츠 미리보기");
  const [statusTick, setStatusTick] = useState(0);
  const [mobileSection, setMobileSection] = useState<MobileWorkspaceSection>("wizard");
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const focusMobileSection = (section: MobileWorkspaceSection) => {
    setMobileSection(section);
    if (typeof window === "undefined") return;
    window.requestAnimationFrame(() => {
      document.getElementById(`workspace-${section}`)?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    });
  };

  const loadProjectList = async () => {
    const projectList = await listProjects();
    setProjects(projectList.items);
  };

  const loadProject = async (projectId: string) => {
    const [detail, assetsResponse] = await Promise.all([getProjectDetail(projectId), getProjectAssets(projectId)]);
    setSelectedProject({ project: detail, assets: assetsResponse.assets });
    setSelectedProjectId(projectId);
    setWizard({
      businessType: detail.businessType,
      regionName: detail.regionName,
      detailLocation: detail.detailLocation ?? "",
      purpose: detail.purpose,
      style: detail.style,
      channels: detail.channels,
      templateId: templateForPurpose(detail.purpose),
      thumbnailText: "",
    });
    setDraftFiles([]);
    const status = await getGenerationStatus(projectId);
    setGenerationStatus(status);
    if (status.result) {
      const result = await getProjectResult(projectId).catch(() => null);
      if (result) setActiveResult(result);
    }
  };

  const refreshUploadJob = async () => {
    if (!activeUploadJobId) return;
    const job = await getUploadJob(activeUploadJobId).catch(() => null);
    if (job) setUploadJob(job);
  };

  const bootstrap = async () => {
    const [projectList, inventory] = await Promise.all([
      listProjects(),
      listApprovedHybridCandidates().catch(() => null),
    ]);
    setProjects(projectList.items);
    setApprovedHybridInventory(inventory);
    const nextProject =
      projectList.items.find((project) => project.projectId === requestedProjectId) ??
      projectList.items[0];
    if (nextProject) {
      await loadProject(nextProject.projectId);
      if (requestedUploadJobId) {
        const job = await getUploadJob(requestedUploadJobId).catch(() => null);
        if (job) {
          setActiveUploadJobId(requestedUploadJobId);
          setUploadJob(job);
        }
      }
    }
  };

  useEffect(() => {
    void bootstrap();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [requestedProjectId, requestedUploadJobId]);

  useEffect(() => {
    if (!selectedProjectId) return;
    const timer = window.setInterval(async () => {
      const status = await getGenerationStatus(selectedProjectId).catch(() => null);
      if (status) {
        setGenerationStatus(status);
        if (status.projectStatus === "generated" || status.result) {
          const result = await getProjectResult(selectedProjectId).catch(() => null);
          if (result) setActiveResult(result);
        }
        await loadProjectList();
      }
      if (activeUploadJobId) {
        const job = await getUploadJob(activeUploadJobId).catch(() => null);
        if (job) setUploadJob(job);
      }
      setStatusTick((value) => value + 1);
    }, 2200);
    return () => window.clearInterval(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedProjectId, activeUploadJobId]);

  useEffect(() => {
    if (!selectedApprovedHybridCandidateKey) return;
    const candidateExists = approvedHybridInventory?.items.some((item) => item.candidateKey === selectedApprovedHybridCandidateKey) ?? false;
    if (!candidateExists) {
      setSelectedApprovedHybridCandidateKey("");
    }
  }, [approvedHybridInventory, selectedApprovedHybridCandidateKey]);

  useEffect(() => {
    if (!activeResult) return;
    setPublishCaptionDraft(activeResult.copySet.captions[0] ?? activeResult.copySet.hookText ?? "");
    setPublishHashtagDraft((activeResult.copySet.hashtags ?? []).join(" "));
    setPublishThumbnailDraft(wizard.thumbnailText || "콘텐츠 미리보기");
    setPublishChannel("instagram");
  }, [activeResult?.variantId]);

  useEffect(() => {
    if (!selectedHybridServiceLane) return;
    const laneExists = Boolean(approvedHybridInventory?.laneCounts[selectedHybridServiceLane]);
    if (!laneExists) {
      setSelectedHybridServiceLane("");
    }
  }, [approvedHybridInventory, selectedHybridServiceLane]);

  const syncProjectById = async (projectId: string) => {
    startTransition(() => {
      void loadProject(projectId)
        .then(() => focusMobileSection("result"))
        .catch((error) => setFeedback(error instanceof Error ? error.message : "프로젝트를 불러오지 못했습니다."));
    });
  };

  const createDemoProject = async () => {
    const files = draftFiles;
    if (!files.length) {
      setFeedback("사진을 올리시거나 샘플 사진 채우기를 눌러 주세요.");
      focusMobileSection("wizard");
      return;
    }
    const approvedHybridSourceCandidateKey = selectedApprovedHybridCandidateKey || undefined;
    const projectPayload = {
      businessType: wizard.businessType,
      regionName: wizard.regionName,
      detailLocation: wizard.detailLocation || null,
      purpose: wizard.purpose,
      style: wizard.style,
      channels: wizard.channels,
    };

    const created = await createProject(projectPayload);
    const uploaded = await uploadAssets(created.projectId, files);
    const generation = await startGeneration(created.projectId, {
      assetIds: uploaded.assets.map((asset) => asset.assetId),
      templateId: wizard.templateId,
      quickOptions: {
        highlightPrice: false,
        shorterCopy: false,
        emphasizeRegion: false,
      },
      ...(approvedHybridSourceCandidateKey ? { approvedHybridSourceCandidateKey } : {}),
    });

    setSelectedProjectId(created.projectId);
    setFeedback(
      `생성 요청 완료: ${generation.generationRunId.slice(0, 8)}${approvedHybridSourceCandidateKey ? " · approved hybrid 기준선 적용" : ""}`,
    );
    setActiveResult(null);
    setActiveUploadJobId(null);
    await Promise.all([loadProjectList(), loadProject(created.projectId)]);
    focusMobileSection("result");
  };

  const regenerateWithChangeSet = async (changeSet: Record<string, unknown>) => {
    if (!selectedProjectId) return;
    const normalized = {
      highlightPrice: Boolean(changeSet.highlightPrice),
      shorterCopy: Boolean(changeSet.shorterCopy),
      emphasizeRegion: Boolean(changeSet.emphasizeRegion),
      templateId: (changeSet.templateId as TemplateId | undefined) ?? wizard.templateId,
      styleOverride: changeSet.styleOverride as Style | undefined,
      approvedHybridSourceCandidateKey: selectedApprovedHybridCandidateKey || undefined,
    };
    const response = await regenerateProject(selectedProjectId, { changeSet: normalized });
    setFeedback(
      `재생성 요청 완료: ${response.generationRunId.slice(0, 8)}${normalized.approvedHybridSourceCandidateKey ? " · approved hybrid 기준선 적용" : ""}`,
    );
    setActiveResult(null);
    await loadProject(selectedProjectId);
  };

  const handlePublish = async (publishMode: "auto" | "assist", channel: Channel = "instagram") => {
    if (!selectedProjectId || !activeResult) return;
    const normalizedHashtags = normalizeHashtagDraft(publishHashtagDraft);
    const response = await publishProject(selectedProjectId, {
      variantId: activeResult.variantId,
      channel,
      publishMode,
      captionOverride: publishCaptionDraft.trim() || activeResult.copySet.captions[0],
      hashtags: normalizedHashtags.length ? normalizedHashtags : activeResult.copySet.hashtags,
      thumbnailText: publishThumbnailDraft.trim() || "콘텐츠 미리보기",
    });
    setActiveUploadJobId(response.uploadJobId);
    const job = await getUploadJob(response.uploadJobId).catch(() => null);
    setUploadJob(
      job ?? {
        uploadJobId: response.uploadJobId,
        projectId: response.projectId,
        channel,
        status: response.status,
        assistPackage: response.assistPackage,
        error: null,
      },
    );
    setFeedback(
      job?.error?.message
        ? job.error.message
        : response.status === "assist_required"
          ? "업로드에 필요한 파일과 문구를 준비했습니다."
          : "업로드를 시작했습니다.",
    );
    await loadProjectList();
    focusMobileSection("result");
  };

  const handleAssistComplete = async () => {
    if (!activeUploadJobId) return;
    const job = await completeAssist(activeUploadJobId);
    setUploadJob(job);
    setFeedback("업로드 보조 완료를 기록했습니다.");
    await loadProjectList();
    focusMobileSection("result");
  };

  const sampleFill = () => {
    setDraftFiles(demoFiles());
    setFeedback("샘플 사진 2장을 채웠습니다.");
    setMobileSection("wizard");
  };

  const selectedTemplate = TEMPLATES.find((template) => template.templateId === wizard.templateId) ?? TEMPLATES[0];
  const selectedAssets = selectedProject?.assets ?? [];
  const laneHintAssetFileNames =
    draftFiles.length > 0
      ? draftFiles.map((file) => file.name)
      : selectedAssets.length > 0
        ? selectedAssets.map((asset) => asset.fileName)
        : [];
  const hybridLaneHint = inferHybridLaneHint({
    businessType: wizard.businessType,
    templateId: wizard.templateId,
    assetFileNames: laneHintAssetFileNames,
    inventory: approvedHybridInventory,
  });
  const inferredHybridServiceLane = hybridLaneHint.lane;
  const inventoryServiceLaneOptions = Object.keys(approvedHybridInventory?.laneCounts ?? {});
  const recommendedHybridCandidates = (
    selectedHybridServiceLane
      ? [approvedHybridInventory?.recommendedByLane?.[selectedHybridServiceLane]].filter(Boolean)
      : Object.values(approvedHybridInventory?.recommendedByLane ?? {})
  ) as ApprovedHybridCandidateItem[];
  const filteredApprovedHybridCandidates = (
    approvedHybridInventory?.items.filter((item) => !selectedHybridServiceLane || item.serviceLane === selectedHybridServiceLane) ?? []
  ) as ApprovedHybridCandidateItem[];
  const inferredHybridCandidate =
    inferredHybridServiceLane && approvedHybridInventory?.recommendedByLane?.[inferredHybridServiceLane]
      ? (approvedHybridInventory.recommendedByLane[inferredHybridServiceLane] as ApprovedHybridCandidateItem)
      : null;
  const activeApprovedHybridCandidate =
    approvedHybridInventory?.items.find((item) => item.candidateKey === selectedApprovedHybridCandidateKey) ?? null;
  const currentPurposeLabel = PURPOSE_LABELS[wizard.purpose].title;
  const progressPercent = !generationStatus?.steps?.length
    ? 0
    : Math.round((generationStatus.steps.filter((step) => step.status === "completed").length / generationStatus.steps.length) * 100);
  const activeProject = projects.find((project) => project.projectId === selectedProjectId) ?? projects[0] ?? null;
  const previewHeadline = activeResult?.copySet.hookText ?? `${wizard.regionName}에서 ${PURPOSE_LABELS[wizard.purpose].title}를 보여줍니다`;
  const previewSubtitle = activeResult?.copySet.ctaText ?? selectedTemplate.description;
  const activeDetailLocation = selectedProject?.project.detailLocation ?? wizard.detailLocation;
  const activeResultTemplateId = (activeResult?.video.templateId ?? wizard.templateId) as TemplateId;
  const preferredTemplateId = templateForPurpose(wizard.purpose);
  const quickActionRecommendations = activeResult
    ? recommendQuickActions({
        result: activeResult,
        purpose: wizard.purpose,
        detailLocation: activeDetailLocation,
        currentTemplateId: activeResultTemplateId,
        currentStyle: wizard.style,
        preferredTemplateId,
      })
    : [];
  const quickActionRecommendationMap = new Map(quickActionRecommendations.map((item) => [item.actionId, item]));
  const timelineSteps: GenerationStep[] =
    generationStatus?.steps?.length
      ? generationStatus.steps
      : (["preprocessing", "copy_generation", "video_rendering", "post_rendering", "packaging"] as const).map((name) => ({
          name,
          status: "pending",
        }));
  const mobileActionCaption =
    uploadJob?.status === "assist_required"
      ? "업로드를 마친 뒤 완료만 눌러 주시면 됩니다."
      : activeResult
        ? "결과를 확인하고 문구를 다듬은 뒤 업로드 준비를 진행하시면 됩니다."
        : "설정과 사진을 확인한 뒤 바로 생성할 수 있습니다.";
  const mobilePhotoCaption =
    draftFiles.length > 0 ? `${draftFiles.length}장 준비됨` : selectedAssets.length > 0 ? `${selectedAssets.length}장 업로드됨` : "사진 선택 필요";
  const mobileResultCaption =
    uploadJob?.status === "assist_required"
      ? "업로드 보조 필요"
      : activeResult
        ? "결과 준비 완료"
        : generationStatus
          ? `${progressPercent}% 진행 중`
          : "아직 결과 없음";
  const publishHashtagCount = normalizeHashtagDraft(publishHashtagDraft).length;

  return (
    <div className="app-shell">
      <section className="hero">
        <div className="hero-inner">
          <div>
            <span className="eyebrow">사진 몇 장으로 바로 시작</span>
            <h1>가게 사진으로 업로드용 숏폼을 빠르게 준비합니다.</h1>
            <p>
              사진을 올리고, 결과를 확인하고, 문구를 다듬은 뒤, 바로 업로드할 수 있는 패키지까지 한 번에 준비합니다.
            </p>
            <div className="hero-actions">
              <button className="button button-primary" disabled={isPending} onClick={() => void createDemoProject()}>
                새 프로젝트 생성
              </button>
              <button className="button button-secondary" onClick={sampleFill}>
                샘플 사진 채우기
              </button>
              <button className="button button-ghost" onClick={() => void loadProjectList()}>
                목록 새로고침
              </button>
            </div>
          </div>
          <div
            style={{
              minHeight: 320,
              borderRadius: 28,
              border: "1px solid rgba(29,22,17,0.08)",
              background:
                "radial-gradient(circle at 20% 20%, rgba(229,106,76,0.26), transparent 28%), radial-gradient(circle at 80% 80%, rgba(34,107,95,0.2), transparent 22%), linear-gradient(180deg, rgba(255,255,255,0.98), rgba(247,239,230,0.94))",
              display: "grid",
              alignItems: "end",
              padding: 22,
            }}
          >
            <div
              style={{
                borderRadius: 24,
                background: "rgba(255,255,255,0.84)",
                border: "1px solid rgba(29,22,17,0.08)",
                padding: 18,
                display: "grid",
                gap: 12,
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
                <strong style={{ fontSize: "1rem" }}>현재 미리보기</strong>
                <span
                  style={{
                    padding: "6px 10px",
                    borderRadius: 999,
                    background: "rgba(34,107,95,0.1)",
                    color: "#226b5f",
                    fontWeight: 700,
                    fontSize: ".82rem",
                  }}
                >
                  {statusLabel(activeProject?.status)}
                </span>
              </div>
              <div
                style={{
                  aspectRatio: "9 / 16",
                  position: "relative",
                  overflow: "hidden",
                  borderRadius: 22,
                  padding: 18,
                  display: "grid",
                  alignContent: "end",
                  background:
                    "linear-gradient(180deg, rgba(255,255,255,0.05), rgba(17,16,16,0.65)), radial-gradient(circle at 30% 20%, rgba(242,166,90,0.5), transparent 22%), linear-gradient(180deg, #755846, #2a231e)",
                  color: "white",
                }}
              >
                {activeResult ? (
                  <video
                    key={activeResult.video.url}
                    src={resolveMediaUrl(activeResult.video.url)}
                    autoPlay
                    loop
                    muted
                    playsInline
                    style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", opacity: 0.82 }}
                  />
                ) : null}
                <div
                  style={{
                    position: "absolute",
                    inset: 0,
                    background: "linear-gradient(180deg, rgba(17,16,16,0.08), rgba(17,16,16,0.72))",
                  }}
                />
                <div style={{ position: "relative", zIndex: 1 }}>
                  <div style={{ fontSize: "1.55rem", fontWeight: 800, lineHeight: 1.2 }}>{previewHeadline}</div>
                  <div style={{ marginTop: 10, color: "rgba(255,255,255,0.82)", lineHeight: 1.55 }}>{previewSubtitle}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mobile-workspace-nav" aria-label="모바일 작업 빠른 이동">
        <button
          className={mobileSection === "wizard" ? "mobile-workspace-nav__item mobile-workspace-nav__item--active" : "mobile-workspace-nav__item"}
          onClick={() => focusMobileSection("wizard")}
        >
          <strong>설정/사진</strong>
          <span>{mobilePhotoCaption}</span>
        </button>
        <button
          className={mobileSection === "result" ? "mobile-workspace-nav__item mobile-workspace-nav__item--active" : "mobile-workspace-nav__item"}
          onClick={() => focusMobileSection("result")}
        >
          <strong>결과/게시</strong>
          <span>{mobileResultCaption}</span>
        </button>
        <button
          className={mobileSection === "recent" ? "mobile-workspace-nav__item mobile-workspace-nav__item--active" : "mobile-workspace-nav__item"}
          onClick={() => focusMobileSection("recent")}
        >
          <strong>프로젝트</strong>
          <span>{projects.length}건 저장됨</span>
        </button>
      </section>

      <div className="workspace">
        <aside id="workspace-recent" className="panel workspace__recent">
          <div className="panel-header">
            <div>
              <h2 className="panel-title">최근 프로젝트</h2>
              <p className="panel-subtitle">이미 있는 것과 없는 것을 빠르게 확인합니다.</p>
            </div>
            <span className="eyebrow">{projects.length}건</span>
          </div>
          <div className="panel-body" style={{ display: "grid", gap: 12 }}>
            {projects.map((project) => (
              <button
                key={project.projectId}
                onClick={() => void syncProjectById(project.projectId)}
                className="button button-secondary"
                style={{
                  minHeight: "unset",
                  width: "100%",
                  justifyContent: "space-between",
                  alignItems: "start",
                  padding: 16,
                  textAlign: "left",
                  borderColor: project.projectId === selectedProjectId ? "rgba(229,106,76,0.45)" : "rgba(29,22,17,0.08)",
                }}
              >
                <span style={{ display: "grid", gap: 6 }}>
                  <strong>{BUSINESS_LABELS[project.businessType]} · {PURPOSE_LABELS[project.purpose].title}</strong>
                  <span style={{ color: "var(--muted)", fontSize: ".92rem" }}>{STYLE_LABELS[project.style].title}</span>
                </span>
                <span
                  style={{
                    padding: "6px 10px",
                    borderRadius: 999,
                    background: statusTone(project.status) === "good" ? "rgba(34,107,95,0.12)" : statusTone(project.status) === "danger" ? "rgba(229,106,76,0.12)" : "rgba(29,22,17,0.08)",
                    color: statusTone(project.status) === "good" ? "#226b5f" : statusTone(project.status) === "danger" ? "#c25337" : "var(--text)",
                    fontWeight: 800,
                    fontSize: ".8rem",
                  }}
                >
                  {statusLabel(project.status)}
                </span>
              </button>
            ))}

            <div
              style={{
                marginTop: 8,
                padding: 16,
                borderRadius: 8,
                border: "1px solid rgba(29,22,17,0.08)",
                background: "rgba(255,255,255,0.72)",
                display: "grid",
                gap: 12,
              }}
            >
              <div>
                <strong>업로드 방식</strong>
                <p className="panel-subtitle" style={{ marginTop: 6 }}>
                  지금은 자동 게시보다, 업로드용 패키지를 바로 준비해 드리는 흐름을 우선 제공합니다.
                </p>
              </div>
              <div
                style={{
                  display: "grid",
                  gap: 8,
                  padding: 12,
                  borderRadius: 8,
                  border: "1px solid rgba(29,22,17,0.08)",
                  background: "rgba(255,255,255,0.88)",
                }}
              >
                <div>1. 영상과 게시글 이미지를 준비합니다.</div>
                <div>2. 캡션과 해시태그를 복사할 수 있게 묶어 드립니다.</div>
                <div>3. 업로드를 마친 뒤 완료만 눌러 상태를 정리합니다.</div>
              </div>
            </div>
          </div>
        </aside>

        <main id="workspace-wizard" className="panel workspace__wizard">
          <div className="panel-header">
            <div>
              <h2 className="panel-title">생성 마법사</h2>
              <p className="panel-subtitle">한 화면에서 업종, 목적, 스타일, 채널, 사진, 템플릿을 조정합니다.</p>
            </div>
            <span className="eyebrow">{currentPurposeLabel}</span>
          </div>
          <div className="panel-body" style={{ display: "grid", gap: 18 }}>
            <section style={{ display: "grid", gap: 12 }}>
              <strong>1. 업종 · 목적 · 스타일</strong>
              <div style={{ display: "grid", gap: 12, gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))" }}>
                {BUSINESS_TYPES.map((business) => (
                  <button
                    key={business}
                    className={wizard.businessType === business ? "button button-primary" : "button button-secondary"}
                    onClick={() => setWizard((prev) => ({ ...prev, businessType: business }))}
                  >
                    {BUSINESS_LABELS[business]}
                  </button>
                ))}
              </div>
              <div style={{ display: "grid", gap: 12, gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" }}>
                {(Object.keys(PURPOSE_LABELS) as Purpose[]).map((purpose) => (
                  <button
                    key={purpose}
                    className={wizard.purpose === purpose ? "button button-primary" : "button button-secondary"}
                    onClick={() =>
                      setWizard((prev) => ({
                        ...prev,
                        purpose,
                        templateId: templateForPurpose(purpose),
                      }))
                    }
                    style={{ minHeight: 82, flexDirection: "column", alignItems: "start" }}
                  >
                    <span>{PURPOSE_LABELS[purpose].title}</span>
                    <span style={{ fontSize: ".84rem", opacity: 0.82 }}>{PURPOSE_LABELS[purpose].hint}</span>
                  </button>
                ))}
              </div>
              <div style={{ display: "grid", gap: 12, gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" }}>
                {STYLES.map((style) => (
                  <button
                    key={style}
                    className={wizard.style === style ? "button button-primary" : "button button-secondary"}
                    onClick={() => setWizard((prev) => ({ ...prev, style }))}
                    style={{ minHeight: 84, flexDirection: "column", alignItems: "start" }}
                  >
                    <span>{STYLE_LABELS[style].title}</span>
                    <span style={{ fontSize: ".84rem", opacity: 0.82 }}>{STYLE_LABELS[style].hint}</span>
                  </button>
                ))}
              </div>
            </section>

            <section style={{ display: "grid", gap: 12 }}>
              <strong>2. 위치 · 채널 · 템플릿</strong>
              <div style={{ display: "grid", gap: 12, gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))" }}>
                <label style={{ display: "grid", gap: 8 }}>
                  <span>지역명</span>
                  <input
                    value={wizard.regionName}
                    onChange={(event) => setWizard((prev) => ({ ...prev, regionName: event.target.value }))}
                    style={{ minHeight: 52, borderRadius: 16, border: "1px solid var(--line)", padding: "0 14px", background: "rgba(255,255,255,0.9)" }}
                  />
                </label>
                <label style={{ display: "grid", gap: 8 }}>
                  <span>상세 위치</span>
                  <input
                    value={wizard.detailLocation}
                    onChange={(event) => setWizard((prev) => ({ ...prev, detailLocation: event.target.value }))}
                    style={{ minHeight: 52, borderRadius: 16, border: "1px solid var(--line)", padding: "0 14px", background: "rgba(255,255,255,0.9)" }}
                  />
                </label>
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
                {CHANNELS.map((channel) => {
                  const selected = wizard.channels.includes(channel);
                  return (
                    <button
                      key={channel}
                      className={selected ? "button button-primary" : "button button-secondary"}
                      onClick={() =>
                        setWizard((prev) => ({
                          ...prev,
                          channels: selected ? prev.channels.filter((value) => value !== channel) : [...prev.channels, channel],
                        }))
                      }
                    >
                      {CHANNEL_LABELS[channel].title} · {CHANNEL_LABELS[channel].tier}
                    </button>
                  );
                })}
              </div>
              <div style={{ display: "grid", gap: 12, gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" }}>
                {TEMPLATES.filter((template) => template.supportedPurposes.includes(wizard.purpose)).map((template) => (
                  <button
                    key={template.templateId}
                    className={wizard.templateId === template.templateId ? "button button-primary" : "button button-secondary"}
                    onClick={() => setWizard((prev) => ({ ...prev, templateId: template.templateId }))}
                    style={{ minHeight: 84, flexDirection: "column", alignItems: "start" }}
                  >
                    <span>{templateLabel(template.templateId)}</span>
                    <span style={{ fontSize: ".84rem", opacity: 0.82 }}>{template.description}</span>
                  </button>
                ))}
              </div>
              {approvedHybridInventory ? (
                <details
                  style={{
                    display: "grid",
                    gap: 12,
                    padding: 16,
                    borderRadius: 8,
                    border: "1px solid rgba(34,107,95,0.16)",
                    background: "rgba(34,107,95,0.06)",
                  }}
                >
                  <summary style={{ cursor: "pointer", fontWeight: 800 }}>고급 설정 열기</summary>
                  <div style={{ height: 4 }} />
                  <div style={{ display: "grid", gap: 6 }}>
                    <strong>승인된 hybrid 기준선 선택</strong>
                    <div style={{ color: "var(--muted)", fontSize: ".9rem", lineHeight: 1.55 }}>
                      현재 approved inventory {approvedHybridInventory.itemCount}건을 읽었습니다. 이 설정은 내부 검토용 기준선을 직접 붙일 때만 사용합니다.
                    </div>
                  </div>
                  <div
                    style={{
                      display: "grid",
                      gap: 10,
                      padding: 14,
                      borderRadius: 16,
                      border: "1px solid rgba(29,22,17,0.08)",
                      background: "rgba(255,255,255,0.74)",
                    }}
                  >
                    <strong>임시 lane hint</strong>
                    <div style={{ color: "var(--muted)", fontSize: ".9rem", lineHeight: 1.55 }}>
                      업종, 템플릿, 업로드 파일명과 approved inventory label 매칭을 함께 점수화합니다. 다만 이 단계에서도 candidate는 자동으로 붙이지 않고, 운영자가 직접 적용합니다.
                    </div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
                      <button
                        className={selectedHybridServiceLane === "" ? "button button-primary" : "button button-secondary"}
                        onClick={() => setSelectedHybridServiceLane("")}
                      >
                        전체 보기
                      </button>
                      {inventoryServiceLaneOptions.map((lane) => (
                        <button
                          key={lane}
                          className={selectedHybridServiceLane === lane ? "button button-primary" : "button button-secondary"}
                          onClick={() => setSelectedHybridServiceLane(lane)}
                        >
                          {HYBRID_LANE_LABELS[lane] ?? lane} · {approvedHybridInventory.laneCounts[lane]}건
                        </button>
                      ))}
                    </div>
                    {inferredHybridServiceLane && inferredHybridCandidate ? (
                      <div
                        style={{
                          display: "grid",
                          gap: 8,
                          padding: 12,
                          borderRadius: 14,
                          border: "1px solid rgba(34,107,95,0.16)",
                          background: "rgba(34,107,95,0.08)",
                        }}
                      >
                        <div style={{ fontWeight: 800 }}>
                          현재 설정 기준 추천 lane: {HYBRID_LANE_LABELS[inferredHybridServiceLane] ?? inferredHybridServiceLane} · confidence {hybridLaneHint.confidence}
                        </div>
                        <div style={{ color: "var(--muted)", fontSize: ".9rem", lineHeight: 1.55 }}>
                          추천 candidate: {inferredHybridCandidate.label} · {inferredHybridCandidate.provider} ·{" "}
                          {HYBRID_APPROVAL_SOURCE_LABELS[inferredHybridCandidate.approvalSource] ?? inferredHybridCandidate.approvalSource}
                        </div>
                        {hybridLaneHint.evidence.length > 0 ? (
                          <div style={{ display: "grid", gap: 6 }}>
                            {hybridLaneHint.evidence.map((reason) => (
                              <div key={reason} style={{ color: "var(--muted)", fontSize: ".88rem", lineHeight: 1.5 }}>
                                - {reason}
                              </div>
                            ))}
                          </div>
                        ) : null}
                        {hybridLaneHint.consideredAssetFileNames.length > 0 ? (
                          <div style={{ color: "var(--muted)", fontSize: ".84rem", lineHeight: 1.5 }}>
                            파일 기준: {hybridLaneHint.consideredAssetFileNames.join(", ")}
                          </div>
                        ) : null}
                        <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
                          <button
                            className="button button-secondary"
                            onClick={() => setSelectedHybridServiceLane(inferredHybridServiceLane)}
                          >
                            이 lane 보기
                          </button>
                          <button
                            className="button button-primary"
                            onClick={() => {
                              setSelectedHybridServiceLane(inferredHybridServiceLane);
                              setSelectedApprovedHybridCandidateKey(inferredHybridCandidate.candidateKey);
                            }}
                          >
                            추천 candidate 적용
                          </button>
                        </div>
                      </div>
                    ) : hybridLaneHint.confidence === "none" ? (
                      <div
                        style={{
                          display: "grid",
                          gap: 8,
                          padding: 12,
                          borderRadius: 14,
                          border: "1px dashed rgba(29,22,17,0.12)",
                          background: "rgba(255,255,255,0.62)",
                        }}
                      >
                        <div style={{ fontWeight: 800 }}>현재 설정만으로는 명확한 lane hint가 없습니다.</div>
                        {hybridLaneHint.evidence.map((reason) => (
                          <div key={reason} style={{ color: "var(--muted)", fontSize: ".88rem", lineHeight: 1.5 }}>
                            - {reason}
                          </div>
                        ))}
                        {hybridLaneHint.consideredAssetFileNames.length > 0 ? (
                          <div style={{ color: "var(--muted)", fontSize: ".84rem", lineHeight: 1.5 }}>
                            파일 기준: {hybridLaneHint.consideredAssetFileNames.join(", ")}
                          </div>
                        ) : (
                          <div style={{ color: "var(--muted)", fontSize: ".84rem", lineHeight: 1.5 }}>
                            업로드 파일명 근거가 아직 없어 업종/템플릿 신호만으로는 확정하지 않았습니다.
                          </div>
                        )}
                      </div>
                    ) : null}
                  </div>
                  {recommendedHybridCandidates.length > 0 ? (
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
                      {recommendedHybridCandidates.map((candidate) => (
                        <button
                          key={candidate.candidateKey}
                          className={selectedApprovedHybridCandidateKey === candidate.candidateKey ? "button button-primary" : "button button-secondary"}
                          onClick={() => {
                            setSelectedHybridServiceLane(candidate.serviceLane);
                            setSelectedApprovedHybridCandidateKey(candidate.candidateKey);
                          }}
                          style={{ minHeight: 76, flexDirection: "column", alignItems: "start" }}
                        >
                          <span>
                            {candidate.label} · {HYBRID_LANE_LABELS[candidate.serviceLane] ?? candidate.serviceLane}
                          </span>
                          <span style={{ fontSize: ".8rem", opacity: 0.82 }}>
                            {HYBRID_APPROVAL_SOURCE_LABELS[candidate.approvalSource] ?? candidate.approvalSource}
                          </span>
                        </button>
                      ))}
                      <button
                        className={selectedApprovedHybridCandidateKey ? "button button-ghost" : "button button-primary"}
                        onClick={() => setSelectedApprovedHybridCandidateKey("")}
                        style={{ minHeight: 76 }}
                      >
                        사용 안 함
                      </button>
                    </div>
                  ) : null}
                  <label style={{ display: "grid", gap: 8 }}>
                    <span>approved candidate key</span>
                    <select
                      value={selectedApprovedHybridCandidateKey}
                      onChange={(event) => {
                        const nextCandidateKey = event.target.value;
                        const matchedCandidate = approvedHybridInventory.items.find((candidate) => candidate.candidateKey === nextCandidateKey) ?? null;
                        setSelectedApprovedHybridCandidateKey(nextCandidateKey);
                        if (matchedCandidate) {
                          setSelectedHybridServiceLane(matchedCandidate.serviceLane);
                        }
                      }}
                      style={{ minHeight: 52, borderRadius: 16, border: "1px solid var(--line)", padding: "0 14px", background: "rgba(255,255,255,0.9)" }}
                    >
                      <option value="">사용 안 함</option>
                      {filteredApprovedHybridCandidates.map((candidate) => (
                        <option key={candidate.candidateKey} value={candidate.candidateKey}>
                          {candidate.label} · {HYBRID_LANE_LABELS[candidate.serviceLane] ?? candidate.serviceLane} · {candidate.provider}
                        </option>
                      ))}
                    </select>
                  </label>
                  {activeApprovedHybridCandidate ? (
                    <div
                      style={{
                        display: "grid",
                        gap: 8,
                        padding: 14,
                        borderRadius: 16,
                        border: "1px solid rgba(29,22,17,0.08)",
                        background: "rgba(255,255,255,0.78)",
                      }}
                    >
                      <strong>{activeApprovedHybridCandidate.candidateKey}</strong>
                      <div style={{ color: "var(--muted)", fontSize: ".9rem", lineHeight: 1.55 }}>
                        {HYBRID_APPROVAL_SOURCE_LABELS[activeApprovedHybridCandidate.approvalSource] ?? activeApprovedHybridCandidate.approvalSource}
                        {" · "}
                        {activeApprovedHybridCandidate.selectionMode}
                        {" · "}
                        MSE {typeof activeApprovedHybridCandidate.midFrameMse === "number" ? activeApprovedHybridCandidate.midFrameMse.toFixed(2) : "-"}
                        {" · "}
                        RGB diff {typeof activeApprovedHybridCandidate.motionAvgRgbDiff === "number" ? activeApprovedHybridCandidate.motionAvgRgbDiff.toFixed(2) : "-"}
                      </div>
                    </div>
                  ) : (
                    <div
                      style={{
                        padding: 14,
                        borderRadius: 16,
                        border: "1px dashed rgba(29,22,17,0.12)",
                        color: "var(--muted)",
                        background: "rgba(255,255,255,0.52)",
                      }}
                    >
                      현재는 승인된 hybrid 기준선을 사용하지 않습니다.
                    </div>
                  )}
                </details>
              ) : (
                <div
                  style={{
                    padding: 14,
                    borderRadius: 8,
                    border: "1px dashed rgba(29,22,17,0.12)",
                    color: "var(--muted)",
                    background: "rgba(255,255,255,0.52)",
                  }}
                >
                    고급 기준선을 아직 읽지 못했습니다. 이 설정은 사용자 테스트 없이도 바로 사용하실 수 있습니다.
                  </div>
              )}
              <details
                style={{
                  display: "grid",
                  gap: 12,
                  padding: 16,
                  borderRadius: 8,
                  border: "1px solid rgba(29,22,17,0.08)",
                  background: "rgba(255,255,255,0.72)",
                }}
              >
                <summary style={{ cursor: "pointer", fontWeight: 800 }}>카피 정책 보기</summary>
                <CopyPolicySummary
                  purpose={wizard.purpose}
                  templateId={wizard.templateId}
                  detailLocation={wizard.detailLocation}
                  title="현재 템플릿 카피 정책"
                  description="선택한 조합에서 상세 위치를 어디까지 노출하지 않는지 확인합니다."
                />
              </details>
            </section>

            <section style={{ display: "grid", gap: 12 }}>
              <strong>3. 사진 업로드</strong>
              <div style={{ display: "grid", gap: 10, gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))" }}>
                {[
                  "제품을 가운데 두세요",
                  "배경은 단순하게 정리하세요",
                  "흔들리지 않게 밝은 곳에서 찍으세요",
                ].map((guide) => (
                  <div key={guide} style={{ borderRadius: 16, border: "1px solid rgba(29,22,17,0.08)", padding: 14, background: "rgba(255,255,255,0.72)" }}>
                    {guide}
                  </div>
                ))}
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept=".png,.jpg,.jpeg,.svg"
                  style={{ display: "none" }}
                  onChange={(event) => setDraftFiles(Array.from(event.target.files ?? []))}
                />
                <button className="button button-secondary" onClick={() => fileInputRef.current?.click()}>
                  파일 선택
                </button>
                <button className="button button-ghost" onClick={sampleFill}>
                  샘플 자산 사용
                </button>
              </div>
              <div style={{ display: "grid", gap: 10, gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))" }}>
                {(draftFiles.length ? draftFiles : []).map((file, index) => (
                  <div key={`${file.name}-${index}`} style={{ borderRadius: 18, border: "1px solid rgba(29,22,17,0.08)", padding: 14, background: "rgba(255,255,255,0.76)" }}>
                    <strong>{file.name}</strong>
                    <div style={{ color: "var(--muted)", marginTop: 8, fontSize: ".9rem" }}>{Math.max(1, Math.round(file.size / 1024))} KB</div>
                  </div>
                ))}
              </div>
              {!draftFiles.length ? (
                <div
                  style={{
                    padding: 14,
                    borderRadius: 8,
                    border: "1px dashed rgba(29,22,17,0.12)",
                    background: "rgba(255,255,255,0.62)",
                    color: "var(--muted)",
                    lineHeight: 1.55,
                  }}
                >
                  아직 사진이 없습니다. 직접 올리시거나 샘플 사진 채우기를 눌러 흐름을 바로 확인하실 수 있습니다.
                </div>
              ) : null}
              <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
                <button className="button button-primary" disabled={isPending || wizard.channels.length === 0} onClick={() => void createDemoProject()}>
                  생성 시작
                </button>
                <button
                  className="button button-secondary"
                  disabled={!selectedProjectId}
                  onClick={() => selectedProjectId && void syncProjectById(selectedProjectId)}
                >
                  현재 프로젝트 동기화
                </button>
              </div>
              {selectedAssets.length > 0 && (
                <div style={{ display: "grid", gap: 10 }}>
                  {selectedAssets.map((asset) => (
                    <div
                      key={asset.assetId}
                      style={{
                        display: "grid",
                        gap: 8,
                        padding: 14,
                        borderRadius: 16,
                        border: "1px solid rgba(29,22,17,0.08)",
                        background: "rgba(255,255,255,0.76)",
                      }}
                    >
                      <strong>{asset.fileName}</strong>
                      <span style={{ color: "var(--muted)", fontSize: ".9rem" }}>
                        {asset.width}×{asset.height}
                      </span>
                      {asset.warnings.length > 0 && (
                        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                          {asset.warnings.map((warning) => (
                            <span key={warning} style={{ padding: "6px 10px", borderRadius: 999, background: "rgba(229,106,76,0.12)", color: "#c25337", fontSize: ".82rem", fontWeight: 700 }}>
                              {assetWarningText(warning)}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>
        </main>

        <aside id="workspace-result" className="panel workspace__result">
          <div className="panel-header">
            <div>
              <h2 className="panel-title">상태 · 결과 · 게시</h2>
              <p className="panel-subtitle">{feedback}</p>
            </div>
            <span className="eyebrow">{progressPercent}%</span>
          </div>
          <div className="panel-body" style={{ display: "grid", gap: 18 }}>
            <section style={{ display: "grid", gap: 10 }}>
              {timelineSteps.map((step) => (
                <div key={step.name} style={{ borderRadius: 16, border: "1px solid rgba(29,22,17,0.08)", padding: 14, background: "rgba(255,255,255,0.76)" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
                    <strong>{stepTitle(step.name)}</strong>
                    <span
                      style={{
                        padding: "6px 10px",
                        borderRadius: 999,
                        background: statusTone(step.status) === "good" ? "rgba(34,107,95,0.12)" : statusTone(step.status) === "warning" ? "rgba(229,106,76,0.12)" : "rgba(29,22,17,0.08)",
                        color: statusTone(step.status) === "good" ? "#226b5f" : statusTone(step.status) === "warning" ? "#c25337" : "var(--text)",
                        fontWeight: 800,
                        fontSize: ".8rem",
                      }}
                    >
                      {statusLabel(step.status)}
                    </span>
                  </div>
                  <p style={{ color: "var(--muted)", margin: "8px 0 0", lineHeight: 1.55 }}>{stepMessage(step.name)}</p>
                </div>
              ))}
            </section>

            {activeResult ? (
              <section style={{ display: "grid", gap: 12 }}>
                <ResultMediaPreview
                  result={activeResult}
                  description="완성된 영상과 게시글 이미지를 바로 확인하고 저장할 수 있습니다."
                />
              </section>
            ) : null}

            <section style={{ display: "grid", gap: 12 }}>
              <strong>결과 요약</strong>
              <div style={{ borderRadius: 18, border: "1px solid rgba(29,22,17,0.08)", padding: 16, background: "rgba(255,255,255,0.8)", display: "grid", gap: 12 }}>
                <div style={{ fontSize: "1.2rem", fontWeight: 800, lineHeight: 1.35 }}>{previewHeadline}</div>
                <div style={{ color: "var(--muted)", lineHeight: 1.6 }}>{previewSubtitle}</div>
                {activeResult && (
                  <>
                    <div style={{ display: "grid", gap: 8 }}>
                      {activeResult.copySet.captions.map((caption) => (
                        <div key={caption} style={{ padding: 12, borderRadius: 14, background: "rgba(246,239,230,0.7)" }}>
                          {caption}
                        </div>
                      ))}
                    </div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                      {activeResult.copySet.hashtags.map((hashtag) => (
                        <span key={hashtag} style={{ padding: "6px 10px", borderRadius: 999, background: "rgba(34,107,95,0.12)", color: "#226b5f", fontWeight: 700 }}>
                          {hashtag}
                        </span>
                      ))}
                    </div>
                  </>
                )}
              </div>
            </section>

            {activeResult ? (
              <section style={{ display: "grid", gap: 12 }}>
                <strong>문구 다듬기</strong>
                <div
                  style={{
                    borderRadius: 8,
                    border: "1px solid rgba(29,22,17,0.08)",
                    padding: 16,
                    background: "rgba(255,255,255,0.82)",
                    display: "grid",
                    gap: 12,
                  }}
                >
                  <div style={{ display: "grid", gap: 8 }}>
                    <span style={{ fontWeight: 800 }}>추천 문구 선택</span>
                    <div style={{ display: "grid", gap: 8 }}>
                      {activeResult.copySet.captions.map((caption, index) => (
                        <button
                          key={caption}
                          className={publishCaptionDraft === caption ? "button button-primary" : "button button-secondary"}
                          style={{ justifyContent: "start", minHeight: "unset", paddingTop: 12, paddingBottom: 12 }}
                          onClick={() => setPublishCaptionDraft(caption)}
                        >
                          문구 {index + 1} · {caption}
                        </button>
                      ))}
                    </div>
                  </div>
                  <label style={{ display: "grid", gap: 8 }}>
                    <span style={{ fontWeight: 800 }}>업로드 캡션</span>
                    <textarea
                      value={publishCaptionDraft}
                      onChange={(event) => setPublishCaptionDraft(event.target.value)}
                      rows={4}
                      style={{ borderRadius: 8, border: "1px solid var(--line)", padding: 12, background: "rgba(255,255,255,0.94)", resize: "vertical", lineHeight: 1.6 }}
                    />
                  </label>
                  <label style={{ display: "grid", gap: 8 }}>
                    <span style={{ fontWeight: 800 }}>해시태그</span>
                    <textarea
                      value={publishHashtagDraft}
                      onChange={(event) => setPublishHashtagDraft(event.target.value)}
                      rows={3}
                      style={{ borderRadius: 8, border: "1px solid var(--line)", padding: 12, background: "rgba(255,255,255,0.94)", resize: "vertical", lineHeight: 1.6 }}
                    />
                    <span style={{ color: "var(--muted)", fontSize: ".88rem" }}>{publishHashtagCount}개 태그 준비됨</span>
                  </label>
                  <label style={{ display: "grid", gap: 8 }}>
                    <span style={{ fontWeight: 800 }}>썸네일 문구</span>
                    <input
                      value={publishThumbnailDraft}
                      onChange={(event) => setPublishThumbnailDraft(event.target.value)}
                      style={{ minHeight: 48, borderRadius: 8, border: "1px solid var(--line)", padding: "0 12px", background: "rgba(255,255,255,0.94)" }}
                    />
                  </label>
                </div>
              </section>
            ) : null}

            <section style={{ display: "grid", gap: 12 }}>
              <strong>다시 만들기</strong>
              <div style={{ color: "var(--muted)", fontSize: ".92rem", lineHeight: 1.55 }}>
                영상과 문구를 한 번 더 다르게 만들고 싶을 때, 자주 쓰는 수정 방향만 빠르게 다시 요청할 수 있습니다.
              </div>
              {quickActionRecommendations.length ? (
                <div
                  style={{
                    borderRadius: 16,
                    border: "1px solid rgba(34,107,95,0.18)",
                    background: "rgba(34,107,95,0.08)",
                    padding: 14,
                    display: "grid",
                    gap: 8,
                  }}
                >
                  <strong style={{ fontSize: ".92rem", color: "#226b5f" }}>현재 결과 기준 추천 action</strong>
                  <div style={{ color: "var(--muted)", fontSize: ".9rem", lineHeight: 1.55 }}>
                    {quickActionRecommendations.map((item) => item.reason).join(" ")}
                  </div>
                </div>
              ) : null}
              <div style={{ display: "grid", gap: 10, gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))" }}>
                {QUICK_ACTIONS.map((action) => {
                  const preview = describeQuickActionPreview(action.id, nextTemplateId(wizard.templateId));
                  const recommendation = quickActionRecommendationMap.get(action.id);

                  return (
                    <div
                      key={action.id}
                      style={{
                        display: "grid",
                        gap: 10,
                        borderRadius: 18,
                        border: recommendation ? "1px solid rgba(34,107,95,0.22)" : "1px solid rgba(29,22,17,0.08)",
                        padding: 14,
                        background: recommendation ? "rgba(34,107,95,0.08)" : "rgba(255,255,255,0.76)",
                      }}
                    >
                      {recommendation ? (
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
                          <span
                            style={{
                              padding: "4px 8px",
                              borderRadius: 999,
                              background: "rgba(34,107,95,0.12)",
                              color: "#226b5f",
                              fontSize: ".76rem",
                              fontWeight: 900,
                            }}
                          >
                            추천
                          </span>
                          <span style={{ color: "var(--muted)", fontSize: ".78rem", fontWeight: 700 }}>priority {recommendation.priority}</span>
                        </div>
                      ) : null}
                      <button
                        className="button button-secondary"
                        disabled={!selectedProjectId}
                        onClick={() => {
                          const changeSet =
                            action.id === "highlightPrice"
                              ? { highlightPrice: true }
                              : action.id === "shorterCopy"
                                ? { shorterCopy: true }
                                : action.id === "emphasizeRegion"
                                  ? { emphasizeRegion: true }
                                  : action.id === "friendly"
                                    ? { styleOverride: "friendly" as Style }
                                    : action.id === "fun"
                                      ? { styleOverride: "b_grade_fun" as Style }
                                      : { templateId: nextTemplateId(wizard.templateId) };
                          void regenerateWithChangeSet(changeSet);
                        }}
                      >
                        {action.label}
                      </button>
                      {recommendation ? (
                        <div style={{ color: "#226b5f", fontSize: ".86rem", lineHeight: 1.5, fontWeight: 700 }}>{recommendation.reason}</div>
                      ) : null}
                      {preview ? (
                        <>
                          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                            {preview.affectedLayers.map((layer) => (
                              <span
                                key={`${action.id}-${layer}`}
                                style={{
                                  padding: "4px 8px",
                                  borderRadius: 999,
                                  background:
                                    layer === "hook"
                                      ? "rgba(229,106,76,0.12)"
                                      : layer === "cta"
                                        ? "rgba(34,107,95,0.12)"
                                        : layer === "visual"
                                          ? "rgba(123,245,255,0.12)"
                                          : "rgba(29,22,17,0.08)",
                                  color:
                                    layer === "hook"
                                      ? "#c25337"
                                      : layer === "cta"
                                        ? "#226b5f"
                                        : layer === "visual"
                                          ? "#0f7281"
                                          : "var(--text)",
                                  fontSize: ".76rem",
                                  fontWeight: 800,
                                }}
                              >
                                {layer.toUpperCase()}
                              </span>
                            ))}
                          </div>
                          <div style={{ color: "var(--muted)", fontSize: ".86rem", lineHeight: 1.5 }}>{preview.note}</div>
                        </>
                      ) : null}
                    </div>
                  );
                })}
              </div>
            </section>

            <section style={{ display: "grid", gap: 12 }}>
              <strong>업로드 준비</strong>
              <div style={{ color: "var(--muted)", fontSize: ".92rem", lineHeight: 1.55 }}>
                지금은 자동 게시보다 업로드 보조를 우선 제공합니다. 필요한 파일과 문구를 한 번에 묶어 드립니다.
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
                {CHANNELS.map((channel) => (
                  <button
                    key={channel}
                    className={publishChannel === channel ? "button button-primary" : "button button-secondary"}
                    onClick={() => setPublishChannel(channel)}
                  >
                    {CHANNEL_LABELS[channel].title}
                  </button>
                ))}
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
                <button className="button button-primary" disabled={!activeResult} onClick={() => void handlePublish("assist", publishChannel)}>
                  업로드용 패키지 만들기
                </button>
              </div>
              {uploadJob && (
                <div style={{ borderRadius: 18, border: "1px solid rgba(29,22,17,0.08)", padding: 16, background: "rgba(255,255,255,0.8)", display: "grid", gap: 10 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
                    <strong>{CHANNEL_LABELS[uploadJob.channel].title}</strong>
                    <span
                      style={{
                        padding: "6px 10px",
                        borderRadius: 999,
                        background: statusTone(uploadJob.status) === "good" ? "rgba(34,107,95,0.12)" : statusTone(uploadJob.status) === "danger" ? "rgba(229,106,76,0.12)" : "rgba(29,22,17,0.08)",
                        color: statusTone(uploadJob.status) === "good" ? "#226b5f" : statusTone(uploadJob.status) === "danger" ? "#c25337" : "var(--text)",
                        fontWeight: 800,
                        fontSize: ".8rem",
                      }}
                    >
                      {statusLabel(uploadJob.status)}
                    </span>
                  </div>
                  {uploadJob.error && (
                    <div
                      style={{
                        borderRadius: 14,
                        padding: 12,
                        background: "rgba(229,106,76,0.12)",
                        color: "#9b3c27",
                        lineHeight: 1.55,
                        fontWeight: 700,
                      }}
                    >
                      {uploadJob.error.message}
                    </div>
                  )}
                  {uploadJob.assistPackage && (
                    <UploadAssistPanel
                      assistPackage={uploadJob.assistPackage}
                      postUrl={activeResult?.post.url ?? null}
                      completeHint="업로드를 마친 뒤 아래의 완료 확인 버튼을 눌러 상태를 정리해 주세요."
                    />
                  )}
                  {uploadJob.status === "assist_required" && (
                    <button className="button button-primary" onClick={() => void handleAssistComplete()}>
                      업로드 완료 확인
                    </button>
                  )}
                </div>
              )}
            </section>

            <details
              style={{
                display: "grid",
                gap: 12,
                padding: 16,
                borderRadius: 8,
                border: "1px solid rgba(29,22,17,0.08)",
                background: "rgba(255,255,255,0.72)",
              }}
            >
              <summary style={{ cursor: "pointer", fontWeight: 800 }}>검토 정보 열기</summary>
              <div style={{ height: 4 }} />
              {activeResult?.rendererSummary?.hybridSourceCandidateKey ? (
                <section style={{ display: "grid", gap: 12 }}>
                  <strong>적용된 hybrid 기준선</strong>
                  <div style={{ borderRadius: 8, border: "1px solid rgba(34,107,95,0.16)", padding: 16, background: "rgba(34,107,95,0.08)", display: "grid", gap: 8 }}>
                    <div style={{ fontWeight: 800 }}>{activeResult.rendererSummary.hybridSourceCandidateKey}</div>
                    <div style={{ color: "var(--muted)", lineHeight: 1.55 }}>
                      {activeResult.rendererSummary.hybridSourceSelectionMode ?? "approved inventory reference"}
                      {" · "}
                      {activeResult.rendererSummary.videoSourceMode ?? "hybrid_generated_clip"}
                      {" · "}
                      {activeResult.rendererSummary.motionMode ?? "hybrid_overlay_packaging"}
                    </div>
                  </div>
                </section>
              ) : null}

              <CopyPolicySummary
                purpose={wizard.purpose}
                templateId={activeResultTemplateId}
                detailLocation={activeDetailLocation}
                activePolicy={activeResult?.copyPolicy ?? null}
                title="결과 기준 카피 정책"
                description="현재 결과에서 상세 위치를 어떻게 숨기고 있는지 확인합니다."
              />
              <PromptBaselineSummary
                summary={activeResult?.promptBaselineSummary ?? null}
                description="현재 결과와 추천 프로필의 대응 관계를 확인합니다."
              />
              <CopyDeckSummary
                copyDeck={activeResult?.copyDeck ?? null}
                description="현재 결과 문구가 어느 슬롯에 들어갔는지 확인합니다."
              />
              <ChangeImpactSummary
                summary={activeResult?.changeImpactSummary ?? null}
                description="최근 다시 만들기에서 어떤 층이 바뀌었는지 확인합니다."
              />

              {activeResult?.scenePlan && selectedProjectId ? (
                <ScenePlanPreviewLinks
                  projectId={selectedProjectId}
                  scenePlan={activeResult.scenePlan}
                  sceneLayerSummary={activeResult.sceneLayerSummary ?? null}
                  activePolicy={activeResult.copyPolicy ?? null}
                  changeImpactSummary={activeResult.changeImpactSummary ?? null}
                  description="씬 단위 결과를 확인합니다."
                />
              ) : null}
            </details>
          </div>
        </aside>
      </div>

      <div className="mobile-action-bar">
        <div className="mobile-action-bar__meta">
          <strong>{activeProject ? statusLabel(activeProject.status) : "새 콘텐츠 만들기"}</strong>
          <span>{mobileActionCaption}</span>
        </div>
        <div className="mobile-action-bar__buttons">
          {uploadJob?.status === "assist_required" ? (
            <>
              <button className="button button-primary" onClick={() => void handleAssistComplete()}>
                업로드 완료 확인
              </button>
              <button className="button button-secondary" onClick={() => void handlePublish("assist", "instagram")} disabled={!activeResult}>
                업로드 보조 다시 열기
              </button>
            </>
          ) : activeResult ? (
            <>
              <button className="button button-primary" disabled={!activeResult} onClick={() => void handlePublish("assist", publishChannel)}>
                업로드 준비
              </button>
              <button className="button button-secondary" onClick={() => focusMobileSection("result")}>
                결과 다시 보기
              </button>
            </>
          ) : (
            <>
              <button className="button button-primary" disabled={isPending || wizard.channels.length === 0} onClick={() => void createDemoProject()}>
                생성 시작
              </button>
              <button className="button button-secondary" onClick={sampleFill}>
                샘플 사진
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
type ProjectEditorState = {
  project: GetProjectResponse;
  assets: UploadedAssetItem[];
};
