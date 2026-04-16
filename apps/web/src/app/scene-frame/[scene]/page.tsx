import { SceneFrame, getSceneById } from "@/components/scene-lab";
import { sceneSpecsFromScenePlan } from "@/components/scene-lab";
import { loadProjectScenePlan, loadScenePlanArtifact } from "@/lib/scene-plan";
import { headers } from "next/headers";
import { notFound } from "next/navigation";

export default async function SceneFramePage({
  params,
  searchParams,
}: {
  params: Promise<{ scene: string }>;
  searchParams: Promise<{ artifact?: string; projectId?: string; clean?: string }>;
}) {
  const { scene: sceneId } = await params;
  const { artifact, projectId, clean } = await searchParams;

  let scene = getSceneById(sceneId);
  let activeCopyPolicy:
    | {
        detailLocationPolicyId: string | null;
        forbiddenDetailLocationSurfaces: string[];
        guardActive: boolean;
        emphasizeRegionRequested: boolean;
        detailLocationPresent: boolean;
      }
    | null = null;
  let currentSceneLayer:
    | {
        sceneId: string;
        slotGroup: "hook" | "body" | "cta";
        textRole: string;
        uiLabel: string;
      }
    | null = null;
  if (projectId) {
    const headerStore = await headers();
    const host = headerStore.get("x-forwarded-host") ?? headerStore.get("host");
    const protocol = headerStore.get("x-forwarded-proto") ?? "http";
    if (!host) {
      notFound();
    }
    const loaded = await loadProjectScenePlan(projectId, `${protocol}://${host}`);
    if (!loaded) {
      notFound();
    }
    const projectScenes = sceneSpecsFromScenePlan(loaded.scenePlan, { assetBaseUrl: loaded.apiBaseUrl });
    scene = getSceneById(sceneId, projectScenes);
    activeCopyPolicy = loaded.copyPolicy;
    currentSceneLayer = loaded.sceneLayerSummary?.items.find((item) => item.sceneId === sceneId) ?? null;
  } else if (artifact) {
    const loaded = await loadScenePlanArtifact(artifact);
    if (!loaded) {
      notFound();
    }
    const artifactScenes = sceneSpecsFromScenePlan(loaded.scenePlan);
    scene = getSceneById(sceneId, artifactScenes);
  }

  if (!scene) {
    notFound();
  }

  const showPolicyOverlay = Boolean(activeCopyPolicy) && clean !== "1";

  return (
    <main
      style={{
        minHeight: "100svh",
        background: "#080706",
        display: "grid",
        gap: 16,
        padding: "18px 16px 24px",
      }}
    >
      {activeCopyPolicy ? (
        <section
          style={{
            width: "min(1080px, 100%)",
            margin: "0 auto",
            borderRadius: 18,
            border: "1px solid rgba(255,255,255,0.08)",
            background: "rgba(14,12,11,0.92)",
            color: "#fff7ef",
            padding: 16,
            display: "grid",
            gap: 10,
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
            <strong style={{ fontSize: "0.96rem" }}>scene-frame 기준 active copy policy</strong>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <span
                style={{
                  padding: "6px 10px",
                  borderRadius: 999,
                  background: "rgba(229,255,57,0.12)",
                  color: "#e5ff39",
                  fontSize: ".8rem",
                  fontWeight: 800,
                }}
              >
                {activeCopyPolicy.detailLocationPolicyId ?? "상세 위치 정책 미표기"}
              </span>
              <span
                style={{
                  padding: "6px 10px",
                  borderRadius: 999,
                  background: activeCopyPolicy.guardActive ? "rgba(123,245,255,0.12)" : "rgba(255,255,255,0.08)",
                  color: activeCopyPolicy.guardActive ? "#7bf5ff" : "rgba(255,247,239,0.72)",
                  fontSize: ".8rem",
                  fontWeight: 800,
                }}
              >
                {activeCopyPolicy.guardActive ? "guard 활성" : "guard 비활성"}
              </span>
            </div>
          </div>
          <div style={{ color: "rgba(255,247,239,0.74)", lineHeight: 1.55, fontSize: ".92rem" }}>
            {activeCopyPolicy.detailLocationPresent
              ? activeCopyPolicy.guardActive
                ? `현재 scene-frame은 상세 위치 guard가 활성화된 결과를 기준으로 열렸습니다. 금지 surface: ${activeCopyPolicy.forbiddenDetailLocationSurfaces.join(", ") || "미표기"}`
                : "현재 scene-frame은 상세 위치 입력은 있었지만 guard가 비활성화된 결과를 기준으로 열렸습니다."
              : "현재 scene-frame은 상세 위치 입력이 없는 결과를 기준으로 열렸습니다."}
          </div>
          <div style={{ color: "rgba(255,247,239,0.62)", lineHeight: 1.5, fontSize: ".86rem" }}>
            {showPolicyOverlay
              ? "현재는 프레임 안쪽에도 compact policy overlay를 함께 표시합니다. 깔끔한 프레임만 보려면 URL 뒤에 `&clean=1`을 붙이시면 됩니다."
              : "현재는 clean mode로 열려 프레임 안쪽 policy overlay를 숨긴 상태입니다."}
          </div>
          {activeCopyPolicy.emphasizeRegionRequested ? (
            <div style={{ color: "rgba(255,247,239,0.74)", lineHeight: 1.55, fontSize: ".92rem" }}>
              `지역명 강조` 요청이 있어도 scene-frame 기준 detail location guard는 그대로 유지됩니다.
            </div>
          ) : null}
        </section>
      ) : null}
      <section
        style={{
          width: "min(1080px, 100%)",
          margin: "0 auto",
          position: "relative",
        }}
      >
        {showPolicyOverlay ? (
          <aside
            style={{
              position: "absolute",
              top: 18,
              left: 18,
              zIndex: 20,
              maxWidth: 360,
              pointerEvents: "none",
              display: "grid",
              gap: 8,
            }}
          >
            <div
              style={{
                display: "inline-flex",
                gap: 8,
                flexWrap: "wrap",
              }}
            >
              <span
                style={{
                  padding: "7px 12px",
                  borderRadius: 999,
                  background: "rgba(14,12,11,0.84)",
                  border: "1px solid rgba(255,255,255,0.08)",
                  color: "#e5ff39",
                  fontSize: ".78rem",
                  fontWeight: 900,
                  letterSpacing: "0.04em",
                  backdropFilter: "blur(12px)",
                }}
              >
                {activeCopyPolicy?.detailLocationPolicyId ?? "상세 위치 정책 미표기"}
              </span>
              <span
                style={{
                  padding: "7px 12px",
                  borderRadius: 999,
                  background: "rgba(14,12,11,0.84)",
                  border: "1px solid rgba(255,255,255,0.08)",
                  color: activeCopyPolicy?.guardActive ? "#7bf5ff" : "rgba(255,247,239,0.74)",
                  fontSize: ".78rem",
                  fontWeight: 900,
                  letterSpacing: "0.04em",
                  backdropFilter: "blur(12px)",
                }}
              >
                {activeCopyPolicy?.guardActive ? "guard 활성" : "guard 비활성"}
              </span>
              {activeCopyPolicy?.emphasizeRegionRequested ? (
                <span
                  style={{
                    padding: "7px 12px",
                    borderRadius: 999,
                    background: "rgba(14,12,11,0.84)",
                    border: "1px solid rgba(255,255,255,0.08)",
                    color: "#fff7ef",
                    fontSize: ".78rem",
                    fontWeight: 900,
                    letterSpacing: "0.04em",
                    backdropFilter: "blur(12px)",
                  }}
                >
                  지역명 강조 요청
                </span>
              ) : null}
              {currentSceneLayer ? (
                <span
                  style={{
                    padding: "7px 12px",
                    borderRadius: 999,
                    background: "rgba(14,12,11,0.84)",
                    border: "1px solid rgba(255,255,255,0.08)",
                    color: "#fff7ef",
                    fontSize: ".78rem",
                    fontWeight: 900,
                    letterSpacing: "0.04em",
                    backdropFilter: "blur(12px)",
                  }}
                >
                  {currentSceneLayer.sceneId} · {currentSceneLayer.slotGroup.toUpperCase()} · {currentSceneLayer.uiLabel}
                </span>
              ) : null}
            </div>
            <div
              style={{
                padding: "12px 14px",
                borderRadius: 18,
                background: "rgba(14,12,11,0.72)",
                border: "1px solid rgba(255,255,255,0.08)",
                color: "rgba(255,247,239,0.78)",
                fontSize: ".84rem",
                lineHeight: 1.5,
                backdropFilter: "blur(12px)",
                boxShadow: "0 18px 42px rgba(0,0,0,0.22)",
              }}
            >
              {activeCopyPolicy?.detailLocationPresent
                ? `금지 surface: ${activeCopyPolicy?.forbiddenDetailLocationSurfaces.join(", ") || "미표기"}`
                : "상세 위치 입력 없음"}
            </div>
          </aside>
        ) : null}
        <SceneFrame scene={scene} captureMode />
      </section>
    </main>
  );
}
