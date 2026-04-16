import type { ProjectResultResponse, QuickOptions } from "@/lib/contracts";

type PromptBaselineSummaryProps = {
  summary?: ProjectResultResponse["promptBaselineSummary"] | null;
  title?: string;
  description?: string;
};

function quickOptionLabel(key: string, value: boolean | undefined) {
  const label =
    key === "highlightPrice"
      ? "가격 강조"
      : key === "shorterCopy"
        ? "짧은 문구"
        : key === "emphasizeRegion"
          ? "지역명 강조"
          : key;
  return `${label} ${value ? "on" : "off"}`;
}

function formatQuickOptions(options: QuickOptions | Record<string, boolean | undefined>) {
  return Object.entries(options as Record<string, boolean | undefined>).map(([key, value]) => quickOptionLabel(key, value));
}

function formatExperimentIds(ids: string[]) {
  return ids.length ? ids.join(", ") : "미기록";
}

function executionStatusLabel(status: NonNullable<NonNullable<ProjectResultResponse["promptBaselineSummary"]>["executionHint"]>["status"]) {
  if (status === "default_match") return "main baseline match";
  if (status === "option_match") return "option profile match";
  return "coverage gap";
}

function policyStateLabel(state: NonNullable<NonNullable<ProjectResultResponse["promptBaselineSummary"]>["policyHint"]>["policyState"]) {
  if (state === "main_reference") return "main reference";
  if (state === "option_reference") return "option reference";
  return "manual review";
}

function coverageKindLabel(kind: NonNullable<NonNullable<ProjectResultResponse["promptBaselineSummary"]>["coverageHint"]>["nearestProfileKind"]) {
  if (kind === "default") return "main baseline";
  if (kind === "option") return "option profile";
  return "미기록";
}

function coverageGapClassLabel(gapClass: NonNullable<NonNullable<ProjectResultResponse["promptBaselineSummary"]>["coverageHint"]>["gapClass"]) {
  if (gapClass === "quick_option_gap") return "quick option gap";
  if (gapClass === "scenario_gap") return "scenario gap";
  return "mixed gap";
}

function PromptBaselineProfileCard({
  profile,
  tone,
  label,
}: {
  profile: NonNullable<NonNullable<ProjectResultResponse["promptBaselineSummary"]>["defaultProfile"]>;
  tone: "neutral" | "good";
  label: string;
}) {
  const toneStyles =
    tone === "good"
      ? { background: "rgba(34,107,95,0.1)", borderColor: "rgba(34,107,95,0.18)", badgeBg: "rgba(34,107,95,0.14)", badgeColor: "#226b5f" }
      : { background: "rgba(255,255,255,0.74)", borderColor: "rgba(29,22,17,0.08)", badgeBg: "rgba(29,22,17,0.08)", badgeColor: "var(--muted)" };

  return (
    <div
      style={{
        padding: 14,
        borderRadius: 16,
        border: `1px solid ${toneStyles.borderColor}`,
        background: toneStyles.background,
        display: "grid",
        gap: 8,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
        <strong>{label}</strong>
        <span
          style={{
            padding: "6px 10px",
            borderRadius: 999,
            background: toneStyles.badgeBg,
            color: toneStyles.badgeColor,
            fontWeight: 800,
            fontSize: ".78rem",
          }}
        >
          {profile.label}
        </span>
      </div>
      <div style={{ color: "var(--muted)", fontSize: ".92rem", lineHeight: 1.55 }}>
        {profile.model.provider} · {profile.model.modelName} · {profile.model.role}
      </div>
      <div style={{ color: "var(--muted)", fontSize: ".9rem", lineHeight: 1.55 }}>
        {profile.purpose} / {profile.templateId} / {profile.styleId}
      </div>
      <div style={{ color: "var(--muted)", fontSize: ".9rem", lineHeight: 1.55 }}>
        조건 quick action: {formatQuickOptions(profile.scenarioQuickOptions).join(", ")}
      </div>
      <div style={{ color: "var(--muted)", fontSize: ".9rem", lineHeight: 1.55 }}>
        preset: {profile.promptPresetId ?? "미기록"} / location policy: {profile.locationPolicyId ?? "미기록"}
      </div>
      <div style={{ color: "var(--muted)", fontSize: ".9rem", lineHeight: 1.55 }}>
        evidence: {formatExperimentIds(profile.evidenceExperimentIds)}
        {profile.snapshotExperimentId ? ` / snapshot: ${profile.snapshotExperimentId}` : ""}
      </div>
      {profile.usageGuidance.length ? (
        <div style={{ display: "grid", gap: 6 }}>
          {profile.usageGuidance.slice(0, 2).map((item) => (
            <div key={item} style={{ color: "var(--muted)", fontSize: ".9rem", lineHeight: 1.5 }}>
              {item}
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}

function PolicyHintCard({
  hint,
}: {
  hint: NonNullable<NonNullable<ProjectResultResponse["promptBaselineSummary"]>["policyHint"]>;
}) {
  const toneStyles =
    hint.policyState === "coverage_gap"
      ? { background: "rgba(246,239,230,0.74)", borderColor: "rgba(177,126,87,0.18)", badgeBg: "rgba(177,126,87,0.12)", badgeColor: "#8a5b35" }
      : hint.policyState === "option_reference"
        ? { background: "rgba(34,107,95,0.08)", borderColor: "rgba(34,107,95,0.18)", badgeBg: "rgba(34,107,95,0.14)", badgeColor: "#226b5f" }
        : { background: "rgba(255,255,255,0.74)", borderColor: "rgba(29,22,17,0.08)", badgeBg: "rgba(29,22,17,0.08)", badgeColor: "var(--muted)" };

  return (
    <div
      style={{
        padding: 14,
        borderRadius: 16,
        border: `1px solid ${toneStyles.borderColor}`,
        background: toneStyles.background,
        display: "grid",
        gap: 8,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
        <strong>정책 힌트</strong>
        <span
          style={{
            padding: "6px 10px",
            borderRadius: 999,
            background: toneStyles.badgeBg,
            color: toneStyles.badgeColor,
            fontWeight: 800,
            fontSize: ".78rem",
          }}
        >
          {policyStateLabel(hint.policyState)}
        </span>
      </div>
      <div style={{ color: "var(--text)", lineHeight: 1.55 }}>{hint.summary}</div>
      <div style={{ color: "var(--muted)", fontSize: ".92rem", lineHeight: 1.55 }}>
        action: {hint.recommendedAction}
        {hint.requiresManualReview ? " / manual review required" : " / manual review optional"}
      </div>
      {hint.recommendedProfileId ? (
        <div style={{ color: "var(--muted)", fontSize: ".9rem", lineHeight: 1.55 }}>
          profile: {hint.recommendedProfileId}
          {hint.recommendedModel ? ` / ${hint.recommendedModel.provider} · ${hint.recommendedModel.modelName}` : ""}
        </div>
      ) : null}
      {hint.transportRecommendation ? (
        <div style={{ color: "var(--muted)", fontSize: ".9rem", lineHeight: 1.55 }}>
          transport: {hint.transportRecommendation.mode}
          {hint.transportRecommendation.fallbackProfileId ? ` / fallback=${hint.transportRecommendation.fallbackProfileId}` : ""}
          {hint.transportRecommendation.trigger ? ` / trigger=${hint.transportRecommendation.trigger}` : ""}
        </div>
      ) : null}
    </div>
  );
}

function ExecutionHintCard({
  hint,
}: {
  hint: NonNullable<NonNullable<ProjectResultResponse["promptBaselineSummary"]>["executionHint"]>;
}) {
  const statusStyles =
    hint.status === "coverage_gap"
      ? { background: "rgba(246,239,230,0.74)", borderColor: "rgba(177,126,87,0.18)", badgeBg: "rgba(177,126,87,0.12)", badgeColor: "#8a5b35" }
      : hint.status === "option_match"
        ? { background: "rgba(34,107,95,0.08)", borderColor: "rgba(34,107,95,0.18)", badgeBg: "rgba(34,107,95,0.14)", badgeColor: "#226b5f" }
        : { background: "rgba(255,255,255,0.74)", borderColor: "rgba(29,22,17,0.08)", badgeBg: "rgba(29,22,17,0.08)", badgeColor: "var(--muted)" };

  return (
    <div
      style={{
        padding: 14,
        borderRadius: 16,
        border: `1px solid ${statusStyles.borderColor}`,
        background: statusStyles.background,
        display: "grid",
        gap: 8,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
        <strong>실행 권장</strong>
        <span
          style={{
            padding: "6px 10px",
            borderRadius: 999,
            background: statusStyles.badgeBg,
            color: statusStyles.badgeColor,
            fontWeight: 800,
            fontSize: ".78rem",
          }}
        >
          {executionStatusLabel(hint.status)}
        </span>
      </div>
      <div style={{ color: "var(--text)", lineHeight: 1.55 }}>{hint.summary}</div>
      {hint.recommendedProfileId ? (
        <div style={{ color: "var(--muted)", fontSize: ".92rem", lineHeight: 1.55 }}>
          권장 profile: {hint.recommendedProfileId}
          {hint.recommendedModel ? ` / ${hint.recommendedModel.provider} · ${hint.recommendedModel.modelName}` : ""}
        </div>
      ) : null}
      {hint.transportRecommendation ? (
        <div style={{ color: "var(--muted)", fontSize: ".9rem", lineHeight: 1.55 }}>
          transport guard: {hint.transportRecommendation.mode}
          {hint.transportRecommendation.defaultProfileId ? ` / default=${hint.transportRecommendation.defaultProfileId}` : ""}
          {hint.transportRecommendation.fallbackProfileId ? ` / fallback=${hint.transportRecommendation.fallbackProfileId}` : ""}
          {hint.transportRecommendation.trigger ? ` / trigger=${hint.transportRecommendation.trigger}` : ""}
          {hint.transportRecommendation.sourceExperimentId ? ` / evidence=${hint.transportRecommendation.sourceExperimentId}` : ""}
        </div>
      ) : null}
      {hint.notes.length ? (
        <div style={{ display: "grid", gap: 6 }}>
          {hint.notes.slice(0, 3).map((item) => (
            <div key={item} style={{ color: "var(--muted)", fontSize: ".9rem", lineHeight: 1.5 }}>
              {item}
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}

function CoverageHintCard({
  hint,
}: {
  hint: NonNullable<NonNullable<ProjectResultResponse["promptBaselineSummary"]>["coverageHint"]>;
}) {
  return (
    <div
      style={{
        padding: 14,
        borderRadius: 16,
        border: "1px solid rgba(177,126,87,0.18)",
        background: "rgba(246,239,230,0.74)",
        display: "grid",
        gap: 8,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
        <strong>coverage gap 진단</strong>
        <span
          style={{
            padding: "6px 10px",
            borderRadius: 999,
            background: "rgba(177,126,87,0.12)",
            color: "#8a5b35",
            fontWeight: 800,
            fontSize: ".78rem",
          }}
        >
          nearest profile
        </span>
      </div>
      <div style={{ color: "var(--text)", lineHeight: 1.55 }}>{hint.summary}</div>
      <div style={{ color: "var(--muted)", fontSize: ".92rem", lineHeight: 1.55 }}>
        class: {coverageGapClassLabel(hint.gapClass)} / action: {hint.recommendedAction}
      </div>
      {hint.nearestProfileId ? (
        <div style={{ color: "var(--muted)", fontSize: ".92rem", lineHeight: 1.55 }}>
          nearest: {hint.nearestProfileId} / {coverageKindLabel(hint.nearestProfileKind)}
        </div>
      ) : null}
      {hint.mismatchDimensions.length ? (
        <div style={{ display: "grid", gap: 6 }}>
          {hint.mismatchDimensions.slice(0, 4).map((item) => (
            <div key={item} style={{ color: "var(--muted)", fontSize: ".9rem", lineHeight: 1.5 }}>
              mismatch: {item}
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}

function OperationalCheckCard({
  check,
}: {
  check: NonNullable<ProjectResultResponse["promptBaselineSummary"]>["operationalChecks"][number];
}) {
  return (
    <div
      style={{
        padding: 12,
        borderRadius: 14,
        border: "1px solid rgba(29,22,17,0.08)",
        background: "rgba(255,255,255,0.7)",
        display: "grid",
        gap: 6,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
        <strong>{check.experimentId || "운영 체크"}</strong>
        <span
          style={{
            padding: "5px 9px",
            borderRadius: 999,
            background: check.appliesToRecommendedModel ? "rgba(34,107,95,0.12)" : "rgba(29,22,17,0.08)",
            color: check.appliesToRecommendedModel ? "#226b5f" : "var(--muted)",
            fontWeight: 800,
            fontSize: ".76rem",
          }}
        >
          {check.appliesToRecommendedModel ? "권장 모델 관련" : "참고 메모"}
        </span>
      </div>
      <div style={{ color: "var(--muted)", fontSize: ".9rem", lineHeight: 1.55 }}>
        {check.targetTemplateId ?? "전체"} / {check.result || "미기록"}
        {check.model ? ` / ${check.model.provider} · ${check.model.modelName}` : ""}
      </div>
      {check.transportRecommendation ? (
        <div style={{ color: "var(--muted)", fontSize: ".88rem", lineHeight: 1.55 }}>
          transport: {check.transportRecommendation.mode}
          {check.transportRecommendation.defaultProfileId ? ` / default=${check.transportRecommendation.defaultProfileId}` : ""}
          {check.transportRecommendation.fallbackProfileId ? ` / fallback=${check.transportRecommendation.fallbackProfileId}` : ""}
        </div>
      ) : null}
      {check.notes.slice(0, 2).map((item) => (
        <div key={item} style={{ color: "var(--muted)", fontSize: ".88rem", lineHeight: 1.5 }}>
          {item}
        </div>
      ))}
    </div>
  );
}

export function PromptBaselineSummary({
  summary,
  title = "prompt baseline 정렬",
  description = "현재 결과를 prompt 연구선 기준 manifest와 대조해, 어떤 main/fallback profile이 권장되는지 추천 메타데이터로만 보여줍니다.",
}: PromptBaselineSummaryProps) {
  if (!summary) return null;

  const extraCandidates = summary.candidateProfiles.filter(
    (profile) => !summary.recommendedProfile || profile.profileId !== summary.recommendedProfile.profileId,
  );
  const applicableOperationalChecks = summary.operationalChecks.filter((check) => check.applicable || check.appliesToRecommendedModel);

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
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
          <div style={{ color: "var(--muted)", lineHeight: 1.55 }}>{description}</div>
          <span
            style={{
              padding: "6px 10px",
              borderRadius: 999,
              background: "rgba(29,22,17,0.08)",
              color: "var(--muted)",
              fontWeight: 800,
              fontSize: ".78rem",
            }}
          >
            {summary.baselineId} · 추천 전용
          </span>
        </div>

        <div style={{ color: "var(--muted)", fontSize: ".92rem", lineHeight: 1.6 }}>
          현재 결과 컨텍스트: {summary.context.purpose} / {summary.context.templateId} / {summary.context.styleId} /{" "}
          {formatQuickOptions(summary.context.quickOptions).join(", ")}
        </div>

        {summary.policyHint ? <PolicyHintCard hint={summary.policyHint} /> : null}
        {summary.executionHint ? <ExecutionHintCard hint={summary.executionHint} /> : null}
        {summary.coverageHint ? <CoverageHintCard hint={summary.coverageHint} /> : null}

        {summary.defaultProfile ? (
          <PromptBaselineProfileCard profile={summary.defaultProfile} tone="neutral" label="기본 baseline" />
        ) : null}

        {summary.recommendedProfile ? (
          <PromptBaselineProfileCard profile={summary.recommendedProfile} tone="good" label="현재 결과 권장 profile" />
        ) : (
          <div
            style={{
              padding: 14,
              borderRadius: 16,
              background: "rgba(246,239,230,0.74)",
              color: "var(--muted)",
              lineHeight: 1.6,
            }}
          >
            현재 결과 컨텍스트와 exact match되는 prompt baseline profile은 아직 없습니다.
          </div>
        )}

        {extraCandidates.length ? (
          <div style={{ display: "grid", gap: 8 }}>
            <span style={{ fontSize: ".82rem", fontWeight: 800, color: "var(--muted)" }}>등록된 option profile</span>
            <div style={{ display: "grid", gap: 8 }}>
              {extraCandidates.map((profile) => (
                <PromptBaselineProfileCard
                  key={profile.profileId}
                  profile={profile}
                  tone={profile.applicable ? "good" : "neutral"}
                  label={profile.applicable ? "현재 컨텍스트와 일치하는 option" : "조건부 option"}
                />
              ))}
            </div>
          </div>
        ) : null}

        {applicableOperationalChecks.length ? (
          <div style={{ display: "grid", gap: 8 }}>
            <span style={{ fontSize: ".82rem", fontWeight: 800, color: "var(--muted)" }}>적용 가능한 운영 메모</span>
            <div style={{ display: "grid", gap: 8 }}>
              {applicableOperationalChecks.map((check) => (
                <OperationalCheckCard key={`${check.experimentId}-${check.result}`} check={check} />
              ))}
            </div>
          </div>
        ) : null}

        <div style={{ color: "var(--muted)", fontSize: ".88rem", lineHeight: 1.55 }}>
          {summary.recommendationOnly
            ? "이 표시는 현재 deterministic runtime 위에 붙는 연구선 메타데이터이며, 실제 generation provider routing이 자동으로 바뀌는 것은 아닙니다."
            : "이 표시는 실제 runtime routing 상태입니다."}
        </div>
      </div>
    </section>
  );
}
