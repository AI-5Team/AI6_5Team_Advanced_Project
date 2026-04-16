import type { ProjectResultResponse } from "@/lib/contracts";
import { resolveMediaUrl } from "@/lib/media-url";

type ResultMediaPreviewProps = {
  result: ProjectResultResponse;
  title?: string;
  description?: string;
  showDiagnostics?: boolean;
};

const mediaCardStyle = {
  borderRadius: 8,
  border: "1px solid var(--theme-panel-border, rgba(17,17,17,0.08))",
  padding: 16,
  background: "var(--theme-panel-surface, rgba(255,255,255,0.98))",
  display: "grid",
  gap: 12,
} as const;

const mediaFrameStyle = {
  overflow: "hidden",
  borderRadius: 8,
  border: "1px solid var(--theme-panel-border, rgba(17,17,17,0.08))",
  background: "var(--theme-frame-surface, #111111)",
} as const;

export function ResultMediaPreview({ result, title = "결과 미리보기", description, showDiagnostics = false }: ResultMediaPreviewProps) {
  const videoSrc = resolveMediaUrl(result.video.url);
  const postSrc = resolveMediaUrl(result.post.url);
  const rendererSummary = result.rendererSummary;
  const rendererBadges = [
    rendererSummary?.videoSourceMode ? `source ${rendererSummary.videoSourceMode}` : null,
    rendererSummary?.motionMode ? `motion ${rendererSummary.motionMode}` : null,
    rendererSummary?.framingMode ? `framing ${rendererSummary.framingMode}` : null,
    rendererSummary?.durationStrategy ? `duration ${rendererSummary.durationStrategy}` : null,
  ].filter(Boolean) as string[];

  return (
    <section style={{ display: "grid", gap: 12 }}>
      <div style={{ display: "grid", gap: 6 }}>
        <strong>{title}</strong>
        {description ? <p style={{ color: "var(--theme-muted, var(--muted))", lineHeight: 1.55 }}>{description}</p> : null}
        {showDiagnostics && rendererBadges.length ? (
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {rendererBadges.map((badge) => (
              <span
                key={badge}
                style={{
                  borderRadius: 999,
                  border: "1px solid var(--theme-panel-border, rgba(17,17,17,0.1))",
                  background: "var(--theme-accent-soft, rgba(17,17,17,0.04))",
                  padding: "6px 10px",
                  fontSize: ".82rem",
                  color: "var(--theme-muted, var(--muted))",
                }}
              >
                {badge}
              </span>
            ))}
            {rendererSummary?.targetDurationSec ? (
              <span
                style={{
                  borderRadius: 999,
                  border: "1px solid var(--theme-panel-border, rgba(17,17,17,0.1))",
                  background: "var(--theme-accent-soft, rgba(17,17,17,0.04))",
                  padding: "6px 10px",
                  fontSize: ".82rem",
                  color: "var(--theme-muted, var(--muted))",
                }}
              >
                target {rendererSummary.targetDurationSec}초
              </span>
            ) : null}
          </div>
        ) : null}
      </div>

      <div style={{ display: "grid", gap: 12, gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))" }}>
        <article style={mediaCardStyle}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
            <strong>영상 미리보기</strong>
            <span style={{ color: "var(--theme-muted, var(--muted))", fontSize: ".9rem" }}>{result.video.durationSec}초</span>
          </div>
          <div style={{ ...mediaFrameStyle, aspectRatio: "9 / 16" }}>
            <video
              key={videoSrc}
              src={videoSrc}
              controls
              muted
              playsInline
              preload="metadata"
              style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
            />
          </div>
          <a href={videoSrc} target="_blank" rel="noreferrer" className="button button-ghost" style={{ width: "100%", justifyContent: "center" }}>
            영상 원본 열기
          </a>
        </article>

        <article style={mediaCardStyle}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
            <strong>게시 이미지</strong>
            <span style={{ color: "var(--theme-muted, var(--muted))", fontSize: ".9rem" }}>업로드용 이미지</span>
          </div>
          <div style={{ ...mediaFrameStyle, aspectRatio: "4 / 5", background: "var(--theme-frame-alt, rgba(17,17,17,0.04))" }}>
            <img src={postSrc} alt="생성된 게시글 미리보기" style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }} />
          </div>
          <a href={postSrc} target="_blank" rel="noreferrer" className="button button-ghost" style={{ width: "100%", justifyContent: "center" }}>
            게시글 원본 열기
          </a>
        </article>
      </div>
    </section>
  );
}
