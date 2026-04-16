import type { ProjectResultResponse } from "@/lib/contracts";

type ScenePlanPreviewMeta = {
  url: string;
  sceneCount?: number | null;
  sceneSpecVersion?: string | null;
};

export function ScenePlanPreviewLinks({
  projectId,
  scenePlan,
  sceneLayerSummary = null,
  activePolicy = null,
  changeImpactSummary = null,
  title = "scenePlan 확인",
  description = "현재 프로젝트 결과의 scenePlan을 opening/closing scene으로 바로 확인합니다.",
}: {
  projectId: string;
  scenePlan: ScenePlanPreviewMeta;
  sceneLayerSummary?: ProjectResultResponse["sceneLayerSummary"] | null;
  activePolicy?: ProjectResultResponse["copyPolicy"] | null;
  changeImpactSummary?: ProjectResultResponse["changeImpactSummary"] | null;
  title?: string;
  description?: string;
}) {
  const closingSceneId = `s${scenePlan.sceneCount ?? 1}`;
  const guardLabel = activePolicy?.guardActive ? "guard 활성" : "guard 비활성";
  const policyLabel = activePolicy?.detailLocationPolicyId ?? "상세 위치 정책 미표기";
  const forbiddenSurfaces = activePolicy?.forbiddenDetailLocationSurfaces ?? [];
  const openingHref = `/scene-frame/s1?projectId=${projectId}`;
  const openingCleanHref = `/scene-frame/s1?projectId=${projectId}&clean=1`;
  const closingHref = `/scene-frame/${closingSceneId}?projectId=${projectId}`;
  const closingCleanHref = `/scene-frame/${closingSceneId}?projectId=${projectId}&clean=1`;

  return (
    <section style={{ display: "grid", gap: 12 }}>
      <strong>{title}</strong>
      <div
        style={{
          borderRadius: 18,
          border: "1px solid rgba(29,22,17,0.08)",
          padding: 16,
          background: "rgba(255,255,255,0.8)",
          display: "grid",
          gap: 12,
        }}
      >
        <div style={{ color: "var(--muted)", lineHeight: 1.55 }}>{description}</div>
        {activePolicy ? (
          <div style={{ display: "grid", gap: 8 }}>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              <span
                style={{
                  padding: "6px 10px",
                  borderRadius: 999,
                  background: "rgba(34,107,95,0.12)",
                  color: "#226b5f",
                  fontSize: ".82rem",
                  fontWeight: 800,
                }}
              >
                {policyLabel}
              </span>
              <span
                style={{
                  padding: "6px 10px",
                  borderRadius: 999,
                  background: activePolicy.guardActive ? "rgba(34,107,95,0.12)" : "rgba(29,22,17,0.08)",
                  color: activePolicy.guardActive ? "#226b5f" : "var(--muted)",
                  fontSize: ".82rem",
                  fontWeight: 800,
                }}
              >
                {guardLabel}
              </span>
            </div>
            <div style={{ color: "var(--muted)", fontSize: ".9rem", lineHeight: 1.55 }}>
              {activePolicy.detailLocationPresent
                ? activePolicy.guardActive
                  ? `scene preview를 열기 전에도 상세 위치 guard가 활성화된 상태임을 확인할 수 있습니다. 금지 surface: ${forbiddenSurfaces.join(", ") || "미표기"}`
                  : "scene preview를 열기 전 기준으로 상세 위치 guard가 비활성화된 상태입니다."
                : "현재 결과 payload에는 상세 위치 입력이 없어 scene preview 기준 guard가 비활성화되어 있습니다."}
            </div>
            {activePolicy.emphasizeRegionRequested ? (
              <div style={{ color: "var(--muted)", fontSize: ".9rem", lineHeight: 1.55 }}>
                `지역명 강조` 요청이 있어도 scene preview 기준 detail location guard는 그대로 유지합니다.
              </div>
            ) : null}
          </div>
        ) : null}
        {sceneLayerSummary?.items?.length ? (
          <div style={{ display: "grid", gap: 8 }}>
            <span style={{ fontSize: ".82rem", fontWeight: 800, color: "var(--muted)" }}>scene layer map</span>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              {sceneLayerSummary.items.map((item) => (
                <span
                  key={`${item.sceneId}-${item.textRole}`}
                  style={{
                    padding: "6px 10px",
                    borderRadius: 999,
                    background:
                      item.slotGroup === "hook"
                        ? "rgba(229,106,76,0.12)"
                        : item.slotGroup === "cta"
                          ? "rgba(34,107,95,0.12)"
                          : "rgba(29,22,17,0.08)",
                    color:
                      item.slotGroup === "hook"
                        ? "#c25337"
                        : item.slotGroup === "cta"
                          ? "#226b5f"
                          : "var(--text)",
                    fontSize: ".82rem",
                    fontWeight: 800,
                  }}
                >
                  {item.sceneId} · {item.slotGroup.toUpperCase()} · {item.uiLabel}
                </span>
              ))}
            </div>
          </div>
        ) : null}
        {changeImpactSummary ? (
          <div style={{ display: "grid", gap: 8 }}>
            <span style={{ fontSize: ".82rem", fontWeight: 800, color: "var(--muted)" }}>최근 변경 영향</span>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              <span
                style={{
                  padding: "6px 10px",
                  borderRadius: 999,
                  background: "rgba(29,22,17,0.08)",
                  fontSize: ".82rem",
                  fontWeight: 800,
                }}
              >
                {changeImpactSummary.runType === "regenerate" ? "재생성" : "초기 생성"}
              </span>
              {changeImpactSummary.impactLayers.map((layer) => (
                <span
                  key={layer}
                  style={{
                    padding: "6px 10px",
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
                    fontSize: ".82rem",
                    fontWeight: 800,
                  }}
                >
                  {layer.toUpperCase()}
                </span>
              ))}
            </div>
            <div style={{ color: "var(--muted)", fontSize: ".9rem", lineHeight: 1.55 }}>
              {changeImpactSummary.activeActions.length
                ? `scene preview를 열기 전 기준으로 ${changeImpactSummary.activeActions.map((action) => action.label).join(", ")} 변경이 현재 결과에 반영되어 있습니다.`
                : "scene preview를 열기 전 기준으로 이번 결과는 별도 quick action 없이 기본 생성 상태입니다."}
            </div>
            {changeImpactSummary.activeActions.length ? (
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                {changeImpactSummary.activeActions.map((action) => (
                  <span
                    key={action.actionId}
                    style={{
                      padding: "6px 10px",
                      borderRadius: 999,
                      background: "rgba(255,255,255,0.9)",
                      border: "1px solid rgba(29,22,17,0.08)",
                      fontSize: ".82rem",
                      fontWeight: 800,
                    }}
                  >
                    {action.label}
                  </span>
                ))}
              </div>
            ) : null}
          </div>
        ) : null}
        <div style={{ display: "grid", gap: 10 }}>
          <div style={{ display: "grid", gap: 6 }}>
            <strong style={{ fontSize: ".88rem" }}>오프닝 씬</strong>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
              <a className="button button-secondary" href={openingHref}>
                일반 보기
              </a>
              <a className="button button-ghost" href={openingCleanHref}>
                clean mode
              </a>
            </div>
          </div>
          <div style={{ display: "grid", gap: 6 }}>
            <strong style={{ fontSize: ".88rem" }}>마감 씬</strong>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
              <a className="button button-secondary" href={closingHref}>
                일반 보기
              </a>
              <a className="button button-ghost" href={closingCleanHref}>
                clean mode
              </a>
            </div>
          </div>
        </div>
        <div style={{ fontSize: ".88rem", color: "var(--muted)" }}>
          {scenePlan.sceneCount ?? 0}개 scene · {scenePlan.sceneSpecVersion ?? "sceneSpec 미표기"}
        </div>
      </div>
    </section>
  );
}
