"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import {
  getGenerationStatus,
  getLatestUploadJobForProject,
  getProjectDetail,
  getProjectResult,
  listProjects,
} from "@/lib/api";
import { ResultMediaPreview } from "@/components/result-media-preview";
import { UploadAssistPanel } from "@/components/upload-assist-panel";
import type {
  GenerationStatusResponse,
  GetProjectResponse,
  ProjectResultResponse,
  ProjectStatus,
  ProjectSummary,
  UploadJobResponse,
} from "@/lib/contracts";
import {
  BUSINESS_LABELS,
  CHANNEL_LABELS,
  PURPOSE_LABELS,
  STYLE_LABELS,
  formatDateTime,
  projectStatusLabel,
  statusTone,
} from "@/lib/display";

type HistoryFilter = "all" | ProjectStatus;

const FILTERS: Array<{ value: HistoryFilter; label: string }> = [
  { value: "all", label: "전체" },
  { value: "generated", label: "완료" },
  { value: "upload_assist", label: "업로드 준비" },
  { value: "published", label: "게시 완료" },
];

const RESULT_READY_STATUSES: ProjectStatus[] = [
  "generated",
  "upload_assist",
  "publishing",
  "published",
];

const STEP_LABELS: Record<string, string> = {
  preprocessing: "사진 정리",
  copy_generation: "문구 만들기",
  video_rendering: "영상 만들기",
  post_rendering: "게시 이미지 만들기",
  packaging: "업로드 준비",
};

function stepLabel(name: string) {
  return STEP_LABELS[name] ?? name;
}

function stepStatusLabel(status: string) {
  switch (status) {
    case "completed":
      return "완료";
    case "processing":
      return "진행 중";
    case "failed":
      return "실패";
    case "skipped":
      return "건너뜀";
    default:
      return "대기";
  }
}

export function HistoryBoard({
  initialProjectId = null,
}: {
  initialProjectId?: string | null;
}) {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [filter, setFilter] = useState<HistoryFilter>("all");
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [projectDetail, setProjectDetail] = useState<GetProjectResponse | null>(null);
  const [status, setStatus] = useState<GenerationStatusResponse | null>(null);
  const [result, setResult] = useState<ProjectResultResponse | null>(null);
  const [latestUploadJob, setLatestUploadJob] = useState<UploadJobResponse | null>(null);
  const [feedback, setFeedback] = useState(
    "완료된 작업을 고르면 영상과 업로드 준비물을 다시 확인할 수 있습니다.",
  );

  const selectedProject = useMemo(
    () => projects.find((project) => project.projectId === selectedProjectId) ?? null,
    [projects, selectedProjectId],
  );
  const readyProjectCount = useMemo(
    () => projects.filter((project) => RESULT_READY_STATUSES.includes(project.status)).length,
    [projects],
  );
  const publishedProjectCount = useMemo(
    () => projects.filter((project) => project.status === "published").length,
    [projects],
  );

  const completedStepCount =
    status?.steps?.filter((step) => step.status === "completed").length ?? 0;

  const loadProjectBundle = async (projectId: string) => {
    const [detailResponse, statusResponse] = await Promise.all([
      getProjectDetail(projectId),
      getGenerationStatus(projectId),
    ]);

    setProjectDetail(detailResponse);
    setStatus(statusResponse);

    const latestJobResponse = await getLatestUploadJobForProject(projectId).catch(() => null);
    setLatestUploadJob(latestJobResponse);

    if (
      statusResponse.result ||
      RESULT_READY_STATUSES.includes(statusResponse.projectStatus)
    ) {
      const resultResponse = await getProjectResult(projectId).catch(() => null);
      setResult(resultResponse);
    } else {
      setResult(null);
    }
  };

  const loadProjects = async () => {
    const response = await listProjects(filter === "all" ? undefined : filter);
    setProjects(response.items);

    if (response.items.length === 0) {
      setSelectedProjectId(null);
      setProjectDetail(null);
      setStatus(null);
      setResult(null);
      setLatestUploadJob(null);
      return;
    }

    const requestedProject = initialProjectId
      ? response.items.find((item) => item.projectId === initialProjectId)
      : null;
    const preferredProject =
      response.items.find((item) => RESULT_READY_STATUSES.includes(item.status)) ??
      response.items[0] ??
      null;
    const nextProjectId = response.items.some(
      (item) => item.projectId === selectedProjectId,
    )
      ? selectedProjectId
      : requestedProject?.projectId ?? preferredProject?.projectId ?? null;

    if (nextProjectId) {
      if (nextProjectId === selectedProjectId) {
        await loadProjectBundle(nextProjectId);
      } else {
        setSelectedProjectId(nextProjectId);
      }
    }
  };

  useEffect(() => {
    void loadProjects().catch((error) => {
      setFeedback(
        error instanceof Error
          ? error.message
          : "지난 작업을 불러오지 못했습니다.",
      );
    });
  }, [filter]);

  useEffect(() => {
    if (!selectedProjectId) {
      return;
    }

    void loadProjectBundle(selectedProjectId).catch((error) => {
      setFeedback(
        error instanceof Error
          ? error.message
          : "선택한 작업을 불러오지 못했습니다.",
      );
    });
  }, [selectedProjectId]);

  return (
    <main className="app-shell workspace-page">
      <section className="workspace-overview">
        <div className="workspace-overview__main">
          <span className="workspace-label">지난 작업</span>
          <h1>만든 결과를 다시 엽니다.</h1>
          <p>
            최근 작업과 업로드 준비 상태를 한 화면에서 다시 확인합니다.
          </p>
        </div>
        <div className="workspace-overview__stats">
          <div className="workspace-inline-stats">
            <div className="workspace-stat">
              <span>저장된 작업</span>
              <strong>{projects.length}개</strong>
            </div>
            <div className="workspace-stat">
              <span>다시 열 수 있는 결과</span>
              <strong>{readyProjectCount}개</strong>
            </div>
            <div className="workspace-stat">
              <span>게시 완료</span>
              <strong>{publishedProjectCount}개</strong>
            </div>
          </div>
          <div className="workspace-note">
            <strong>현재 안내</strong>
            <p>{feedback}</p>
            {selectedProject ? (
              <span>
                선택 중: {PURPOSE_LABELS[selectedProject.purpose].title} ·{" "}
                {projectStatusLabel(selectedProject.status)}
              </span>
            ) : null}
          </div>
        </div>
      </section>

      <div className="workspace-columns">
        <aside className="workspace-rail">
          <div className="workspace-section">
            <div className="workspace-section-head">
              <div>
                <h2>최근 작업</h2>
                <p>필요한 상태만 골라 바로 다시 엽니다.</p>
              </div>
            </div>

            <div className="workspace-filter-row" role="tablist" aria-label="상태 필터">
              {FILTERS.map((item) => (
                <button
                  key={item.value}
                  className={
                    filter === item.value
                      ? "workspace-filter workspace-filter--active"
                      : "workspace-filter"
                  }
                  onClick={() => setFilter(item.value)}
                >
                  {item.label}
                </button>
              ))}
            </div>

            {projects.length === 0 ? (
              <div className="empty-state">
                <strong>아직 저장된 작업이 없습니다.</strong>
                <p>먼저 사진으로 하나 만들어 보시면 이 화면에 자동으로 쌓입니다.</p>
                <Link href="/" className="button button-primary">
                  새로 만들기
                </Link>
              </div>
            ) : (
              <div className="workspace-list">
                {projects.map((project) => (
                  <button
                    key={project.projectId}
                    className={
                      selectedProjectId === project.projectId
                        ? "project-row project-row--active"
                        : "project-row"
                    }
                    onClick={() => setSelectedProjectId(project.projectId)}
                    >
                    <div className="project-row__top">
                      <div className="project-row__title">
                        <strong>
                          {PURPOSE_LABELS[project.purpose].title} ·{" "}
                          {BUSINESS_LABELS[project.businessType]}
                        </strong>
                        <span>{projectStatusLabel(project.status)} 작업입니다.</span>
                      </div>
                      <span className={`tone-badge tone-badge--${statusTone(project.status)}`}>
                        {projectStatusLabel(project.status)}
                      </span>
                    </div>
                    <div className="project-row__meta">
                      <span>{STYLE_LABELS[project.style].title}</span>
                      <span>{formatDateTime(project.createdAt)}</span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </aside>

        <section className="workspace-main">
          {!projectDetail ? (
            <div className="workspace-section">
              <div className="empty-state">
                <strong>왼쪽에서 작업을 하나 골라 주세요.</strong>
                <p>선택하면 영상, 문구, 업로드 준비물을 바로 보여드립니다.</p>
              </div>
            </div>
          ) : (
            <>
              <div className="workspace-section">
                <div className="workspace-section-head">
                  <div>
                    <h2>선택한 작업</h2>
                    <p>결과와 업로드 준비를 다시 확인합니다.</p>
                  </div>
                </div>

                <div className="workspace-kpi-grid">
                  <div className="workspace-kpi">
                    <span className="workspace-kpi__label">무엇을 만들었나요</span>
                    <strong>
                      {PURPOSE_LABELS[projectDetail.purpose].title} ·{" "}
                      {BUSINESS_LABELS[projectDetail.businessType]}
                    </strong>
                    <p>
                      {projectDetail.regionName}
                      {projectDetail.detailLocation
                        ? ` · ${projectDetail.detailLocation}`
                        : ""}
                    </p>
                  </div>
                  <div className="workspace-kpi">
                    <span className="workspace-kpi__label">현재 상태</span>
                    <strong>{projectStatusLabel(projectDetail.status)}</strong>
                    <p>완료된 단계 {completedStepCount}개</p>
                  </div>
                  <div className="workspace-kpi">
                    <span className="workspace-kpi__label">올릴 채널</span>
                    <strong>
                      {projectDetail.channels
                        .map((channel) => CHANNEL_LABELS[channel].title)
                        .join(", ")}
                    </strong>
                    <p>{STYLE_LABELS[projectDetail.style].hint}</p>
                  </div>
                </div>

                {status?.steps?.length ? (
                  <div className="workspace-stack">
                    <div className="workspace-stack__title">
                      <strong>진행 기록</strong>
                      <span>어디까지 끝났는지 한 번에 확인합니다.</span>
                    </div>
                    <div className="workspace-status-grid">
                      {status.steps.map((step) => (
                        <div key={step.name} className="workspace-status-card">
                          <strong>{stepLabel(step.name)}</strong>
                          <span
                            className={`tone-badge tone-badge--${statusTone(step.status)}`}
                          >
                            {stepStatusLabel(step.status)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}
              </div>

              <div className="workspace-section">
                {result ? (
                  <>
                    <ResultMediaPreview
                      result={result}
                      title="결과 다시 보기"
                      description="완성된 영상과 게시 이미지를 다시 열어 바로 사용할 수 있습니다."
                    />
                    <div className="workspace-kpi">
                      <span className="workspace-kpi__label">문구 요약</span>
                      <strong>{result.copySet.hookText}</strong>
                      <p>{result.copySet.ctaText}</p>
                      <div className="tag-row">
                        {result.copySet.hashtags.map((hashtag) => (
                          <span key={hashtag} className="tag-pill">
                            {hashtag}
                          </span>
                        ))}
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="workspace-kpi">
                    <span className="workspace-kpi__label">결과 상태</span>
                    <strong>아직 결과를 준비하는 중입니다.</strong>
                    <p>잠시 뒤 새로고침하면 최신 결과를 다시 확인할 수 있습니다.</p>
                  </div>
                )}
              </div>

              <div className="workspace-section">
                {latestUploadJob?.assistPackage ? (
                  <UploadAssistPanel
                    assistPackage={latestUploadJob.assistPackage}
                    postUrl={result?.post.url ?? null}
                    completeHint="메인 화면으로 돌아가 업로드 완료만 눌러 정리하시면 됩니다."
                  />
                ) : (
                  <div className="workspace-kpi">
                    <span className="workspace-kpi__label">업로드 준비</span>
                    <strong>아직 업로드 준비물이 없습니다.</strong>
                    <p>
                      메인 화면에서 이 작업을 다시 열고 업로드 준비 버튼을 누르면 바로
                      정리됩니다.
                    </p>
                  </div>
                )}

                <div className="history-actions">
                  <Link
                    href={
                      latestUploadJob
                        ? `/?projectId=${projectDetail.projectId}&uploadJobId=${latestUploadJob.uploadJobId}`
                        : `/?projectId=${projectDetail.projectId}`
                    }
                    className="button button-primary"
                  >
                    이 작업 이어서 열기
                  </Link>
                  <button
                    className="button button-secondary"
                    onClick={() =>
                      selectedProjectId && void loadProjectBundle(selectedProjectId)
                    }
                  >
                    상태 다시 불러오기
                  </button>
                  <Link href="/" className="button button-ghost">
                    새로 만들기
                  </Link>
                </div>
              </div>
            </>
          )}
        </section>
      </div>
    </main>
  );
}
