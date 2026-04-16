import type { ProjectResultResponse } from "@/lib/contracts";

type ChangeImpactSummaryProps = {
  summary?: ProjectResultResponse["changeImpactSummary"] | null;
  title?: string;
  description?: string;
};

export function ChangeImpactSummary({
  summary,
  title = "이번 결과에서 바뀐 축",
  description = "현재 generation run 기준으로 어떤 quick action / change set이 어떤 층에 영향을 줬는지 요약합니다.",
}: ChangeImpactSummaryProps) {
  if (!summary) return null;

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
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          <span style={{ padding: "6px 10px", borderRadius: 999, background: "rgba(29,22,17,0.08)", fontSize: ".82rem", fontWeight: 800 }}>
            {summary.runType === "regenerate" ? "재생성" : "초기 생성"}
          </span>
          {summary.impactLayers.map((layer) => (
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
        {summary.activeActions.length ? (
          <div style={{ display: "grid", gap: 8 }}>
            {summary.activeActions.map((action) => (
              <div
                key={action.actionId}
                style={{
                  padding: 12,
                  borderRadius: 14,
                  background: "rgba(255,255,255,0.72)",
                  border: "1px solid rgba(29,22,17,0.08)",
                  display: "grid",
                  gap: 6,
                }}
              >
                <strong>{action.label}</strong>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {action.affectedLayers.map((layer) => (
                    <span key={`${action.actionId}-${layer}`} style={{ padding: "4px 8px", borderRadius: 999, background: "rgba(29,22,17,0.08)", fontSize: ".78rem", fontWeight: 800 }}>
                      {layer.toUpperCase()}
                    </span>
                  ))}
                </div>
                <span style={{ color: "var(--muted)", fontSize: ".92rem", lineHeight: 1.5 }}>{action.note}</span>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ color: "var(--muted)", fontSize: ".92rem", lineHeight: 1.55 }}>이번 결과는 별도 quick action 없이 기본 생성 기준으로 만들어졌습니다.</div>
        )}
      </div>
    </section>
  );
}
