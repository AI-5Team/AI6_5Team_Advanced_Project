"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { ResultMediaPreview } from "@/components/result-media-preview";
import { UploadAssistPanel } from "@/components/upload-assist-panel";
import {
  completeAssist,
  createProject,
  getGenerationStatus,
  getProjectResult,
  getUploadJob,
  listProjects,
  publishProject,
  startGeneration,
  uploadAssets,
} from "@/lib/api";
import type {
  BusinessType,
  GenerationStatusResponse,
  GenerationStep,
  ProjectResultResponse,
  ProjectSummary,
  Purpose,
  TemplateId,
  UploadJobResponse,
} from "@/lib/contracts";

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

const STATUS_LABELS: Record<GenerationStep["name"], string> = {
  preprocessing: "사진을 정리하고 있습니다",
  copy_generation: "문구와 설명을 만들고 있습니다",
  video_rendering: "짧은 영상을 만들고 있습니다",
  post_rendering: "게시용 이미지를 만들고 있습니다",
  packaging: "올릴 수 있게 정리하고 있습니다",
};

const PURPOSE_VISUALS: Record<
  Purpose,
  Array<{ src: string; title: string; note: string }>
> = {
  new_menu: [
    {
      src: "/sample-assets/eel.jpg",
      title: "대표 장면",
      note: "대표 메뉴를 크게 보여줍니다.",
    },
    {
      src: "/sample-assets/takoyaki.jpg",
      title: "보조 장면",
      note: "메뉴 디테일을 붙입니다.",
    },
    {
      src: "/sample-assets/beer.jpg",
      title: "마무리 장면",
      note: "오늘 올릴 문구로 마무리합니다.",
    },
  ],
  promotion: [
    {
      src: "/sample-assets/spicy.jpg",
      title: "혜택 강조",
      note: "행사 문구를 먼저 보여줍니다.",
    },
    {
      src: "/sample-assets/beer.jpg",
      title: "대표 컷",
      note: "가격이나 혜택을 붙이기 좋습니다.",
    },
    {
      src: "/sample-assets/takoyaki.jpg",
      title: "마감 컷",
      note: "오늘만 혜택을 다시 한 번 강조합니다.",
    },
  ],
  review: [
    {
      src: "/sample-assets/ramen.jpg",
      title: "후기 장면",
      note: "가장 반응이 좋은 메뉴부터 보여줍니다.",
    },
    {
      src: "/sample-assets/katsu.jpg",
      title: "보조 장면",
      note: "만족감을 주는 대표 컷을 이어 붙입니다.",
    },
    {
      src: "/sample-assets/eel.jpg",
      title: "마무리 장면",
      note: "다시 오고 싶게 만드는 한 줄로 끝냅니다.",
    },
  ],
  location_push: [
    {
      src: "/sample-assets/katsu.jpg",
      title: "대표 장면",
      note: "가게에 와야 할 이유를 먼저 보여줍니다.",
    },
    {
      src: "/sample-assets/beer.jpg",
      title: "분위기 장면",
      note: "가게 분위기나 대표 메뉴를 덧붙입니다.",
    },
    {
      src: "/sample-assets/ramen.jpg",
      title: "방문 유도",
      note: "지역과 위치를 함께 정리합니다.",
    },
  ],
};

function makeSvgFile(title: string, accent: string, secondary: string, subline: string): File {
  const gradientId = `grad-${title.replace(/\s+/g, "-").toLowerCase()}`;
  const markup = `
    <svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1440">
      <defs>
        <linearGradient id="${gradientId}" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="${accent}" />
          <stop offset="100%" stop-color="${secondary}" />
        </linearGradient>
      </defs>
      <rect width="1080" height="1440" fill="url(#${gradientId})" />
      <rect x="64" y="64" width="952" height="1312" rx="48" fill="white" opacity="0.96" />
      <rect x="120" y="170" width="188" height="10" rx="5" fill="${accent}" opacity="0.9" />
      <line x1="120" y1="474" x2="960" y2="474" stroke="#dbe3ee" stroke-width="4" />
      <line x1="120" y1="944" x2="960" y2="944" stroke="#dbe3ee" stroke-width="4" />
      <rect x="120" y="1078" width="840" height="128" rx="30" fill="${accent}" opacity="0.14" />
      <text x="120" y="260" font-family="Pretendard, Arial, sans-serif" font-size="94" font-weight="700" fill="#111827">${title}</text>
      <text x="120" y="390" font-family="Pretendard, Arial, sans-serif" font-size="42" fill="#4b5563">${subline}</text>
      <text x="120" y="1148" font-family="Pretendard, Arial, sans-serif" font-size="52" fill="#111827">오늘 바로 올릴 수 있는 샘플 이미지</text>
    </svg>
  `.trim();

  return new File([markup], `${title}.svg`, {
    type: "image/svg+xml",
    lastModified: Date.now(),
  });
}

function getSampleFiles(purpose: Purpose): File[] {
  if (purpose === "promotion") {
    return [
      makeSvgFile("오늘의 할인", "#ff8f63", "#ffd16b", "행사 안내용 샘플 이미지"),
      makeSvgFile("대표 메뉴", "#ff9b72", "#ffc676", "가격과 혜택을 함께 보여주는 샘플"),
    ];
  }

  if (purpose === "review") {
    return [
      makeSvgFile("손님 후기", "#22c7df", "#29d8b3", "후기 강조용 샘플 이미지"),
      makeSvgFile("재방문 추천", "#30b8f5", "#27d0cb", "만족감을 보여주는 샘플"),
    ];
  }

  if (purpose === "location_push") {
    return [
      makeSvgFile("이번 주 추천", "#2bc4f2", "#20d3c0", "방문 유도용 샘플 이미지"),
      makeSvgFile("지금 오세요", "#3cb4ff", "#ff9b6e", "행사 참여를 돕는 샘플"),
    ];
  }

  return [
    makeSvgFile("신메뉴 출시", "#1ec6df", "#23d4ba", "신메뉴 소개용 샘플 이미지"),
    makeSvgFile("대표 컷", "#23b8f2", "#20d1cf", "메뉴를 또렷하게 보여주는 샘플"),
  ];
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
  const [regionName, setRegionName] = useState("성수동");
  const [detailLocation, setDetailLocation] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [recentProjects, setRecentProjects] = useState<ProjectSummary[]>([]);

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
    "사진을 넣고 목적을 고르면 바로 결과를 만들어 드립니다.",
  );

  const [caption, setCaption] = useState("");
  const [hashtagsDraft, setHashtagsDraft] = useState("");
  const [thumbnailText, setThumbnailText] = useState("");

  useEffect(() => {
    void listProjects()
      .then((response) => setRecentProjects(response.items.slice(0, 3)))
      .catch(() => setRecentProjects([]));
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
          setFeedback("결과가 준비되었습니다. 그대로 올리기 전에 한 번만 읽어 보세요.");
          setIsGenerating(false);
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

  const resetFlow = () => {
    setProjectId(null);
    setGenerationStatus(null);
    setResult(null);
    setUploadJob(null);
    setCaption("");
    setHashtagsDraft("");
    setThumbnailText("");
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

  const handleSampleClick = () => {
    const sampleFiles = getSampleFiles(purpose);
    setFiles(sampleFiles);
    setFeedback("샘플 사진을 불러왔습니다. 실제 사진으로 바꾸셔도 됩니다.");
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
    setFeedback("사진과 문구를 바탕으로 결과를 만들고 있습니다.");

    try {
      const created = await createProject({
        businessType,
        channels: ["instagram"],
        detailLocation: detailLocation.trim() || null,
        purpose,
        regionName: regionName.trim() || "우리 동네",
        style: "friendly",
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
    setFeedback("업로드용 캡션과 파일을 정리하고 있습니다.");

    try {
      const response = await publishProject(projectId, {
        captionOverride: caption.trim() || null,
        channel: "instagram",
        hashtags: hashtagList,
        publishMode: "assist",
        thumbnailText: thumbnailText.trim() || null,
        variantId: result.variantId,
      });

      setUploadJob({
        assistPackage: response.assistPackage,
        channel: "instagram",
        error: null,
        projectId,
        status: response.status,
        uploadJobId: response.uploadJobId,
      });
      setFeedback("업로드 전에 확인할 준비물이 정리되었습니다.");
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

  const progressSteps = generationStatus?.steps ?? [];
  const recentItems = recentProjects.slice(0, 4);
  const selectedBusiness =
    BUSINESS_OPTIONS.find((option) => option.id === businessType) ?? BUSINESS_OPTIONS[0];
  const fileSummary =
    files.length > 0
      ? `${files.length}장 업로드됨`
      : "샘플 없이도 구조를 먼저 볼 수 있습니다";
  const primaryObjectPosition = "center center";
  const primaryObjectFit = primaryVisual.src.startsWith("/sample-assets/") ? "contain" : "cover";
  const showProgress = isGenerating && progressSteps.length > 0;

  return (
    <main className="app-shell studio-shell">
      <section className="studio-landing">
        <section className="studio-landing-hero">
          <figure className="studio-landing-hero__media">
            <img
              src={primaryVisual.src}
              alt={primaryVisual.note}
              style={{ objectFit: "cover", objectPosition: primaryObjectPosition }}
            />
            <div className="studio-landing-hero__shade" />
          </figure>

          <div className="studio-landing-hero__copy">
            <span className="studio-kicker">가게 숏폼 스튜디오</span>
            <h1>사진으로 바로 광고 숏폼을 정리합니다.</h1>
            <p>
              사진을 넣고 목적만 고르면 됩니다. 결과 확인과 업로드 준비는 아래에서
              이어집니다.
            </p>
            <div className="studio-landing-hero__meta">
              <span>사진 업로드</span>
              <span>문구 정리</span>
              <span>업로드 준비</span>
            </div>
          </div>
        </section>

        <section className="studio-launcher">
          <div className="studio-launcher__grid">
            <section className="studio-launcher__group">
              <div className="studio-launcher__head">
                <span>사진</span>
                <strong>사진부터 넣습니다.</strong>
              </div>

              <div className="studio-launcher__actions">
                <button
                  type="button"
                  className="button button-primary"
                  onClick={() => fileInputRef.current?.click()}
                >
                  사진 선택하기
                </button>
                <button
                  type="button"
                  className="button button-secondary"
                  onClick={handleSampleClick}
                >
                  샘플로 시작
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

              <div className="studio-launcher__note">{fileSummary}</div>
              {files.length > 0 ? (
                <div className="studio-launcher__chips">
                  {files.slice(0, 2).map((file) => (
                    <span key={`${file.name}-${file.lastModified}`}>{file.name}</span>
                  ))}
                </div>
              ) : null}
            </section>

            <section className="studio-launcher__group">
              <div className="studio-launcher__head">
                <span>목적</span>
                <strong>무엇을 알릴지 고릅니다.</strong>
              </div>

              <div className="studio-launcher__tabs">
                {PURPOSE_OPTIONS.map((option) => {
                  const active = option.id === purpose;
                  return (
                    <button
                      key={option.id}
                      type="button"
                      className={active ? "studio-launcher__tab studio-launcher__tab--active" : "studio-launcher__tab"}
                      onClick={() => setPurpose(option.id)}
                    >
                      {option.title}
                    </button>
                  );
                })}
              </div>
            </section>

            <section className="studio-launcher__group">
              <div className="studio-launcher__head">
                <span>가게</span>
                <strong>업종과 지역만 적습니다.</strong>
              </div>

              <div className="studio-launcher__tabs studio-launcher__tabs--compact">
                {BUSINESS_OPTIONS.map((option) => {
                  const active = option.id === businessType;
                  return (
                    <button
                      key={option.id}
                      type="button"
                      className={active ? "studio-launcher__tab studio-launcher__tab--active" : "studio-launcher__tab"}
                      onClick={() => setBusinessType(option.id)}
                    >
                      {option.title}
                    </button>
                  );
                })}
              </div>

              <div className="studio-launcher__fields">
                <label className="studio-field">
                  <span>지역 이름</span>
                  <input
                    value={regionName}
                    onChange={(event) => setRegionName(event.target.value)}
                    placeholder="예: 성수동"
                  />
                </label>
                <label className="studio-field">
                  <span>위치 설명</span>
                  <input
                    value={detailLocation}
                    onChange={(event) => setDetailLocation(event.target.value)}
                    placeholder="예: 2호선 4번 출구 앞"
                  />
                </label>
              </div>
            </section>

            <section className="studio-launcher__group studio-launcher__group--cta">
              <div className="studio-launcher__head">
                <span>실행</span>
                <strong>{isGenerating ? statusMessage : "지금 바로 결과를 만듭니다."}</strong>
              </div>

              <p className="studio-launcher__note">
                {showProgress
                  ? "현재 생성 단계만 간단히 보여드립니다."
                  : "만들기 이후 단계는 아래에서 바로 이어집니다."}
              </p>

              {showProgress ? (
                <div className="studio-progress-list">
                  {progressSteps.map((step) => (
                    <div key={step.name} className="studio-progress-item">
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
              ) : null}

              <button
                type="button"
                className="button button-primary"
                onClick={() => void handleGenerate()}
                disabled={isGenerating}
              >
                {isGenerating ? "만드는 중입니다..." : "콘텐츠 만들기"}
              </button>

              <button type="button" className="button button-ghost" onClick={resetFlow}>
                초기화
              </button>
            </section>
          </div>
        </section>
      </section>

      <section className="studio-workbench">
        <div className="studio-workbench__main">
          <div className="studio-section-title studio-section-title--compact">
            <h2>결과 확인</h2>
            <p>영상과 게시 이미지를 한 자리에서 바로 확인합니다.</p>
          </div>

          {result ? (
            <ResultMediaPreview result={result} />
          ) : (
            <div className="studio-result-placeholder studio-result-placeholder--minimal">
              <div className="studio-result-placeholder__visual">
                <img
                  src={primaryVisual.src}
                  alt={primaryVisual.note}
                  style={{ objectFit: primaryObjectFit, objectPosition: primaryObjectPosition }}
                />
                <div className="studio-result-placeholder__shade" />
                <div className="studio-result-placeholder__copy">
                  <span>생성 전 미리보기</span>
                  <strong>{selectedPurpose.title} 결과가 이 위치에 바로 뜹니다.</strong>
                </div>
              </div>
              <div className="studio-result-placeholder__footer">
                영상 미리보기와 게시 이미지가 이 자리에서 같이 정리됩니다.
              </div>
            </div>
          )}
        </div>

        <div className="studio-workbench__side">
          <div className="studio-section-title studio-section-title--compact">
            <h2>올리기 준비</h2>
            <p>문구를 다듬고 업로드 준비물만 받아 가시면 됩니다.</p>
          </div>

          <div className="studio-upload-form">
            <label className="studio-field">
              <span>게시글 문구</span>
              <textarea
                value={caption}
                onChange={(event) => setCaption(event.target.value)}
                rows={5}
                placeholder="가게 소개 문구가 여기에 들어옵니다."
              />
            </label>

            <label className="studio-field">
              <span>해시태그</span>
              <textarea
                value={hashtagsDraft}
                onChange={(event) => setHashtagsDraft(event.target.value)}
                rows={3}
                placeholder="#성수동 #신메뉴"
              />
            </label>

            <label className="studio-field">
              <span>썸네일 문구</span>
              <input
                value={thumbnailText}
                onChange={(event) => setThumbnailText(event.target.value)}
                placeholder="예: 오늘의 추천"
              />
            </label>

            <button
              type="button"
              className="button button-primary"
              onClick={() => void handlePrepareUpload()}
              disabled={!result || isPreparingUpload}
            >
              {isPreparingUpload ? "정리 중입니다..." : "인스타 업로드 준비하기"}
            </button>

            {uploadJob ? (
              <div style={{ display: "grid", gap: 14 }}>
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
              </div>
            ) : (
              <div className="studio-note-box">
                결과를 만든 뒤 버튼을 누르면 업로드용 캡션과 파일을 바로 정리해 드립니다.
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="studio-recent-bar">
        <div className="studio-recent-bar__head">
          <div className="studio-section-title studio-section-title--compact">
            <h2>지난 작업</h2>
            <p>최근 작업을 다시 열어 이어서 수정할 수 있습니다.</p>
          </div>

          {recentItems.length > 0 ? (
            <div className="studio-recent__list">
              {recentItems.map((project) => (
                <div key={project.projectId} className="studio-recent__item">
                  <strong>{project.projectId.slice(0, 8)}</strong>
                  <span>{project.purpose}</span>
                  <span>{project.status}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="studio-note-box">
              아직 저장된 작업이 많지 않습니다. 한 번 만들어 보시면 여기에 바로 쌓입니다.
            </div>
          )}
        </div>

        <a
          href="/history"
          className="button button-ghost"
          style={{ textDecoration: "none" }}
        >
          전체 보기
        </a>
      </section>
    </main>
  );
}
