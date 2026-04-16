"use client";

import { useState } from "react";
import type { PublishAssistPackage } from "@/lib/contracts";
import { buildMediaProxyUrl, resolveMediaUrl } from "@/lib/media-url";

type UploadAssistPanelProps = {
  assistPackage: PublishAssistPackage;
  postUrl?: string | null;
  completeHint?: string;
};

async function copyText(text: string) {
  await navigator.clipboard.writeText(text);
}

export function UploadAssistPanel({ assistPackage, postUrl = null, completeHint = "업로드 후 이 화면으로 돌아와 완료 상태를 정리해 주세요." }: UploadAssistPanelProps) {
  const [copyFeedback, setCopyFeedback] = useState<string | null>(null);
  const hashtagText = assistPackage.hashtags.join(" ");
  const combinedText = [assistPackage.caption, hashtagText].filter(Boolean).join("\n\n");
  const mediaOpenUrl = resolveMediaUrl(assistPackage.mediaUrl);
  const mediaDownloadUrl = buildMediaProxyUrl(assistPackage.mediaUrl, { download: true, filename: "shortform.mp4" });
  const postOpenUrl = postUrl ? resolveMediaUrl(postUrl) : null;
  const postDownloadUrl = postUrl ? buildMediaProxyUrl(postUrl, { download: true, filename: "post.png" }) : null;

  const handleCopy = async (label: string, text: string) => {
    try {
      await copyText(text);
      setCopyFeedback(`${label}을 클립보드에 복사했습니다.`);
    } catch {
      setCopyFeedback(`${label} 복사에 실패했습니다. 브라우저 권한을 확인해 주세요.`);
    }
  };

  return (
    <section
      style={{
        display: "grid",
        gap: 14,
        padding: 18,
        borderRadius: 8,
        border: "1px solid var(--theme-panel-border, rgba(29,22,17,0.08))",
        background: "var(--theme-panel-soft, rgba(250,247,243,0.92))",
      }}
    >
      <div style={{ display: "grid", gap: 4 }}>
        <strong>업로드 준비물</strong>
        <p style={{ color: "var(--theme-muted, var(--muted))", lineHeight: 1.55 }}>
          영상, 게시글, 캡션, 해시태그를 한 번에 정리해 두었습니다. 아래 순서대로 열고 붙여 넣으면 바로 올릴 수 있습니다.
        </p>
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
        <a href={mediaOpenUrl} target="_blank" rel="noreferrer" className="button button-secondary">
          영상 열기
        </a>
        <a href={mediaDownloadUrl} className="button button-secondary">
          영상 다운로드
        </a>
        {postOpenUrl ? (
          <a href={postOpenUrl} target="_blank" rel="noreferrer" className="button button-ghost">
            게시글 열기
          </a>
        ) : null}
        {postDownloadUrl ? (
          <a href={postDownloadUrl} className="button button-ghost">
            게시글 다운로드
          </a>
        ) : null}
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
        <button className="button button-primary" onClick={() => void handleCopy("캡션", assistPackage.caption)}>
          캡션 복사
        </button>
        <button className="button button-secondary" onClick={() => void handleCopy("해시태그", hashtagText)}>
          해시태그 복사
        </button>
        <button className="button button-ghost" onClick={() => void handleCopy("업로드 패키지", combinedText)}>
          전체 복사
        </button>
      </div>

      {copyFeedback ? (
        <p style={{ color: "var(--theme-accent-strong, #226b5f)", fontWeight: 700, margin: 0 }}>{copyFeedback}</p>
      ) : null}

      <div style={{ display: "grid", gap: 10 }}>
        <div
          style={{
            padding: 12,
            borderRadius: 8,
            background: "var(--theme-panel-surface, rgba(255,255,255,0.82))",
            border: "1px solid var(--theme-panel-border, rgba(29,22,17,0.06))",
            display: "grid",
            gap: 6,
          }}
        >
          <span style={{ fontSize: ".82rem", fontWeight: 800, color: "var(--theme-muted, var(--muted))" }}>캡션</span>
          <div style={{ lineHeight: 1.6 }}>{assistPackage.caption}</div>
        </div>

        <div
          style={{
            padding: 12,
            borderRadius: 8,
            background: "var(--theme-panel-surface, rgba(255,255,255,0.82))",
            border: "1px solid var(--theme-panel-border, rgba(29,22,17,0.06))",
            display: "grid",
            gap: 8,
          }}
        >
          <span style={{ fontSize: ".82rem", fontWeight: 800, color: "var(--theme-muted, var(--muted))" }}>해시태그</span>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {assistPackage.hashtags.map((hashtag) => (
              <span
                key={hashtag}
                style={{
                  padding: "6px 10px",
                  borderRadius: 8,
                  background: "var(--theme-accent-soft, rgba(246,239,230,0.9))",
                }}
              >
                {hashtag}
              </span>
            ))}
          </div>
        </div>

        <div
          style={{
            padding: 12,
            borderRadius: 8,
            background: "var(--theme-panel-surface, rgba(255,255,255,0.82))",
            border: "1px solid var(--theme-panel-border, rgba(29,22,17,0.06))",
            display: "grid",
            gap: 6,
          }}
        >
          <span style={{ fontSize: ".82rem", fontWeight: 800, color: "var(--theme-muted, var(--muted))" }}>썸네일 문구</span>
          <div>{assistPackage.thumbnailText || "별도 문구 없음"}</div>
        </div>
      </div>

      <ol style={{ margin: 0, paddingLeft: 18, lineHeight: 1.65, color: "var(--text)" }}>
        <li>영상 또는 게시글을 열어 업로드 화면에 준비합니다.</li>
        <li>캡션과 해시태그를 복사해서 붙여 넣습니다.</li>
        <li>썸네일 문구가 필요하면 마지막으로 반영합니다.</li>
        <li>{completeHint}</li>
      </ol>
    </section>
  );
}
