import { findCopyRule, type ProjectResultResponse, type Purpose } from "@/lib/contracts";

const LOCATION_POLICY_LABELS: Record<string, string> = {
  strict_all_surfaces: "모든 공개 surface 차단",
  public_copy_surfaces: "본문/캡션/해시태그 차단",
  distribution_surfaces: "배포 surface 차단",
};

const LOCATION_SURFACE_LABELS: Record<string, string> = {
  hookText: "hook",
  ctaText: "CTA",
  captions: "캡션",
  hashtags: "해시태그",
  sceneText: "scene text",
  subText: "sub text",
};

const QUICK_ACTION_LABELS: Record<string, string> = {
  highlightPrice: "가격 더 크게",
  shorterCopy: "문구 더 짧게",
  emphasizeRegion: "지역명 강조",
  styleOverride: "스타일 변경",
  templateId: "템플릿 변경",
};

type CopyPolicySummaryProps = {
  purpose: Purpose;
  templateId: string | null | undefined;
  detailLocation?: string | null;
  activePolicy?: ProjectResultResponse["copyPolicy"] | null;
  title?: string;
  description?: string;
};

function labelForLocationPolicy(policyId: string | undefined) {
  if (!policyId) return "상세 위치 정책 미연결";
  return LOCATION_POLICY_LABELS[policyId] ?? policyId;
}

function labelForSurface(surface: string) {
  return LOCATION_SURFACE_LABELS[surface] ?? surface;
}

function labelForQuickAction(action: string) {
  return QUICK_ACTION_LABELS[action] ?? action;
}

export function CopyPolicySummary({
  purpose,
  templateId,
  detailLocation,
  activePolicy,
  title = "카피 정책",
  description,
}: CopyPolicySummaryProps) {
  const copyRule = findCopyRule(templateId, purpose);

  if (!copyRule) return null;

  const locationPolicy = copyRule.locationPolicy;
  const forbiddenSurfaces = activePolicy?.forbiddenDetailLocationSurfaces ?? locationPolicy?.forbiddenDetailLocationSurfaces ?? [];
  const policyId = activePolicy?.detailLocationPolicyId ?? locationPolicy?.policyId;
  const locationLabel = detailLocation?.trim() ? `상세 위치 "${detailLocation.trim()}"` : "상세 위치";
  const supportsLocationGuard = forbiddenSurfaces.length > 0;
  const guardActive = activePolicy?.guardActive ?? Boolean(detailLocation?.trim() && supportsLocationGuard);
  const emphasizeRegionRequested = activePolicy?.emphasizeRegionRequested ?? false;
  const detailLocationPresent = activePolicy?.detailLocationPresent ?? Boolean(detailLocation?.trim());
  const supportsEmphasizeRegion = copyRule.supportedQuickActions?.includes("emphasizeRegion") ?? false;
  const guardStateLabel = guardActive ? "guard 활성" : "guard 비활성";

  return (
    <div
      style={{
        display: "grid",
        gap: 12,
        borderRadius: 18,
        border: "1px solid rgba(29,22,17,0.08)",
        padding: 16,
        background: "rgba(255,255,255,0.78)",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <strong>{title}</strong>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <span
            style={{
              padding: "6px 10px",
              borderRadius: 999,
              background: supportsLocationGuard ? "rgba(34,107,95,0.12)" : "rgba(29,22,17,0.08)",
              color: supportsLocationGuard ? "#226b5f" : "var(--muted)",
              fontWeight: 800,
              fontSize: ".78rem",
            }}
          >
            {labelForLocationPolicy(policyId)}
          </span>
          <span
            style={{
              padding: "6px 10px",
              borderRadius: 999,
              background: guardActive ? "rgba(34,107,95,0.12)" : "rgba(29,22,17,0.08)",
              color: guardActive ? "#226b5f" : "var(--muted)",
              fontWeight: 800,
              fontSize: ".78rem",
            }}
          >
            {guardStateLabel}
          </span>
        </div>
      </div>

      <div style={{ color: "var(--muted)", lineHeight: 1.6, fontSize: ".94rem" }}>
        {description ?? "template-spec copy-rule에 기록된 region budget과 상세 위치 금지 surface를 그대로 보여줍니다."}
      </div>

      <div style={{ display: "grid", gap: 8 }}>
        <div style={{ color: "var(--muted)", fontSize: ".9rem" }}>
          지역명은 최소 {copyRule.regionPolicy.minSlots}개 slot에 넣고 최대 {copyRule.regionPolicy.maxRepeat}회까지 반복합니다.
        </div>
        <div style={{ color: "var(--muted)", fontSize: ".9rem" }}>
          {supportsLocationGuard
            ? `${locationLabel}는 ${forbiddenSurfaces.map(labelForSurface).join(", ")}에서 금지합니다.`
            : `${locationLabel} 금지 surface는 아직 이 템플릿에 선언되지 않았습니다.`}
        </div>
        {activePolicy ? (
          <div style={{ color: "var(--muted)", fontSize: ".9rem" }}>
            {detailLocationPresent
              ? guardActive
                ? "현재 결과 payload 기준으로 상세 위치 guard가 활성화되어 있습니다."
                : "현재 결과 payload 기준으로 상세 위치 guard가 비활성화되어 있습니다."
              : "현재 결과 payload에는 상세 위치 입력이 없어 guard가 비활성화되어 있습니다."}
          </div>
        ) : null}
        {supportsEmphasizeRegion ? (
          <div style={{ color: "var(--muted)", fontSize: ".9rem" }}>
            {emphasizeRegionRequested
              ? "`지역명 강조` 요청이 있어도 상세 위치 금지 정책은 그대로 유지합니다."
              : "`지역명 강조` quick action은 regionName을 더 세게 쓰는 용도이며, 상세 위치 금지 정책 자체는 유지합니다."}
          </div>
        ) : null}
      </div>

      <div style={{ display: "grid", gap: 8 }}>
        <span style={{ fontSize: ".82rem", fontWeight: 800, color: "var(--muted)" }}>카피 구조</span>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {copyRule.structure.map((item) => (
            <span
              key={item}
              style={{
                padding: "6px 10px",
                borderRadius: 999,
                background: "rgba(246,239,230,0.88)",
                fontSize: ".84rem",
                fontWeight: 700,
              }}
            >
              {item}
            </span>
          ))}
        </div>
      </div>

      {supportsLocationGuard ? (
        <div style={{ display: "grid", gap: 8 }}>
          <span style={{ fontSize: ".82rem", fontWeight: 800, color: "var(--muted)" }}>상세 위치 금지 surface</span>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {forbiddenSurfaces.map((surface) => (
              <span
                key={surface}
                style={{
                  padding: "6px 10px",
                  borderRadius: 999,
                  background: "rgba(34,107,95,0.12)",
                  color: "#226b5f",
                  fontSize: ".84rem",
                  fontWeight: 700,
                }}
              >
                {labelForSurface(surface)}
              </span>
            ))}
          </div>
        </div>
      ) : null}

      {copyRule.supportedQuickActions?.length ? (
        <div style={{ display: "grid", gap: 8 }}>
          <span style={{ fontSize: ".82rem", fontWeight: 800, color: "var(--muted)" }}>허용 quick action</span>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {copyRule.supportedQuickActions.map((action) => (
              <span
                key={action}
                style={{
                  padding: "6px 10px",
                  borderRadius: 999,
                  background: "rgba(29,22,17,0.08)",
                  fontSize: ".84rem",
                  fontWeight: 700,
                }}
              >
                {labelForQuickAction(action)}
              </span>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
