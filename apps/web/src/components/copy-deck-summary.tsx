import type { ProjectResultResponse } from "@/lib/contracts";

type CopyDeckSummaryProps = {
  copyDeck?: ProjectResultResponse["copyDeck"] | null;
  title?: string;
  description?: string;
};

export function CopyDeckSummary({
  copyDeck,
  title = "hook / body / cta 구조",
  description = "현재 결과를 템플릿 기반 copy deck 관점으로 다시 읽어, 어떤 문장이 hook/body/cta를 담당하는지 바로 확인합니다.",
}: CopyDeckSummaryProps) {
  if (!copyDeck) return null;

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
          gap: 14,
        }}
      >
        <div style={{ color: "var(--muted)", lineHeight: 1.55 }}>{description}</div>
        <div style={{ display: "grid", gap: 10 }}>
          <span style={{ fontSize: ".82rem", fontWeight: 800, color: "var(--muted)" }}>HOOK</span>
          <div style={{ padding: 12, borderRadius: 14, background: "rgba(246,239,230,0.72)", display: "grid", gap: 6 }}>
            <strong style={{ lineHeight: 1.45 }}>{copyDeck.hook.primaryLine}</strong>
            {copyDeck.hook.supportLine ? <span style={{ color: "var(--muted)", fontSize: ".92rem" }}>{copyDeck.hook.supportLine}</span> : null}
          </div>
        </div>
        <div style={{ display: "grid", gap: 10 }}>
          <span style={{ fontSize: ".82rem", fontWeight: 800, color: "var(--muted)" }}>BODY</span>
          <div style={{ display: "grid", gap: 8 }}>
            {copyDeck.body.blocks.map((block) => (
              <div
                key={block.blockId}
                style={{
                  padding: 12,
                  borderRadius: 14,
                  background: "rgba(255,255,255,0.74)",
                  border: "1px solid rgba(29,22,17,0.08)",
                  display: "grid",
                  gap: 6,
                }}
              >
                <span style={{ fontSize: ".8rem", fontWeight: 800, color: "var(--muted)" }}>{block.uiLabel}</span>
                <strong style={{ lineHeight: 1.45 }}>{block.primaryLine || "미기입"}</strong>
                {block.supportLine ? <span style={{ color: "var(--muted)", fontSize: ".92rem" }}>{block.supportLine}</span> : null}
              </div>
            ))}
          </div>
        </div>
        <div style={{ display: "grid", gap: 10 }}>
          <span style={{ fontSize: ".82rem", fontWeight: 800, color: "var(--muted)" }}>CTA</span>
          <div style={{ padding: 12, borderRadius: 14, background: "rgba(34,107,95,0.1)", display: "grid", gap: 6 }}>
            <strong style={{ lineHeight: 1.45 }}>{copyDeck.cta.primaryLine}</strong>
          </div>
        </div>
      </div>
    </section>
  );
}
