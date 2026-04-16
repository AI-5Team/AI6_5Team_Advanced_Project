import type { CSSProperties } from "react";
import type { ScenePlanPayload, ScenePlanScene } from "@/lib/scene-plan";

type SceneLayout = "offer-poster" | "review-poster" | "cta-poster";
type SceneKind = "opening" | "support" | "review" | "closing";

type TextBudget = {
  maxLines: number;
  maxCharsPerLine: number;
};

type SceneBudget = {
  headline: TextBudget;
  body: TextBudget;
  kicker: TextBudget;
  cta: TextBudget;
};

type SceneScale = {
  headlineFontSize: string;
  headlineLineHeight: number;
  headlineLetterSpacing: string;
  headlineMaxWidth: string;
  bodyFontSize: number;
  bodyLineHeight: number;
  bodyMaxWidth: string;
  kickerFontSize: number;
  kickerLineHeight: number;
  kickerMaxWidth: string;
  ctaFontSize: number;
  ctaLineHeight: number;
  ctaLetterSpacing: string;
};

type SceneRule = {
  layout: SceneLayout;
  budget: SceneBudget;
  scale: SceneScale;
};

type RawSceneSpec = {
  id: string;
  label: string;
  tone: string;
  kind: SceneKind;
  imageSrc: string;
  badge: string;
  headline: string;
  body: string;
  kicker: string;
  cta: string;
  accent: string;
  surface: string;
  stamp: string;
};

export type SceneSpec = RawSceneSpec & SceneRule;

const SCENE_RULES: Record<SceneKind, SceneRule> = {
  opening: {
    layout: "offer-poster",
    budget: {
      headline: { maxLines: 2, maxCharsPerLine: 9 },
      body: { maxLines: 1, maxCharsPerLine: 12 },
      kicker: { maxLines: 2, maxCharsPerLine: 17 },
      cta: { maxLines: 1, maxCharsPerLine: 12 },
    },
    scale: {
      headlineFontSize: "clamp(4rem, 6.5vw, 5.6rem)",
      headlineLineHeight: 0.94,
      headlineLetterSpacing: "-0.06em",
      headlineMaxWidth: "66%",
      bodyFontSize: 28,
      bodyLineHeight: 1,
      bodyMaxWidth: "22ch",
      kickerFontSize: 20,
      kickerLineHeight: 1.42,
      kickerMaxWidth: "24ch",
      ctaFontSize: 34,
      ctaLineHeight: 1,
      ctaLetterSpacing: "-0.05em",
    },
  },
  review: {
    layout: "review-poster",
    budget: {
      headline: { maxLines: 2, maxCharsPerLine: 10 },
      body: { maxLines: 2, maxCharsPerLine: 18 },
      kicker: { maxLines: 2, maxCharsPerLine: 16 },
      cta: { maxLines: 1, maxCharsPerLine: 12 },
    },
    scale: {
      headlineFontSize: "clamp(3.4rem, 5vw, 4.8rem)",
      headlineLineHeight: 0.98,
      headlineLetterSpacing: "-0.05em",
      headlineMaxWidth: "70%",
      bodyFontSize: 22,
      bodyLineHeight: 1.38,
      bodyMaxWidth: "26ch",
      kickerFontSize: 18,
      kickerLineHeight: 1.44,
      kickerMaxWidth: "20ch",
      ctaFontSize: 28,
      ctaLineHeight: 1.04,
      ctaLetterSpacing: "-0.04em",
    },
  },
  support: {
    layout: "offer-poster",
    budget: {
      headline: { maxLines: 2, maxCharsPerLine: 10 },
      body: { maxLines: 2, maxCharsPerLine: 13 },
      kicker: { maxLines: 2, maxCharsPerLine: 16 },
      cta: { maxLines: 1, maxCharsPerLine: 12 },
    },
    scale: {
      headlineFontSize: "clamp(3.6rem, 5.8vw, 4.8rem)",
      headlineLineHeight: 0.96,
      headlineLetterSpacing: "-0.05em",
      headlineMaxWidth: "62%",
      bodyFontSize: 24,
      bodyLineHeight: 1.08,
      bodyMaxWidth: "22ch",
      kickerFontSize: 18,
      kickerLineHeight: 1.38,
      kickerMaxWidth: "22ch",
      ctaFontSize: 30,
      ctaLineHeight: 1,
      ctaLetterSpacing: "-0.04em",
    },
  },
  closing: {
    layout: "cta-poster",
    budget: {
      headline: { maxLines: 2, maxCharsPerLine: 8 },
      body: { maxLines: 2, maxCharsPerLine: 11 },
      kicker: { maxLines: 2, maxCharsPerLine: 13 },
      cta: { maxLines: 1, maxCharsPerLine: 10 },
    },
    scale: {
      headlineFontSize: "clamp(3rem, 4.8vw, 4.3rem)",
      headlineLineHeight: 1.02,
      headlineLetterSpacing: "-0.04em",
      headlineMaxWidth: "72%",
      bodyFontSize: 20,
      bodyLineHeight: 1.34,
      bodyMaxWidth: "24ch",
      kickerFontSize: 18,
      kickerLineHeight: 1.4,
      kickerMaxWidth: "18ch",
      ctaFontSize: 32,
      ctaLineHeight: 1.02,
      ctaLetterSpacing: "-0.05em",
    },
  },
};

const RAW_SCENES: readonly RawSceneSpec[] = [
  {
    id: "opening",
    label: "오프닝 씬",
    tone: "혜택 먼저",
    kind: "opening",
    imageSrc: "/api/sample-assets/katsu",
    badge: "TODAY DEAL",
    headline: "오늘만 2천원↓",
    body: "규카츠 세트 특가",
    kicker: "사진 한 장만으로도 혜택이 먼저 보이는 오프닝",
    cta: "저장 말고 바로 방문",
    accent: "#E5FF39",
    surface: "#100f0d",
    stamp: "2,000원 OFF",
  },
  {
    id: "review",
    label: "리뷰 씬",
    tone: "반응 증명",
    kind: "review",
    imageSrc: "/api/sample-assets/ramen",
    badge: "REAL REVIEW",
    headline: "한 번 오면 또 생각나는 라멘",
    body: "국물 밸런스 좋다는 반응 많은 컷",
    kicker: "재방문 이유 먼저 남기는 리뷰 컷",
    cta: "오늘 저녁 메뉴로 저장",
    accent: "#7BF5FF",
    surface: "#0E1317",
    stamp: "REVIEW 128+",
  },
  {
    id: "closing",
    label: "CTA 씬",
    tone: "행동 유도",
    kind: "closing",
    imageSrc: "/api/sample-assets/beer",
    badge: "LAST CALL",
    headline: "오늘 올릴 컷\n이미 끝났습니다",
    body: "맥주 컷과 업로드 문구 한 번에",
    kicker: "설명보다 행동 먼저 남는 마감 장면",
    cta: "지금 바로 업로드",
    accent: "#FF6D2E",
    surface: "#140F12",
    stamp: "POST READY",
  },
] as const;

const pageStyle: CSSProperties = {
  width: "min(1480px, calc(100% - 32px))",
  margin: "0 auto",
  padding: "24px 0 40px",
  display: "grid",
  gap: 24,
};

const heroStyle: CSSProperties = {
  position: "relative",
  overflow: "hidden",
  borderRadius: 36,
  padding: 32,
  background:
    "linear-gradient(140deg, rgba(255,248,239,0.96), rgba(241,232,220,0.88)), radial-gradient(circle at 0% 0%, rgba(229,255,57,0.22), transparent 24%), radial-gradient(circle at 100% 0%, rgba(255,109,46,0.18), transparent 26%)",
  border: "1px solid rgba(25,19,15,0.08)",
  boxShadow: "0 28px 64px rgba(38, 24, 14, 0.12)",
  display: "grid",
  gridTemplateColumns: "minmax(0, 0.9fr) minmax(300px, 1.1fr)",
  gap: 28,
  alignItems: "end",
};

const heroCopyStyle: CSSProperties = {
  display: "grid",
  gap: 14,
  alignContent: "start",
};

const heroPosterWrapStyle: CSSProperties = {
  minHeight: 0,
};

const gridStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
  gap: 18,
};

const sceneCardStyle: CSSProperties = {
  display: "grid",
  gap: 14,
};

const frameBaseStyle: CSSProperties = {
  position: "relative",
  width: "100%",
  aspectRatio: "9 / 16",
  overflow: "hidden",
  background: "#0f0d0c",
  color: "#fffdf7",
};

const metaRowStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: 12,
};

const previewBadgeStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  minHeight: 34,
  padding: "0 14px",
  borderRadius: 999,
  background: "rgba(18,16,14,0.07)",
  fontSize: 12,
  fontWeight: 900,
  letterSpacing: "0.08em",
  color: "rgba(18,16,14,0.72)",
};

function countCharacters(text: string) {
  return Array.from(text).length;
}

function truncateToLength(text: string, maxChars: number) {
  if (countCharacters(text) <= maxChars) {
    return text;
  }

  if (maxChars <= 1) {
    return "…";
  }

  return `${Array.from(text).slice(0, maxChars - 1).join("")}…`;
}

function chunkByCharacters(text: string, maxCharsPerLine: number) {
  const characters = Array.from(text);
  const lines: string[] = [];

  for (let index = 0; index < characters.length; index += maxCharsPerLine) {
    lines.push(characters.slice(index, index + maxCharsPerLine).join(""));
  }

  return lines;
}

function wrapSegment(segment: string, maxCharsPerLine: number) {
  const trimmed = segment.trim();
  if (!trimmed) {
    return [];
  }

  const words = trimmed.split(/\s+/u).filter(Boolean);
  if (words.length <= 1) {
    return chunkByCharacters(trimmed, maxCharsPerLine);
  }

  const lines: string[] = [];
  let currentLine = "";

  for (const word of words) {
    const candidate = currentLine ? `${currentLine} ${word}` : word;
    if (countCharacters(candidate) <= maxCharsPerLine) {
      currentLine = candidate;
      continue;
    }

    if (currentLine) {
      lines.push(currentLine);
      currentLine = "";
    }

    if (countCharacters(word) <= maxCharsPerLine) {
      currentLine = word;
      continue;
    }

    const chunks = chunkByCharacters(word, maxCharsPerLine);
    lines.push(...chunks.slice(0, -1));
    currentLine = chunks.at(-1) ?? "";
  }

  if (currentLine) {
    lines.push(currentLine);
  }

  return lines;
}

function applyTextBudget(text: string, budget: TextBudget) {
  const requestedLines = text
    .split("\n")
    .flatMap((segment) => wrapSegment(segment, budget.maxCharsPerLine))
    .filter(Boolean);

  if (requestedLines.length === 0) {
    return "";
  }

  const limitedLines = requestedLines.slice(0, budget.maxLines);
  if (requestedLines.length > budget.maxLines) {
    const lastIndex = limitedLines.length - 1;
    limitedLines[lastIndex] = truncateToLength(limitedLines[lastIndex] ?? "", budget.maxCharsPerLine);
  }

  return limitedLines.join("\n");
}

function prepareScene(scene: RawSceneSpec): SceneSpec {
  const rule = SCENE_RULES[scene.kind];
  return {
    ...scene,
    layout: rule.layout,
    budget: rule.budget,
    scale: rule.scale,
    headline: applyTextBudget(scene.headline, rule.budget.headline),
    body: applyTextBudget(scene.body, rule.budget.body),
    kicker: applyTextBudget(scene.kicker, rule.budget.kicker),
    cta: applyTextBudget(scene.cta, rule.budget.cta),
  };
}

export const SCENES: readonly SceneSpec[] = RAW_SCENES.map(prepareScene);

function resolveSceneKind(scene: ScenePlanScene): SceneKind {
  if (scene.sceneRole === "review") {
    return "review";
  }
  if (scene.sceneRole === "closing") {
    return "closing";
  }
  if (scene.sceneRole === "support") {
    return "support";
  }
  return "opening";
}

function resolveSceneImageSrc(storagePath: string, assetBaseUrl?: string) {
  if (storagePath.startsWith("data:") || storagePath.startsWith("http://") || storagePath.startsWith("https://")) {
    return storagePath;
  }
  if (storagePath.startsWith("/docs/sample/") || storagePath.startsWith("/samples/input/")) {
    return `/api/local-media?storagePath=${encodeURIComponent(storagePath)}`;
  }
  if (storagePath.startsWith("/api/")) {
    return storagePath;
  }
  if (storagePath.startsWith("/media/")) {
    return assetBaseUrl ? new URL(storagePath, `${assetBaseUrl}/`).toString() : storagePath;
  }
  if (storagePath.startsWith("/projects/")) {
    const mediaPath = `/media${storagePath}`;
    return assetBaseUrl ? new URL(mediaPath, `${assetBaseUrl}/`).toString() : mediaPath;
  }
  return "/api/sample-assets/katsu";
}

function getSceneToneLabel(scene: ScenePlanScene) {
  if (scene.sceneRole === "review") {
    return "실제 생성 리뷰";
  }
  if (scene.sceneRole === "closing") {
    return "실제 생성 CTA";
  }
  if (scene.sceneRole === "support") {
    return "실제 생성 서포트";
  }
  return "실제 생성 오프닝";
}

function getSceneLabel(scenePlan: ScenePlanPayload, scene: ScenePlanScene, index: number) {
  return `${scenePlan.templateId} · ${scene.sceneId.toUpperCase()} · ${scene.slot.toUpperCase() || index + 1}`;
}

export function sceneSpecsFromScenePlan(scenePlan: ScenePlanPayload, options?: { assetBaseUrl?: string }): SceneSpec[] {
  return scenePlan.scenes.map((scene, index) =>
    prepareScene({
      id: scene.sceneId,
      label: getSceneLabel(scenePlan, scene, index),
      tone: getSceneToneLabel(scene),
      kind: resolveSceneKind(scene),
      imageSrc: resolveSceneImageSrc(scene.asset.storagePath, options?.assetBaseUrl),
      badge: scene.copy.badgeText || scene.slot.toUpperCase(),
      headline: scene.copy.headline || scene.copy.primaryText,
      body: scene.copy.body || scene.copy.secondaryText,
      kicker: scene.copy.kicker,
      cta: scene.sceneRole === "closing" ? scene.copy.primaryText || scene.copy.cta : scene.copy.cta || scene.copy.primaryText,
      accent: scene.renderHints.palette?.accent || "#E5FF39",
      surface: scene.renderHints.palette?.background || "#100f0d",
      stamp: scene.copy.stampText || scene.slot.toUpperCase(),
    }),
  );
}

function splitHeadline(text: string) {
  return text.split("\n").map((line, index) => (
    <span key={`${text}-${index}`} style={{ display: "block" }}>
      {line}
    </span>
  ));
}

function splitMultilineText(text: string) {
  return text.split("\n").map((line, index) => (
    <span key={`${text}-${index}`} style={{ display: "block" }}>
      {line}
    </span>
  ));
}

function Sticker({ accent, stamp }: Pick<SceneSpec, "accent" | "stamp">) {
  return (
    <div
      style={{
        position: "absolute",
        top: 48,
        right: 40,
        width: 188,
        height: 188,
        borderRadius: "50%",
        background: accent,
        color: "#121212",
        display: "grid",
        placeItems: "center",
        boxShadow: "0 22px 42px rgba(0,0,0,0.28)",
        border: "8px solid rgba(255,248,239,0.92)",
        transform: "rotate(8deg)",
        textAlign: "center",
        padding: 18,
      }}
    >
      <div style={{ display: "grid", gap: 2 }}>
        <span style={{ fontSize: 18, fontWeight: 900, letterSpacing: "0.08em" }}>TODAY</span>
        <span style={{ fontSize: 34, fontWeight: 950, lineHeight: 0.92, letterSpacing: "-0.04em" }}>{stamp}</span>
      </div>
    </div>
  );
}

function OfferPosterFrame({ scene, captureMode }: { scene: SceneSpec; captureMode: boolean }) {
  return (
    <div
      style={{
        ...frameBaseStyle,
        borderRadius: captureMode ? 0 : 34,
        background: scene.surface,
      }}
    >
      <img
        src={scene.imageSrc}
        alt={scene.headline}
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          objectFit: "cover",
          objectPosition: "60% center",
          filter: "saturate(1.08) contrast(1.02)",
          transform: "scale(1.06)",
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(180deg, rgba(8,8,8,0.08) 0%, rgba(8,8,8,0.24) 28%, rgba(8,8,8,0.72) 72%, rgba(8,8,8,0.92) 100%), linear-gradient(90deg, rgba(8,8,8,0.82) 0%, rgba(8,8,8,0.3) 44%, rgba(8,8,8,0.12) 62%, rgba(8,8,8,0.18) 100%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          top: 32,
          left: 32,
          display: "grid",
          gap: 14,
        }}
      >
        <span
          style={{
            display: "inline-flex",
            alignItems: "center",
            width: "fit-content",
            minHeight: 38,
            padding: "0 16px",
            borderRadius: 999,
            background: "rgba(255,248,239,0.92)",
            color: "#121212",
            fontSize: 13,
            fontWeight: 900,
            letterSpacing: "0.08em",
          }}
        >
          {scene.badge}
        </span>
        <span
          style={{
            display: "inline-flex",
            alignItems: "center",
            width: "fit-content",
            minHeight: 28,
            padding: "0 10px",
            borderRadius: 999,
            background: "rgba(255,255,255,0.14)",
            color: "rgba(255,253,247,0.76)",
            fontSize: 11,
            fontWeight: 800,
            letterSpacing: "0.16em",
          }}
        >
          B-GRADE PROMOTION CLIP
        </span>
      </div>

      <Sticker accent={scene.accent} stamp={scene.stamp} />

      <div
        style={{
          position: "absolute",
          left: 32,
          right: 32,
          bottom: 172,
          display: "grid",
          gap: 16,
          maxWidth: scene.scale.headlineMaxWidth,
        }}
      >
        <h2
          style={{
            margin: 0,
            fontSize: scene.scale.headlineFontSize,
            lineHeight: scene.scale.headlineLineHeight,
            letterSpacing: scene.scale.headlineLetterSpacing,
            fontWeight: 950,
          }}
        >
          {splitHeadline(scene.headline)}
        </h2>
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            width: "fit-content",
            maxWidth: scene.scale.bodyMaxWidth,
            minHeight: 70,
            padding: "0 22px",
            borderRadius: 24,
            background: "rgba(255,248,239,0.94)",
            color: "#111111",
            fontSize: scene.scale.bodyFontSize,
            lineHeight: scene.scale.bodyLineHeight,
            fontWeight: 900,
            letterSpacing: "-0.04em",
            boxShadow: "0 16px 36px rgba(0,0,0,0.18)",
          }}
        >
          {scene.body}
        </div>
        <p
          style={{
            margin: 0,
            maxWidth: scene.scale.kickerMaxWidth,
            fontSize: scene.scale.kickerFontSize,
            lineHeight: scene.scale.kickerLineHeight,
            color: "rgba(255,253,247,0.82)",
          }}
        >
          {splitMultilineText(scene.kicker)}
        </p>
      </div>

      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: 0,
          minHeight: 136,
          background: "rgba(255,248,239,0.96)",
          color: "#121212",
          display: "grid",
          gridTemplateColumns: "auto 1fr auto",
          alignItems: "center",
          gap: 18,
          padding: "24px 32px",
          borderTop: "2px solid rgba(18,18,18,0.08)",
        }}
      >
        <span
          style={{
            display: "inline-flex",
            alignItems: "center",
            minHeight: 36,
            padding: "0 12px",
            borderRadius: 999,
            background: scene.accent,
            color: "#111111",
            fontSize: 12,
            fontWeight: 900,
            letterSpacing: "0.08em",
          }}
        >
          CTA
        </span>
        <strong
          style={{
            fontSize: scene.scale.ctaFontSize,
            lineHeight: scene.scale.ctaLineHeight,
            letterSpacing: scene.scale.ctaLetterSpacing,
            fontWeight: 950,
          }}
        >
          {scene.cta}
        </strong>
        <div
          style={{
            width: 70,
            height: 70,
            borderRadius: "50%",
            border: "2px solid rgba(18,18,18,0.16)",
            display: "grid",
            placeItems: "center",
            fontSize: 30,
            fontWeight: 900,
          }}
        >
          →
        </div>
      </div>
    </div>
  );
}

function ReviewPosterFrame({ scene, captureMode }: { scene: SceneSpec; captureMode: boolean }) {
  return (
    <div
      style={{
        ...frameBaseStyle,
        borderRadius: captureMode ? 0 : 34,
        background: scene.surface,
      }}
    >
      <img
        src={scene.imageSrc}
        alt={scene.headline}
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          objectFit: "cover",
          objectPosition: "center center",
          transform: "scale(1.05)",
          filter: "saturate(1.08) contrast(1.04)",
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(180deg, rgba(5,10,14,0.12) 0%, rgba(5,10,14,0.44) 38%, rgba(5,10,14,0.84) 76%, rgba(5,10,14,0.94) 100%), linear-gradient(90deg, rgba(5,10,14,0.78) 0%, rgba(5,10,14,0.24) 42%, rgba(5,10,14,0.58) 100%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          top: 32,
          left: 32,
          right: 32,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: 12,
        }}
      >
        <span
          style={{
            display: "inline-flex",
            alignItems: "center",
            minHeight: 38,
            padding: "0 16px",
            borderRadius: 999,
            background: "rgba(255,248,239,0.94)",
            color: "#111111",
            fontSize: 13,
            fontWeight: 900,
            letterSpacing: "0.08em",
          }}
        >
          {scene.badge}
        </span>
        <span
          style={{
            display: "inline-flex",
            alignItems: "center",
            minHeight: 40,
            padding: "0 16px",
            borderRadius: 999,
            background: scene.accent,
            color: "#111111",
            fontSize: 13,
            fontWeight: 900,
            letterSpacing: "0.06em",
          }}
        >
          {scene.stamp}
        </span>
      </div>

      <div
        style={{
          position: "absolute",
          left: 24,
          right: 24,
          bottom: 24,
          padding: "26px 24px 24px",
          borderRadius: 30,
          background: "rgba(10,14,18,0.88)",
          border: "1px solid rgba(255,255,255,0.08)",
          backdropFilter: "blur(10px)",
          display: "grid",
          gap: 16,
          boxShadow: "0 20px 44px rgba(0,0,0,0.24)",
        }}
      >
        <h2
          style={{
            margin: 0,
            maxWidth: scene.scale.headlineMaxWidth,
            fontSize: scene.scale.headlineFontSize,
            lineHeight: scene.scale.headlineLineHeight,
            letterSpacing: scene.scale.headlineLetterSpacing,
            fontWeight: 950,
            color: "#fffdf7",
          }}
        >
          {splitHeadline(scene.headline)}
        </h2>
        <div
          style={{
            maxWidth: scene.scale.bodyMaxWidth,
            paddingLeft: 14,
            borderLeft: `4px solid ${scene.accent}`,
            fontSize: 24,
            lineHeight: 1.32,
            color: "#fffdf7",
            fontWeight: 800,
            letterSpacing: "-0.03em",
          }}
        >
          {splitMultilineText(scene.body)}
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "end",
            gap: 16,
          }}
        >
          <p
            style={{
              margin: 0,
              maxWidth: scene.scale.kickerMaxWidth,
              fontSize: 17,
              lineHeight: scene.scale.kickerLineHeight,
              color: "rgba(255,253,247,0.68)",
            }}
          >
            {splitMultilineText(scene.kicker)}
          </p>
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              minHeight: 66,
              padding: "0 22px",
              borderRadius: 22,
              background: scene.accent,
              color: "#111111",
              fontSize: 24,
              lineHeight: scene.scale.ctaLineHeight,
              letterSpacing: scene.scale.ctaLetterSpacing,
              fontWeight: 950,
              textAlign: "center",
              boxShadow: "0 14px 24px rgba(0,0,0,0.22)",
            }}
          >
            {scene.cta}
          </div>
        </div>
      </div>
    </div>
  );
}

function CtaPosterFrame({ scene, captureMode }: { scene: SceneSpec; captureMode: boolean }) {
  return (
    <div
      style={{
        ...frameBaseStyle,
        borderRadius: captureMode ? 0 : 34,
        background:
          "linear-gradient(180deg, rgba(15,11,12,1) 0%, rgba(22,14,17,1) 100%), radial-gradient(circle at 70% 24%, rgba(255,109,46,0.16), transparent 24%)",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "grid",
          gridTemplateRows: "1fr auto",
        }}
      >
        <div style={{ position: "relative", overflow: "hidden" }}>
          <img
            src={scene.imageSrc}
            alt={scene.headline}
            style={{
              position: "absolute",
              inset: 0,
              width: "100%",
              height: "100%",
              objectFit: "cover",
              objectPosition: "55% center",
              transform: "scale(1.08)",
              filter: "saturate(1.06) contrast(1.04)",
            }}
          />
          <div
            style={{
              position: "absolute",
              inset: 0,
              background:
                "linear-gradient(180deg, rgba(12,9,10,0.22) 0%, rgba(12,9,10,0.48) 30%, rgba(12,9,10,0.86) 78%, rgba(12,9,10,0.94) 100%), linear-gradient(90deg, rgba(12,9,10,0.84) 0%, rgba(12,9,10,0.16) 40%, rgba(12,9,10,0.56) 100%)",
            }}
          />
          <div
            style={{
              position: "absolute",
              top: 34,
              left: 32,
              right: 32,
              display: "flex",
              justifyContent: "space-between",
              gap: 12,
              alignItems: "center",
            }}
          >
            <span
              style={{
                display: "inline-flex",
                alignItems: "center",
                minHeight: 38,
                padding: "0 16px",
                borderRadius: 999,
                background: scene.accent,
                color: "#121212",
                fontSize: 12,
                fontWeight: 900,
                letterSpacing: "0.08em",
              }}
            >
              {scene.badge}
            </span>
            <span
              style={{
                display: "inline-flex",
                alignItems: "center",
                minHeight: 34,
                padding: "0 14px",
                borderRadius: 999,
                background: "rgba(255,255,255,0.08)",
                color: "rgba(255,253,247,0.74)",
                fontSize: 11,
                fontWeight: 800,
                letterSpacing: "0.16em",
              }}
            >
              {scene.stamp}
            </span>
          </div>

          <div
            style={{
              position: "absolute",
              left: 32,
              right: 32,
              bottom: 42,
              display: "grid",
              gap: 12,
              maxWidth: "64%",
            }}
          >
            <h2
              style={{
                margin: 0,
                fontSize: scene.scale.headlineFontSize,
                lineHeight: scene.scale.headlineLineHeight,
                letterSpacing: scene.scale.headlineLetterSpacing,
                fontWeight: 950,
                color: "#fffdf7",
              }}
            >
              {splitHeadline(scene.headline)}
            </h2>
          </div>
        </div>

        <div
          style={{
            position: "relative",
            minHeight: 404,
            padding: "34px 32px 40px",
            background: scene.surface,
            display: "grid",
            gap: 18,
            alignContent: "start",
          }}
        >
          <div
            style={{
              width: "100%",
              height: 8,
              borderRadius: 999,
              background: `linear-gradient(90deg, ${scene.accent}, rgba(255,255,255,0.16))`,
            }}
          />
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              width: "fit-content",
              minHeight: 34,
              padding: "0 14px",
              borderRadius: 999,
              background: "rgba(255,255,255,0.08)",
              color: "rgba(255,253,247,0.72)",
              fontSize: 12,
              fontWeight: 800,
              letterSpacing: "0.08em",
            }}
          >
            UPLOAD FLOW
          </div>
          <p
            style={{
              margin: 0,
              maxWidth: "18ch",
              fontSize: 26,
              lineHeight: 1.22,
              color: "#fffdf7",
              fontWeight: 800,
              letterSpacing: "-0.03em",
            }}
          >
            {splitMultilineText(scene.body)}
          </p>
          <p
            style={{
              margin: 0,
              maxWidth: "19ch",
              fontSize: 20,
              lineHeight: 1.44,
              color: "rgba(255,253,247,0.74)",
            }}
          >
            {splitMultilineText(scene.kicker)}
          </p>
          <div
            style={{
              minHeight: 104,
              borderRadius: 28,
              background: scene.accent,
              color: "#111111",
              display: "grid",
              placeItems: "center",
              textAlign: "center",
              padding: "18px 24px",
              fontSize: scene.scale.ctaFontSize,
              lineHeight: scene.scale.ctaLineHeight,
              letterSpacing: scene.scale.ctaLetterSpacing,
              fontWeight: 950,
              boxShadow: "0 18px 34px rgba(0,0,0,0.22)",
            }}
          >
            {scene.cta}
          </div>
        </div>
      </div>
    </div>
  );
}

export function getSceneById(sceneId: string, scenes: readonly SceneSpec[] = SCENES) {
  return scenes.find((scene) => scene.id === sceneId) ?? null;
}

export function SceneFrame({ scene, captureMode = false }: { scene: SceneSpec; captureMode?: boolean }) {
  if (scene.layout === "review-poster") {
    return <ReviewPosterFrame scene={scene} captureMode={captureMode} />;
  }

  if (scene.layout === "cta-poster") {
    return <CtaPosterFrame scene={scene} captureMode={captureMode} />;
  }

  return <OfferPosterFrame scene={scene} captureMode={captureMode} />;
}

function ScenePreviewCard({ scene }: { scene: SceneSpec }) {
  return (
    <article style={sceneCardStyle}>
      <div style={metaRowStyle}>
        <div>
          <div style={{ fontSize: 12, fontWeight: 900, letterSpacing: "0.08em", color: "rgba(18,16,14,0.5)" }}>{scene.label}</div>
          <div style={{ marginTop: 6, fontSize: 24, lineHeight: 1.02, fontWeight: 900, letterSpacing: "-0.04em" }}>{scene.tone}</div>
        </div>
        <span style={previewBadgeStyle}>{`${scene.budget.headline.maxLines}/${scene.budget.body.maxLines}/${scene.budget.cta.maxLines} budget`}</span>
      </div>
      <SceneFrame scene={scene} />
    </article>
  );
}

export function SceneLabPageContent({
  scenePlanLinks = [],
}: {
  scenePlanLinks?: Array<{ href: string; label: string; summary: string }>;
}) {
  const heroScene = SCENES[0];

  return (
    <div style={pageStyle}>
      <section style={heroStyle}>
        <div style={heroCopyStyle}>
          <span style={previewBadgeStyle}>Renderer Pivot Lab</span>
          <h1
            style={{
              margin: 0,
              fontSize: "clamp(2.8rem, 5vw, 5.4rem)",
              lineHeight: 0.9,
              letterSpacing: "-0.08em",
              maxWidth: "8ch",
            }}
          >
            사진은 크게
            <br />
            카피는 짧게
            <br />
            규칙으로 고정합니다.
          </h1>
          <p style={{ margin: 0, maxWidth: "34ch", fontSize: 19, lineHeight: 1.72, color: "rgba(18,16,14,0.74)" }}>
            이제 장면 문구는 감으로 넣지 않고, `opening / review / closing`별 line budget과 type scale을 먼저 고정합니다. 레이아웃보다 카피가 길어서 망가지는 경우를
            코드에서 먼저 막는 단계입니다.
          </p>
        </div>

        <div style={heroPosterWrapStyle}>
          <SceneFrame scene={heroScene} />
        </div>
      </section>

      <section style={gridStyle}>
        {SCENES.map((scene) => (
          <ScenePreviewCard key={scene.id} scene={scene} />
        ))}
      </section>

      {scenePlanLinks.length > 0 ? (
        <section
          style={{
            display: "grid",
            gap: 12,
            paddingTop: 4,
          }}
        >
          <div style={{ display: "grid", gap: 6 }}>
            <span style={previewBadgeStyle}>Scene Plan Bridge</span>
            <h2 style={{ margin: 0, fontSize: "clamp(2rem, 3.2vw, 3rem)", lineHeight: 0.96, letterSpacing: "-0.05em" }}>
              실제 생성 `scenePlan`을
              <br />
              그대로 poster surface에 태웁니다.
            </h2>
          </div>
          <div style={{ display: "grid", gap: 10 }}>
            {scenePlanLinks.map((item) => (
              <a
                key={item.href}
                href={item.href}
                style={{
                  display: "grid",
                  gap: 4,
                  padding: "18px 20px",
                  borderRadius: 22,
                  background: "rgba(18,16,14,0.05)",
                  border: "1px solid rgba(18,16,14,0.08)",
                  color: "#12100e",
                  textDecoration: "none",
                }}
              >
                <strong style={{ fontSize: 18, lineHeight: 1.1, letterSpacing: "-0.03em" }}>{item.label}</strong>
                <span style={{ fontSize: 14, lineHeight: 1.5, color: "rgba(18,16,14,0.66)" }}>{item.summary}</span>
              </a>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}
