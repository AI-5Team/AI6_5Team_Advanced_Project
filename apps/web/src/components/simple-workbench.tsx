"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { ResultMediaPreview } from "@/components/result-media-preview";
import { UploadAssistPanel } from "@/components/upload-assist-panel";
import {
  completeAssist,
  createProject,
  getGenerationStatus,
  getProjectResult,
  getSocialAccounts,
  getUploadJob,
  listProjects,
  publishProject,
  startGeneration,
  uploadAssets,
} from "@/lib/api";
import type {
  BusinessType,
  Channel,
  GenerationStatusResponse,
  GenerationStep,
  ProjectResultResponse,
  ProjectSummary,
  Purpose,
  SocialAccountSummary,
  Style,
  TemplateId,
  UploadJobResponse,
} from "@/lib/contracts";
import {
  CHANNEL_LABELS,
  PURPOSE_LABELS,
  STYLE_LABELS,
  projectStatusLabel,
  socialStatusHint,
  socialStatusLabel,
  statusTone,
} from "@/lib/display";

const PURPOSE_OPTIONS: Array<{
  id: Purpose;
  title: string;
  description: string;
  templateId: TemplateId;
}> = [
  {
    id: "new_menu",
    title: "신메뉴 알리기",
    description: "새로 나온 메뉴를 짧고 또렷하게 소개합니다.",
    templateId: "T01",
  },
  {
    id: "promotion",
    title: "할인 행사 알리기",
    description: "지금 바로 오게 만드는 혜택 중심 문구를 만듭니다.",
    templateId: "T02",
  },
  {
    id: "review",
    title: "후기 강조하기",
    description: "손님 반응과 만족감을 짧게 보여줍니다.",
    templateId: "T04",
  },
  {
    id: "location_push",
    title: "방문 유도하기",
    description: "오늘 방문해야 할 이유를 빠르게 정리합니다.",
    templateId: "T03",
  },
];

const BUSINESS_OPTIONS: Array<{
  id: BusinessType;
  title: string;
  description: string;
}> = [
  {
    id: "cafe",
    title: "카페",
    description: "음료, 디저트, 분위기 중심으로 구성합니다.",
  },
  {
    id: "restaurant",
    title: "음식점",
    description: "메뉴 소개와 방문 동선을 중심으로 구성합니다.",
  },
];

const STYLE_OPTIONS: Style[] = ["default", "friendly", "b_grade_fun"];
const CHANNEL_OPTIONS: Channel[] = ["instagram", "youtube_shorts", "tiktok"];

const STATUS_LABELS: Record<GenerationStep["name"], string> = {
  preprocessing: "사진 정리",
  copy_generation: "문구 생성",
  video_rendering: "영상 제작",
  post_rendering: "게시 이미지",
  packaging: "업로드 준비",
};

type SampleAssetItem = {
  src: string;
  fileName: string;
  title: string;
  note: string;
};

type SampleResultPreview = {
  experiment: string;
  motionLabel: string;
  note: string;
  sourceName: string;
  sourceSrc: string;
  title: string;
  videoSrc: string;
};

const VM_SAMPLE_ASSETS = {
  beer: {
    src: "/sample-assets/vm/beer-source.jpg",
    fileName: "beer-source.jpg",
    title: "맥주 대표 컷",
    note: "신유철 VM 실험에 사용한 실제 입력 사진입니다.",
  },
  pizza: {
    src: "/sample-assets/vm/pizza-source.jpg",
    fileName: "pizza-source.jpg",
    title: "피자 대표 컷",
    note: "Wan2.1-VACE 실험에 사용한 피자 입력 사진입니다.",
  },
  izakaya: {
    src: "/sample-assets/vm/izakaya-source.jpg",
    fileName: "izakaya-source.jpg",
    title: "이자카야 대표 컷",
    note: "일본식 맥주·야키토리 실험에 사용한 입력 사진입니다.",
  },
} satisfies Record<string, SampleAssetItem>;

const PURPOSE_VISUALS: Record<
  Purpose,
  Array<{ src: string; title: string; note: string }>
> = {
  new_menu: [
    {
      src: VM_SAMPLE_ASSETS.pizza.src,
      title: "대표 장면",
      note: "피자 신메뉴 실험 입력 컷입니다.",
    },
    {
      src: VM_SAMPLE_ASSETS.izakaya.src,
      title: "보조 장면",
      note: "다른 메뉴 컷을 붙여 구성 폭을 넓힙니다.",
    },
    {
      src: VM_SAMPLE_ASSETS.beer.src,
      title: "마무리 장면",
      note: "음료 컷까지 이어서 마무리할 수 있습니다.",
    },
  ],
  promotion: [
    {
      src: VM_SAMPLE_ASSETS.beer.src,
      title: "혜택 강조",
      note: "행사 문구와 함께 쓰기 좋은 맥주 컷입니다.",
    },
    {
      src: VM_SAMPLE_ASSETS.pizza.src,
      title: "대표 컷",
      note: "대표 메뉴 가격과 혜택을 붙이기 좋습니다.",
    },
    {
      src: VM_SAMPLE_ASSETS.izakaya.src,
      title: "마감 컷",
      note: "오늘만 혜택 문구를 다시 한 번 붙입니다.",
    },
  ],
  review: [
    {
      src: VM_SAMPLE_ASSETS.izakaya.src,
      title: "후기 장면",
      note: "반응이 좋은 메뉴를 먼저 보여줍니다.",
    },
    {
      src: VM_SAMPLE_ASSETS.pizza.src,
      title: "보조 장면",
      note: "만족감을 주는 대표 메뉴 컷을 이어 붙입니다.",
    },
    {
      src: VM_SAMPLE_ASSETS.beer.src,
      title: "마무리 장면",
      note: "다시 오고 싶게 만드는 분위기 컷으로 마무리합니다.",
    },
  ],
  location_push: [
    {
      src: VM_SAMPLE_ASSETS.pizza.src,
      title: "대표 장면",
      note: "대표 메뉴를 먼저 보여주고 방문 이유를 만듭니다.",
    },
    {
      src: VM_SAMPLE_ASSETS.beer.src,
      title: "분위기 장면",
      note: "가게 분위기와 음료 컷을 함께 덧붙입니다.",
    },
    {
      src: VM_SAMPLE_ASSETS.izakaya.src,
      title: "방문 유도",
      note: "지역과 위치 문구를 붙이기 좋은 컷입니다.",
    },
  ],
};

const PURPOSE_SAMPLE_FILES: Record<Purpose, SampleAssetItem[]> = {
  new_menu: [VM_SAMPLE_ASSETS.pizza, VM_SAMPLE_ASSETS.izakaya],
  promotion: [VM_SAMPLE_ASSETS.beer, VM_SAMPLE_ASSETS.pizza],
  review: [VM_SAMPLE_ASSETS.izakaya, VM_SAMPLE_ASSETS.pizza],
  location_push: [VM_SAMPLE_ASSETS.pizza, VM_SAMPLE_ASSETS.beer],
};

const PURPOSE_SAMPLE_RESULTS: Record<Purpose, SampleResultPreview> = {
  new_menu: {
    experiment: "wan_vace_pizza_lift_to_camera",
    motionLabel: "lift_to_camera",
    note: "피자 한 조각이 카메라 쪽으로 올라오도록 만든 실제 VM 생성 결과입니다.",
    sourceName: "pizza-source.jpg",
    sourceSrc: VM_SAMPLE_ASSETS.pizza.src,
    title: "신메뉴 강조 샘플 영상",
    videoSrc: "/sample-results/vm/pizza-lift-to-camera.mp4",
  },
  promotion: {
    experiment: "wan_vace_beer_dolly_in",
    motionLabel: "dolly_in",
    note: "맥주 병 쪽으로 천천히 들어가는 광고형 움직임을 만든 실제 결과입니다.",
    sourceName: "beer-source.jpg",
    sourceSrc: VM_SAMPLE_ASSETS.beer.src,
    title: "행사 홍보 샘플 영상",
    videoSrc: "/sample-results/vm/beer-dolly-in.mp4",
  },
  review: {
    experiment: "wan_vace_japan_consume_product",
    motionLabel: "consume_product",
    note: "손이 야키토리 꼬치를 집는 장면으로 후기형 소개에 맞춘 생성 결과입니다.",
    sourceName: "izakaya-source.jpg",
    sourceSrc: VM_SAMPLE_ASSETS.izakaya.src,
    title: "후기 강조 샘플 영상",
    videoSrc: "/sample-results/vm/izakaya-consume-product.mp4",
  },
  location_push: {
    experiment: "wan_vace_pizza_dolly_in",
    motionLabel: "dolly_in",
    note: "대표 메뉴를 가까이 끌어오듯 보여주는 결과라 방문 유도 화면에 맞습니다.",
    sourceName: "pizza-source.jpg",
    sourceSrc: VM_SAMPLE_ASSETS.pizza.src,
    title: "방문 유도 샘플 영상",
    videoSrc: "/sample-results/vm/pizza-dolly-in.mp4",
  },
};

function guessMimeType(src: string): string {
  if (src.endsWith(".png")) {
    return "image/png";
  }
  if (src.endsWith(".webp")) {
    return "image/webp";
  }
  if (src.endsWith(".svg")) {
    return "image/svg+xml";
  }
  return "image/jpeg";
}

async function createFileFromAsset(asset: SampleAssetItem): Promise<File> {
  const response = await fetch(asset.src);
  if (!response.ok) {
    throw new Error(`샘플 파일을 불러오지 못했습니다: ${asset.fileName}`);
  }

  const blob = await response.blob();
  return new File([blob], asset.fileName, {
    type: blob.type || guessMimeType(asset.src),
    lastModified: Date.now(),
  });
}

async function getSampleFiles(purpose: Purpose): Promise<File[]> {
  return Promise.all(PURPOSE_SAMPLE_FILES[purpose].map((asset) => createFileFromAsset(asset)));
}

function normalizeHashtags(input: string): string[] {
  return input
    .split(/[\s,]+/)
    .map((tag) => tag.trim())
    .filter(Boolean)
    .map((tag) => (tag.startsWith("#") ? tag : `#${tag}`));
}

function getStatusMessage(status: GenerationStatusResponse | null): string {
  if (!status || status.steps.length === 0) {
    return "준비가 끝나면 바로 만들 수 있습니다.";
  }

  const active =
    status.steps.find((step) => step.status === "processing") ??
    status.steps.find((step) => step.status === "pending") ??
    status.steps[status.steps.length - 1];

  return STATUS_LABELS[active.name] ?? "결과를 만들고 있습니다.";
}

export function SimpleWorkbench() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const [businessType, setBusinessType] = useState<BusinessType>("cafe");
  const [purpose, setPurpose] = useState<Purpose>("new_menu");
  const [style, setStyle] = useState<Style>("friendly");
  const [selectedChannels, setSelectedChannels] = useState<Channel[]>(["instagram"]);
  const [regionName, setRegionName] = useState("성수동");
  const [detailLocation, setDetailLocation] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [recentProjects, setRecentProjects] = useState<ProjectSummary[]>([]);
  const [socialAccounts, setSocialAccounts] = useState<SocialAccountSummary[]>([]);

  const [isGenerating, setIsGenerating] = useState(false);
  const [isPreparingUpload, setIsPreparingUpload] = useState(false);
  const [isCompletingUpload, setIsCompletingUpload] = useState(false);

  const [projectId, setProjectId] = useState<string | null>(null);
  const [generationStatus, setGenerationStatus] =
    useState<GenerationStatusResponse | null>(null);
  const [result, setResult] = useState<ProjectResultResponse | null>(null);
  const [uploadJob, setUploadJob] = useState<UploadJobResponse | null>(null);
  const [filePreviewUrls, setFilePreviewUrls] = useState<string[]>([]);
  const [feedback, setFeedback] = useState(
    "사진을 넣고 업종, 목적, 스타일을 고르면 바로 결과를 준비합니다.",
  );

  const [caption, setCaption] = useState("");
  const [hashtagsDraft, setHashtagsDraft] = useState("");
  const [thumbnailText, setThumbnailText] = useState("");

  const refreshDashboard = async () => {
    const [projectsResult, socialsResult] = await Promise.allSettled([
      listProjects(),
      getSocialAccounts(),
    ]);

    if (projectsResult.status === "fulfilled") {
      setRecentProjects(projectsResult.value.items.slice(0, 4));
    } else {
      setRecentProjects([]);
    }

    if (socialsResult.status === "fulfilled") {
      setSocialAccounts(socialsResult.value.items);
    } else {
      setSocialAccounts([]);
    }
  };

  useEffect(() => {
    void refreshDashboard();
  }, []);

  useEffect(() => {
    if (files.length === 0) {
      setFilePreviewUrls([]);
      return;
    }

    const nextUrls = files.map((file) => URL.createObjectURL(file));
    setFilePreviewUrls(nextUrls);

    return () => {
      nextUrls.forEach((url) => URL.revokeObjectURL(url));
    };
  }, [files]);

  useEffect(() => {
    if (!projectId) {
      return;
    }

    let stopped = false;

    const poll = async () => {
      try {
        const status = await getGenerationStatus(projectId);
        if (stopped) {
          return;
        }

        setGenerationStatus(status);

        if (status.projectStatus === "generated") {
          const projectResult = await getProjectResult(projectId);
          if (stopped) {
            return;
          }

          setResult(projectResult);
          setCaption(
            projectResult.copySet.captions[0] ??
              projectResult.copySet.hookText ??
              "",
          );
          setHashtagsDraft(projectResult.copySet.hashtags.join(" "));
          setThumbnailText(projectResult.copySet.hookText ?? "오늘의 추천");
          setFeedback("결과가 준비되었습니다. 게시 전 문구와 채널 상태만 확인해 주세요.");
          setIsGenerating(false);
          void refreshDashboard();
        }

        if (status.projectStatus === "failed") {
          setFeedback("결과를 만드는 중 문제가 생겼습니다. 사진을 바꾸거나 다시 시도해 주세요.");
          setIsGenerating(false);
        }
      } catch {
        if (!stopped) {
          setIsGenerating(false);
          setFeedback("상태를 확인하는 중 문제가 생겼습니다. 잠시 후 다시 시도해 주세요.");
        }
      }
    };

    void poll();
    const timer = window.setInterval(() => {
      void poll();
    }, 2000);

    return () => {
      stopped = true;
      window.clearInterval(timer);
    };
  }, [projectId]);

  useEffect(() => {
    if (!uploadJob?.uploadJobId) {
      return;
    }

    let stopped = false;

    const poll = async () => {
      try {
        const nextJob = await getUploadJob(uploadJob.uploadJobId);
        if (!stopped) {
          setUploadJob(nextJob);
        }
      } catch {
        if (!stopped) {
          setFeedback("업로드 준비 상태를 불러오지 못했습니다.");
        }
      }
    };

    void poll();
    const timer = window.setInterval(() => {
      void poll();
    }, 3000);

    return () => {
      stopped = true;
      window.clearInterval(timer);
    };
  }, [uploadJob?.uploadJobId]);

  const selectedPurpose = useMemo(
    () => PURPOSE_OPTIONS.find((option) => option.id === purpose) ?? PURPOSE_OPTIONS[0],
    [purpose],
  );
  const selectedPurposeMeta = PURPOSE_LABELS[purpose];
  const selectedStyleMeta = STYLE_LABELS[style];
  const sampleResult = PURPOSE_SAMPLE_RESULTS[purpose];
  const hashtagList = useMemo(() => normalizeHashtags(hashtagsDraft), [hashtagsDraft]);
  const statusMessage = getStatusMessage(generationStatus);
  const visualGallery = useMemo(() => {
    const uploadedItems = filePreviewUrls.map((src, index) => ({
      src,
      title: index === 0 ? "선택한 대표 사진" : `추가 사진 ${index}`,
      note: files[index]?.name ?? "업로드한 사진",
    }));
    const fallbackItems = PURPOSE_VISUALS[purpose];
    return [...uploadedItems, ...fallbackItems].slice(0, 3);
  }, [filePreviewUrls, files, purpose]);
  const primaryVisual = visualGallery[0];
  const socialByChannel = useMemo(
    () => new Map(socialAccounts.map((account) => [account.channel, account])),
    [socialAccounts],
  );
  const connectedCount = socialAccounts.filter((account) => account.status === "connected").length;
  const reconnectCount = socialAccounts.filter(
    (account) => account.status === "expired" || account.status === "permission_error",
  ).length;
  const publishChannel =
    selectedChannels.includes("instagram") ? "instagram" : selectedChannels[0] ?? "instagram";
  const publishChannelLabel = CHANNEL_LABELS[publishChannel].title;
  const publishAccount = socialByChannel.get(publishChannel);
  const recentItems = recentProjects.slice(0, 4);
  const fileSummary =
    files.length > 0
      ? `${files.length}장 업로드됨`
      : "신유철 VM 실험 샘플로도 바로 흐름을 볼 수 있습니다.";
  const primaryObjectPosition = "center center";
  const primaryObjectFit = "cover";
  const showProgress = isGenerating && (generationStatus?.steps.length ?? 0) > 0;

  const toggleChannel = (channel: Channel) => {
    setSelectedChannels((current) => {
      if (current.includes(channel)) {
        return current.length === 1 ? current : current.filter((item) => item !== channel);
      }
      return [...current, channel];
    });
  };

  const resetFlow = () => {
    setProjectId(null);
    setGenerationStatus(null);
    setResult(null);
    setUploadJob(null);
    setCaption("");
    setHashtagsDraft("");
    setThumbnailText("");
    setFiles([]);
    setIsGenerating(false);
    setIsPreparingUpload(false);
    setIsCompletingUpload(false);
    setFeedback("새 사진으로 다시 만들 준비가 되었습니다.");
  };

  const handleFileSelection = (nextFiles: FileList | null) => {
    if (!nextFiles || nextFiles.length === 0) {
      return;
    }

    setFiles(Array.from(nextFiles));
    setFeedback(`${nextFiles.length}장의 사진을 불러왔습니다.`);
  };

  const handleSampleClick = async () => {
    setFeedback("신유철 VM 실험 샘플 사진을 불러오고 있습니다.");

    try {
      const sampleFiles = await getSampleFiles(purpose);
      setFiles(sampleFiles);
      setFeedback("신유철 VM 실험에 사용한 샘플 사진을 불러왔습니다.");
    } catch (error) {
      setFeedback(
        error instanceof Error
          ? error.message
          : "VM 샘플 사진을 불러오지 못했습니다. 다시 시도해 주세요.",
      );
    }
  };

  const handleGenerate = async () => {
    if (files.length === 0) {
      setFeedback("먼저 사진을 넣어 주세요.");
      return;
    }

    setIsGenerating(true);
    setResult(null);
    setUploadJob(null);
    setGenerationStatus(null);
    setFeedback("사진과 선택한 설정을 바탕으로 결과를 만들고 있습니다.");

    try {
      const created = await createProject({
        businessType,
        channels: selectedChannels,
        detailLocation: detailLocation.trim() || null,
        purpose,
        regionName: regionName.trim() || "우리 동네",
        style,
      });

      setProjectId(created.projectId);

      const uploaded = await uploadAssets(created.projectId, files);
      await startGeneration(created.projectId, {
        assetIds: uploaded.assets.map((asset) => asset.assetId),
        quickOptions: {
          emphasizeRegion: false,
          highlightPrice: purpose === "promotion",
          shorterCopy: true,
        },
        templateId: selectedPurpose.templateId,
      });
    } catch (error) {
      setIsGenerating(false);
      setFeedback(
        error instanceof Error
          ? error.message
          : "결과를 만드는 중 문제가 생겼습니다. 다시 시도해 주세요.",
      );
    }
  };

  const handlePrepareUpload = async () => {
    if (!projectId || !result) {
      setFeedback("먼저 결과를 만든 뒤 업로드 준비를 진행해 주세요.");
      return;
    }

    setIsPreparingUpload(true);
    setFeedback(`${publishChannelLabel} 업로드용 문구와 파일을 정리하고 있습니다.`);

    try {
      const response = await publishProject(projectId, {
        captionOverride: caption.trim() || null,
        channel: publishChannel,
        hashtags: hashtagList,
        publishMode: "assist",
        thumbnailText: thumbnailText.trim() || null,
        variantId: result.variantId,
      });

      setUploadJob({
        assistPackage: response.assistPackage,
        channel: publishChannel,
        error: null,
        projectId,
        status: response.status,
        uploadJobId: response.uploadJobId,
      });
      setFeedback("업로드 전에 확인할 준비물이 정리되었습니다.");
      void refreshDashboard();
    } catch (error) {
      setFeedback(
        error instanceof Error
          ? error.message
          : "업로드 준비 중 문제가 생겼습니다. 다시 시도해 주세요.",
      );
    } finally {
      setIsPreparingUpload(false);
    }
  };

  const handleCompleteAssist = async () => {
    if (!uploadJob?.uploadJobId) {
      return;
    }

    setIsCompletingUpload(true);

    try {
      const completed = await completeAssist(uploadJob.uploadJobId);
      setUploadJob((previous) =>
        previous
          ? {
              ...previous,
              status: completed.status,
            }
          : previous,
      );
      setFeedback("업로드 확인이 끝났습니다. 다음 작업도 같은 방식으로 이어서 만들 수 있습니다.");
      void refreshDashboard();
    } catch (error) {
      setFeedback(
        error instanceof Error
          ? error.message
          : "업로드 완료 처리 중 문제가 생겼습니다.",
      );
    } finally {
      setIsCompletingUpload(false);
    }
  };

  return (
    <main className="app-shell avs-home">
      <section className="avs-home__hero">
        <div className="avs-home__heading">
          <span className="avs-home__eyebrow">AVS</span>
          <h1>오늘 뭐 홍보하실래요?</h1>
          <p>{feedback}</p>
        </div>

        <article className="avs-hero-card">
          <div className="avs-hero-card__copy">
            <span>{selectedPurpose.title}</span>
            <strong>{selectedStyleMeta.title} 톤으로 바로 준비합니다.</strong>
            <p>{selectedPurposeMeta.hint}</p>
          </div>

          <div className="avs-hero-card__visual">
            <img
              src={primaryVisual.src}
              alt={primaryVisual.note}
              style={{ objectFit: primaryObjectFit, objectPosition: primaryObjectPosition }}
            />
            <div className="avs-hero-card__shade" />
            <div className="avs-hero-card__caption">
              <small>{publishChannelLabel}</small>
              <strong>{selectedChannels.map((channel) => CHANNEL_LABELS[channel].title).join(" · ")}</strong>
            </div>
          </div>

          <div className="avs-hero-card__stats">
            <div className="avs-mini-stat">
              <span>선택 채널</span>
              <strong>{selectedChannels.length}개</strong>
            </div>
            <div className="avs-mini-stat">
              <span>연결됨</span>
              <strong>{connectedCount}개</strong>
            </div>
            <div className="avs-mini-stat">
              <span>재연결</span>
              <strong>{reconnectCount}개</strong>
            </div>
          </div>
        </article>
      </section>

      <section className="avs-block">
        <div className="avs-block__head">
          <span className="avs-step-chip">1/6</span>
          <h2>홍보에 쓸 사진</h2>
          <p>{fileSummary}</p>
        </div>

        <div className="avs-button-row">
          <button
            type="button"
            className="button button-primary"
            onClick={() => fileInputRef.current?.click()}
          >
            사진 선택
          </button>
          <button
            type="button"
            className="button button-secondary"
            onClick={() => void handleSampleClick()}
          >
            실험 샘플 사용
          </button>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/png,image/jpeg,image/webp,image/svg+xml"
          multiple
          hidden
          onChange={(event) => handleFileSelection(event.target.files)}
        />

        <div className="avs-media-strip">
          {visualGallery.map((item, index) => (
            <article key={`${item.src}-${index}`} className="avs-media-card">
              <img src={item.src} alt={item.note} />
              <div className="avs-media-card__meta">
                <strong>{item.title}</strong>
                <span>{item.note}</span>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="avs-block">
        <div className="avs-block__head">
          <span className="avs-step-chip">2/6</span>
          <h2>가게 기본 정보</h2>
          <p>업종과 위치만 적어도 문구와 결과 구성이 바로 정리됩니다.</p>
        </div>

        <div className="avs-choice-grid">
          {BUSINESS_OPTIONS.map((option) => (
            <button
              key={option.id}
              type="button"
              className={option.id === businessType ? "avs-choice avs-choice--active" : "avs-choice"}
              onClick={() => setBusinessType(option.id)}
            >
              <strong>{option.title}</strong>
              <span>{option.description}</span>
            </button>
          ))}
        </div>

        <div className="avs-field-stack">
          <label className="avs-field">
            <span>지역 이름</span>
            <input
              value={regionName}
              onChange={(event) => setRegionName(event.target.value)}
              placeholder="예: 성수동"
            />
          </label>
          <label className="avs-field">
            <span>위치 설명</span>
            <input
              value={detailLocation}
              onChange={(event) => setDetailLocation(event.target.value)}
              placeholder="예: 2호선 4번 출구 앞"
            />
          </label>
        </div>
      </section>

      <section className="avs-block">
        <div className="avs-block__head">
          <span className="avs-step-chip">3/6</span>
          <h2>무엇을 알릴지 고르기</h2>
          <p>{selectedPurposeMeta.hint}</p>
        </div>

        <div className="avs-choice-stack">
          {PURPOSE_OPTIONS.map((option) => (
            <button
              key={option.id}
              type="button"
              className={option.id === purpose ? "avs-choice avs-choice--active" : "avs-choice"}
              onClick={() => setPurpose(option.id)}
            >
              <strong>{option.title}</strong>
              <span>{option.description}</span>
            </button>
          ))}
        </div>
      </section>

      <section className="avs-block">
        <div className="avs-block__head">
          <span className="avs-step-chip">4/6</span>
          <h2>문구 톤 맞추기</h2>
          <p>{selectedStyleMeta.hint}</p>
        </div>

        <div className="avs-pill-grid">
          {STYLE_OPTIONS.map((item) => (
            <button
              key={item}
              type="button"
              className={item === style ? "avs-pill avs-pill--active" : "avs-pill"}
              onClick={() => setStyle(item)}
            >
              <strong>{STYLE_LABELS[item].title}</strong>
              <span>{STYLE_LABELS[item].hint}</span>
            </button>
          ))}
        </div>
      </section>

      <section className="avs-block">
        <div className="avs-block__head">
          <span className="avs-step-chip">5/6</span>
          <h2>채널 상태 확인</h2>
          <p>연결 여부를 같이 보고, 준비가 덜 되어도 업로드 보조로 이어갑니다.</p>
        </div>

        <div className="avs-channel-list">
          {CHANNEL_OPTIONS.map((channel) => {
            const active = selectedChannels.includes(channel);
            const account = socialByChannel.get(channel);
            const status = account?.status ?? "not_connected";

            return (
              <button
                key={channel}
                type="button"
                className={active ? "avs-channel-row avs-channel-row--active" : "avs-channel-row"}
                onClick={() => toggleChannel(channel)}
                aria-pressed={active}
              >
                <div className="avs-channel-row__copy">
                  <div className="avs-channel-row__title">
                    <strong>{CHANNEL_LABELS[channel].title}</strong>
                    <span className={`tone-badge tone-badge--${statusTone(status)}`}>
                      {socialStatusLabel(status)}
                    </span>
                  </div>
                  <p>{socialStatusHint(channel, status)}</p>
                </div>
                <span className="avs-channel-row__toggle">{active ? "선택됨" : "선택"}</span>
              </button>
            );
          })}
        </div>
      </section>

      <section className="avs-block avs-block--accent">
        <div className="avs-block__head">
          <span className="avs-step-chip">6/6</span>
          <h2>{isGenerating ? statusMessage : "지금 바로 만들기"}</h2>
          <p>{isGenerating ? "선택한 흐름대로 결과를 만들고 있습니다." : "입력이 끝나면 바로 결과와 업로드 준비물을 만듭니다."}</p>
        </div>

        {showProgress ? (
          <div className="avs-progress-list">
            {generationStatus?.steps.map((step) => (
              <div key={step.name} className="avs-progress-item">
                <span>{STATUS_LABELS[step.name]}</span>
                <strong>
                  {step.status === "completed"
                    ? "완료"
                    : step.status === "processing"
                      ? "진행 중"
                      : step.status === "failed"
                        ? "실패"
                        : "대기"}
                </strong>
              </div>
            ))}
          </div>
        ) : (
          <div className="avs-inline-note">
            <strong>{selectedPurpose.title}</strong>
            <span>{selectedStyleMeta.title} 톤으로 바로 이어집니다.</span>
          </div>
        )}

        <div className="avs-button-stack">
          <button
            type="button"
            className="button button-primary"
            onClick={() => void handleGenerate()}
            disabled={isGenerating}
          >
            {isGenerating ? "만드는 중입니다..." : "콘텐츠 만들기"}
          </button>
          <button type="button" className="button button-secondary" onClick={resetFlow}>
            다시 시작
          </button>
        </div>
      </section>

      <section className="avs-surface">
        <div className="avs-surface__head">
          <div>
            <span className="avs-step-chip">결과</span>
            <h2>미리보기</h2>
            <p>생성 결과와 대표 이미지를 한 자리에서 확인합니다.</p>
          </div>
          {result ? <span className="avs-inline-badge">준비 완료</span> : null}
        </div>

        {result ? (
          <ResultMediaPreview result={result} />
        ) : (
          <div className="avs-result-sample">
            <div className="avs-result-sample__frame">
              <video
                src={sampleResult.videoSrc}
                poster={sampleResult.sourceSrc}
                controls
                muted
                loop
                playsInline
                preload="metadata"
              />
            </div>

            <div className="avs-result-sample__body">
              <div className="avs-result-sample__copy">
                <span>신유철 VM 실험 결과</span>
                <strong>{sampleResult.title}</strong>
                <p>{sampleResult.note}</p>
              </div>

              <div className="avs-result-sample__source">
                <img src={sampleResult.sourceSrc} alt={`${sampleResult.title} 입력 사진`} />
                <div>
                  <small>입력 사진</small>
                  <strong>{sampleResult.sourceName}</strong>
                  <span>{sampleResult.experiment}</span>
                </div>
              </div>

              <div className="avs-result-sample__meta">
                <span>motion · {sampleResult.motionLabel}</span>
                <a
                  href={sampleResult.videoSrc}
                  target="_blank"
                  rel="noreferrer"
                  className="button button-ghost"
                >
                  영상 원본 열기
                </a>
              </div>
            </div>
          </div>
        )}
      </section>

      <section className="avs-surface">
        <div className="avs-surface__head">
          <div>
            <span className="avs-step-chip">업로드</span>
            <h2>{publishChannelLabel} 준비</h2>
            <p>캡션, 해시태그, 썸네일 문구를 지금 선택한 채널 기준으로 정리합니다.</p>
          </div>
          <span className="avs-inline-badge">{publishChannelLabel}</span>
        </div>

        <div className="avs-field-stack">
          <label className="avs-field">
            <span>게시글 문구</span>
            <textarea
              value={caption}
              onChange={(event) => setCaption(event.target.value)}
              rows={5}
              placeholder="가게 소개 문구가 여기에 들어옵니다."
            />
          </label>

          <label className="avs-field">
            <span>해시태그</span>
            <textarea
              value={hashtagsDraft}
              onChange={(event) => setHashtagsDraft(event.target.value)}
              rows={3}
              placeholder="#성수동 #신메뉴"
            />
          </label>

          <label className="avs-field">
            <span>썸네일 문구</span>
            <input
              value={thumbnailText}
              onChange={(event) => setThumbnailText(event.target.value)}
              placeholder="예: 오늘의 추천"
            />
          </label>
        </div>

        <div className="avs-inline-note">
          <strong>{publishChannelLabel} 현재 상태</strong>
          <span>
            {publishAccount
              ? socialStatusHint(publishChannel, publishAccount.status)
              : "채널 정보를 아직 불러오지 못했지만 업로드 보조 방식은 계속 사용할 수 있습니다."}
          </span>
        </div>

        <div className="avs-button-stack">
          <button
            type="button"
            className="button button-primary"
            onClick={() => void handlePrepareUpload()}
            disabled={!result || isPreparingUpload}
          >
            {isPreparingUpload ? "정리 중입니다..." : `${publishChannelLabel} 업로드 준비하기`}
          </button>

          {uploadJob ? (
            <>
              {uploadJob.assistPackage ? (
                <UploadAssistPanel assistPackage={uploadJob.assistPackage} postUrl={result?.post.url ?? null} />
              ) : null}
              <button
                type="button"
                className="button button-secondary"
                onClick={() => void handleCompleteAssist()}
                disabled={isCompletingUpload || uploadJob.status === "assisted_completed"}
              >
                {uploadJob.status === "assisted_completed"
                  ? "업로드 확인 완료"
                  : isCompletingUpload
                    ? "완료 처리 중입니다..."
                    : "업로드 완료로 표시"}
              </button>
            </>
          ) : (
            <div className="avs-inline-note">
              <strong>준비물 안내</strong>
              <span>결과를 만든 뒤 누르면 캡션, 해시태그, 파일을 바로 정리해 드립니다.</span>
            </div>
          )}
        </div>
      </section>

      <section className="avs-surface">
        <div className="avs-surface__head">
          <div>
            <span className="avs-step-chip">이력</span>
            <h2>최근 작업</h2>
            <p>최근 생성 이력을 다시 열어 이어서 수정할 수 있습니다.</p>
          </div>
          <a href="/history" className="button button-secondary avs-link-button">
            전체 보기
          </a>
        </div>

        {recentItems.length > 0 ? (
          <div className="avs-history-list">
            {recentItems.map((project) => (
              <article key={project.projectId} className="avs-history-row">
                <div className="avs-history-row__top">
                  <strong>{PURPOSE_LABELS[project.purpose].title}</strong>
                  <span className={`tone-badge tone-badge--${statusTone(project.status)}`}>
                    {projectStatusLabel(project.status)}
                  </span>
                </div>
                <div className="avs-history-row__meta">
                  <span>{STYLE_LABELS[project.style].title}</span>
                  <span>{project.projectId.slice(0, 8)}</span>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="avs-inline-note">
            <strong>아직 작업 이력이 많지 않습니다.</strong>
            <span>한 번 생성하면 최근 작업 영역에서 바로 다시 이어갈 수 있습니다.</span>
          </div>
        )}
      </section>
    </main>
  );
}
