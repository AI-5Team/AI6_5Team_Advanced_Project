import promptBaselineManifest from "../../../../packages/template-spec/manifests/prompt-baseline-v1.json";
import type { ProjectResultResponse, Purpose, QuickOptions, Style } from "./contracts";

type PromptBaselineSummary = NonNullable<ProjectResultResponse["promptBaselineSummary"]>;
type PromptBaselineProfileSummary = NonNullable<PromptBaselineSummary["defaultProfile"]>;
type PromptBaselineOperationalCheckSummary = PromptBaselineSummary["operationalChecks"][number];

type PromptBaselineContextInput = {
  purpose: Purpose;
  templateId: string;
  styleId: Style;
  quickOptions?: QuickOptions;
};

type ManifestProfileSource = {
  profileId?: string;
  label?: string;
  status?: string;
  sourceType?: string;
  sourceExperimentId?: string;
  sourceEvidence?: Record<string, unknown>;
  snapshotExperimentId?: string;
  promptVariantId?: string;
  selectedScenario?: {
    scenarioId?: string;
    purpose?: string;
    templateId?: string;
    styleId?: string;
    quickOptions?: QuickOptions;
  };
  selectedModel?: {
    provider?: string;
    modelName?: string;
    role?: string;
  };
  promptPreset?: {
    presetId?: string;
  };
  evaluationPolicy?: {
    locationPolicyId?: string;
    requiredScore?: number;
  };
  usageGuidance?: string[];
};

type ManifestOperationalCheckSource = {
  experimentId?: string;
  targetScenarioId?: string;
  targetTemplateId?: string;
  result?: string;
  notes?: string[];
  selectedModel?: {
    provider?: string;
    modelName?: string;
    role?: string;
  };
  transportRecommendation?: {
    mode?: string;
    defaultProfileId?: string;
    fallbackProfileId?: string;
    trigger?: string;
  };
};

function normalizeQuickOptions(quickOptions?: QuickOptions) {
  return {
    highlightPrice: Boolean(quickOptions?.highlightPrice),
    shorterCopy: Boolean(quickOptions?.shorterCopy),
    emphasizeRegion: Boolean(quickOptions?.emphasizeRegion),
  } satisfies QuickOptions;
}

function collectExperimentIds(...sources: unknown[]) {
  const ids: string[] = [];

  const addValue = (value: unknown) => {
    if (typeof value === "string" && value.startsWith("EXP-") && !ids.includes(value)) {
      ids.push(value);
    }
  };

  for (const source of sources) {
    if (Array.isArray(source)) {
      source.forEach(addValue);
      continue;
    }
    if (source && typeof source === "object") {
      Object.values(source).forEach(addValue);
      continue;
    }
    addValue(source);
  }

  return ids;
}

function buildModelSummary(model: { provider?: string; modelName?: string; role?: string } | undefined) {
  return {
    provider: model?.provider ?? "",
    modelName: model?.modelName ?? "",
    role: model?.role ?? "",
  };
}

function isFilledModel(model: { provider: string; modelName: string; role: string } | null | undefined) {
  return Boolean(model && model.provider && model.modelName);
}

function modelsMatch(
  left: { provider: string; modelName: string; role: string } | null | undefined,
  right: { provider: string; modelName: string; role: string } | null | undefined,
) {
  if (!isFilledModel(left) || !isFilledModel(right)) return false;
  const leftModel = left as { provider: string; modelName: string; role: string };
  const rightModel = right as { provider: string; modelName: string; role: string };
  return leftModel.provider === rightModel.provider && leftModel.modelName === rightModel.modelName;
}

function scenarioMatchesContext(
  scenario: ManifestProfileSource["selectedScenario"] | undefined,
  context: PromptBaselineSummary["context"],
) {
  if (!scenario) return false;
  if ((scenario.purpose ?? "") !== context.purpose) return false;
  if ((scenario.templateId ?? "") !== context.templateId) return false;
  if ((scenario.styleId ?? "") !== context.styleId) return false;

  const scenarioQuickOptions = scenario.quickOptions ?? {};
  for (const [key, value] of Object.entries(scenarioQuickOptions)) {
    if (typeof value !== "boolean") continue;
    if ((context.quickOptions as Record<string, boolean | undefined>)[key] !== value) {
      return false;
    }
  }

  return true;
}

function buildProfileSummary(
  source: ManifestProfileSource,
  context: PromptBaselineSummary["context"],
  profileKind: PromptBaselineProfileSummary["profileKind"],
  fallbackLabel: string,
) {
  const scenario = source.selectedScenario ?? {};
  const evaluationPolicy = source.evaluationPolicy ?? {};
  const promptPreset = source.promptPreset ?? {};

  return {
    profileId: source.profileId ?? fallbackLabel,
    label: source.label ?? source.profileId ?? fallbackLabel,
    profileKind,
    status: source.status ?? "candidate",
    sourceType: source.sourceType ?? (profileKind === "default" ? "baseline_manifest" : "baseline_option"),
    evidenceExperimentIds: collectExperimentIds(source.sourceExperimentId, source.sourceEvidence),
    snapshotExperimentId: source.snapshotExperimentId ?? null,
    promptVariantId: source.promptVariantId ?? null,
    scenarioId: scenario.scenarioId ?? null,
    purpose: scenario.purpose ?? "",
    templateId: scenario.templateId ?? "",
    styleId: scenario.styleId ?? "",
    scenarioQuickOptions: normalizeQuickOptions(scenario.quickOptions),
    model: buildModelSummary(source.selectedModel),
    promptPresetId: promptPreset.presetId ?? null,
    locationPolicyId: evaluationPolicy.locationPolicyId ?? null,
    requiredScore: typeof evaluationPolicy.requiredScore === "number" ? evaluationPolicy.requiredScore : null,
    usageGuidance: Array.isArray(source.usageGuidance) ? source.usageGuidance.filter((item): item is string => typeof item === "string") : [],
    applicable: scenarioMatchesContext(scenario, context),
  } satisfies PromptBaselineProfileSummary;
}

function buildTransportRecommendation(
  source: ManifestOperationalCheckSource["transportRecommendation"] | undefined,
): PromptBaselineOperationalCheckSummary["transportRecommendation"] {
  if (!source || typeof source !== "object") return null;

  return {
    mode: typeof source.mode === "string" ? source.mode : "",
    defaultProfileId: typeof source.defaultProfileId === "string" ? source.defaultProfileId : null,
    fallbackProfileId: typeof source.fallbackProfileId === "string" ? source.fallbackProfileId : null,
    trigger: typeof source.trigger === "string" ? source.trigger : null,
  };
}

function buildOperationalCheckSummary(
  source: ManifestOperationalCheckSource,
  context: PromptBaselineSummary["context"],
  recommendedProfile: PromptBaselineSummary["recommendedProfile"],
): PromptBaselineOperationalCheckSummary {
  const model = buildModelSummary(source.selectedModel);
  const applicableByTemplate = !source.targetTemplateId || source.targetTemplateId === context.templateId;
  const applicableByScenario = !source.targetScenarioId || source.targetScenarioId === recommendedProfile?.scenarioId;

  return {
    experimentId: typeof source.experimentId === "string" ? source.experimentId : "",
    targetScenarioId: typeof source.targetScenarioId === "string" ? source.targetScenarioId : null,
    targetTemplateId: typeof source.targetTemplateId === "string" ? source.targetTemplateId : null,
    result: typeof source.result === "string" ? source.result : "",
    model: isFilledModel(model) ? model : null,
    applicable: applicableByTemplate && applicableByScenario,
    appliesToRecommendedModel: modelsMatch(model, recommendedProfile?.model),
    notes: Array.isArray(source.notes) ? source.notes.filter((item): item is string => typeof item === "string") : [],
    transportRecommendation: buildTransportRecommendation(source.transportRecommendation),
  };
}

function dedupeNotes(values: string[]) {
  const unique: string[] = [];
  for (const value of values) {
    if (value && !unique.includes(value)) {
      unique.push(value);
    }
  }
  return unique;
}

function collectProfileMismatchDimensions(
  profile: PromptBaselineSummary["defaultProfile"] | PromptBaselineSummary["recommendedProfile"],
  context: PromptBaselineSummary["context"],
) {
  if (!profile) return [];

  const mismatches: string[] = [];
  if (profile.purpose !== context.purpose) mismatches.push("purpose");
  if (profile.templateId !== context.templateId) mismatches.push("templateId");
  if (profile.styleId !== context.styleId) mismatches.push("styleId");

  for (const [key, value] of Object.entries(profile.scenarioQuickOptions)) {
    if (typeof value !== "boolean") continue;
    if ((context.quickOptions as Record<string, boolean | undefined>)[key] !== value) {
      mismatches.push(`quickOptions.${key}`);
    }
  }

  return mismatches;
}

function buildProfileDistanceKey(
  mismatches: string[],
  profile: PromptBaselineSummary["defaultProfile"] | PromptBaselineSummary["recommendedProfile"],
) {
  const structuralCount = mismatches.filter((item) => item === "purpose" || item === "templateId" || item === "styleId").length;
  const quickOptionCount = mismatches.filter((item) => item.startsWith("quickOptions.")).length;
  const profileKindBias = profile?.profileKind === "option" ? 0 : 1;
  return [structuralCount, quickOptionCount, mismatches.length, profileKindBias] as const;
}

function buildExecutionHint(
  recommendedProfile: PromptBaselineSummary["recommendedProfile"],
  operationalChecks: PromptBaselineOperationalCheckSummary[],
): PromptBaselineSummary["executionHint"] {
  if (!recommendedProfile) {
    return {
      status: "coverage_gap",
      summary: "현재 컨텍스트와 exact match되는 prompt profile이 없어 baseline reference만 존재합니다.",
      recommendedProfileId: null,
      recommendedModel: null,
      notes: ["현재 결과는 profile coverage 밖이므로, main baseline은 참고용으로만 보셔야 합니다."],
      transportRecommendation: null,
    };
  }

  const matchedOperationalCheck =
    operationalChecks.find((item) => item.applicable && item.appliesToRecommendedModel && item.transportRecommendation) ?? null;
  const status = recommendedProfile.profileKind === "default" ? "default_match" : "option_match";
  const notes = dedupeNotes([
    status === "default_match"
      ? "현재 컨텍스트는 main baseline과 exact match됩니다."
      : "현재 컨텍스트는 main baseline exact match가 아니라 option profile 기준으로 권장됩니다.",
    ...recommendedProfile.usageGuidance.slice(0, 2),
    matchedOperationalCheck?.notes[0] ?? "",
  ]);

  return {
    status,
    summary:
      status === "default_match"
        ? "현재 컨텍스트는 main baseline을 그대로 참고할 수 있습니다."
        : "현재 컨텍스트는 option profile을 우선 참고하는 편이 맞습니다.",
    recommendedProfileId: recommendedProfile.profileId,
    recommendedModel: isFilledModel(recommendedProfile.model) ? recommendedProfile.model : null,
    notes,
    transportRecommendation: matchedOperationalCheck?.transportRecommendation
      ? {
          ...matchedOperationalCheck.transportRecommendation,
          sourceExperimentId: matchedOperationalCheck.experimentId || null,
        }
      : null,
  };
}

function buildCoverageHint(
  recommendedProfile: PromptBaselineSummary["recommendedProfile"],
  defaultProfile: PromptBaselineSummary["defaultProfile"],
  candidateProfiles: PromptBaselineSummary["candidateProfiles"],
  context: PromptBaselineSummary["context"],
): PromptBaselineSummary["coverageHint"] {
  if (recommendedProfile) return null;

  const profiles = [defaultProfile, ...candidateProfiles].filter(
    (profile): profile is NonNullable<PromptBaselineSummary["defaultProfile"]> => Boolean(profile),
  );
  if (!profiles.length) {
    return {
      summary: "비교 가능한 prompt profile이 아직 등록되지 않아 coverage gap 원인을 계산할 수 없습니다.",
      nearestProfileId: null,
      nearestProfileKind: null,
      mismatchDimensions: [],
      gapClass: "mixed_gap",
      recommendedAction: "keep_manual_review",
    };
  }

  let nearestProfile: NonNullable<PromptBaselineSummary["defaultProfile"]> | null = null;
  let nearestMismatches: string[] | null = null;
  let nearestDistanceKey: readonly [number, number, number, number] | null = null;
  for (const profile of profiles) {
    const mismatches = collectProfileMismatchDimensions(profile, context);
    const distanceKey = buildProfileDistanceKey(mismatches, profile);
    if (
      !nearestDistanceKey ||
      distanceKey[0] < nearestDistanceKey[0] ||
      (distanceKey[0] === nearestDistanceKey[0] && distanceKey[1] < nearestDistanceKey[1]) ||
      (distanceKey[0] === nearestDistanceKey[0] &&
        distanceKey[1] === nearestDistanceKey[1] &&
        distanceKey[2] < nearestDistanceKey[2]) ||
      (distanceKey[0] === nearestDistanceKey[0] &&
        distanceKey[1] === nearestDistanceKey[1] &&
        distanceKey[2] === nearestDistanceKey[2] &&
        distanceKey[3] < nearestDistanceKey[3])
    ) {
      nearestProfile = profile;
      nearestMismatches = mismatches;
      nearestDistanceKey = distanceKey;
    }
  }

  const mismatchDimensions = nearestMismatches ?? [];
  const mismatchLabel = mismatchDimensions.slice(0, 3).join(", ") || "미기록";
  const structuralMismatch = mismatchDimensions.some((item) => item === "purpose" || item === "templateId" || item === "styleId");
  const quickOptionOnly = Boolean(mismatchDimensions.length) && mismatchDimensions.every((item) => item.startsWith("quickOptions."));

  let gapClass: NonNullable<PromptBaselineSummary["coverageHint"]>["gapClass"] = "mixed_gap";
  let recommendedAction: NonNullable<PromptBaselineSummary["coverageHint"]>["recommendedAction"] = "keep_manual_review";
  let summary = `현재 컨텍스트와 exact match되는 prompt profile은 없고, 가장 가까운 profile은 ${
    nearestProfile?.profileId ?? "미기록"
  }입니다. 현재 mismatch 축은 ${mismatchLabel}이며, 혼합 mismatch라서 우선 manual review로 두는 편이 맞습니다.`;

  if (quickOptionOnly && !structuralMismatch) {
    gapClass = "quick_option_gap";
    recommendedAction = "consider_option_profile";
    summary = `현재 컨텍스트와 exact match되는 prompt profile은 없고, 가장 가까운 profile은 ${
      nearestProfile?.profileId ?? "미기록"
    }입니다. 현재 mismatch 축은 ${mismatchLabel}이며, quick option 차이로 보여 option profile 후보로 검토하는 편이 맞습니다.`;
  } else if (structuralMismatch) {
    gapClass = "scenario_gap";
    recommendedAction = "run_new_scenario_experiment";
    summary = `현재 컨텍스트와 exact match되는 prompt profile은 없고, 가장 가까운 profile은 ${
      nearestProfile?.profileId ?? "미기록"
    }입니다. 현재 mismatch 축은 ${mismatchLabel}이며, scenario 축 차이로 보여 새 scenario 실험이 먼저입니다.`;
  }

  return {
    summary,
    nearestProfileId: nearestProfile?.profileId ?? null,
    nearestProfileKind: nearestProfile?.profileKind ?? null,
    mismatchDimensions,
    gapClass,
    recommendedAction,
  };
}

function buildPolicyHint(executionHint: PromptBaselineSummary["executionHint"]): PromptBaselineSummary["policyHint"] {
  if (!executionHint) return null;

  if (executionHint.status === "default_match") {
    return {
      policyState: "main_reference",
      recommendedAction: "use_main_profile_reference",
      requiresManualReview: false,
      summary: "현재 컨텍스트는 main baseline 기준으로 운영 판단을 이어가면 됩니다.",
      recommendedProfileId: executionHint.recommendedProfileId,
      recommendedModel: executionHint.recommendedModel,
      transportRecommendation: executionHint.transportRecommendation,
      notes: executionHint.notes,
    };
  }

  if (executionHint.status === "option_match") {
    return {
      policyState: "option_reference",
      recommendedAction: "use_option_profile_reference",
      requiresManualReview: false,
      summary: "현재 컨텍스트는 option profile 기준으로 운영 판단을 이어가는 편이 맞습니다.",
      recommendedProfileId: executionHint.recommendedProfileId,
      recommendedModel: executionHint.recommendedModel,
      transportRecommendation: executionHint.transportRecommendation,
      notes: executionHint.notes,
    };
  }

  return {
    policyState: "coverage_gap",
    recommendedAction: "manual_review_required",
    requiresManualReview: true,
    summary: "현재 컨텍스트는 baseline coverage 밖이라 자동 정책 판단보다 수동 검토가 먼저입니다.",
    recommendedProfileId: null,
    recommendedModel: null,
    transportRecommendation: null,
    notes: executionHint.notes,
  };
}

export function buildPromptBaselineSummary({
  purpose,
  templateId,
  styleId,
  quickOptions,
}: PromptBaselineContextInput): PromptBaselineSummary {
  const context = {
    purpose,
    templateId,
    styleId,
    quickOptions: normalizeQuickOptions(quickOptions),
  } satisfies PromptBaselineSummary["context"];

  const defaultProfile = buildProfileSummary(
    {
      profileId: "main_baseline",
      label: promptBaselineManifest.baselineId,
      status: promptBaselineManifest.status,
      sourceType: "baseline_manifest",
      sourceEvidence: promptBaselineManifest.sourceEvidence,
      selectedScenario: promptBaselineManifest.selectedScenario,
      selectedModel: promptBaselineManifest.selectedModel,
      promptPreset: promptBaselineManifest.promptPreset,
      evaluationPolicy: promptBaselineManifest.evaluationPolicy,
      usageGuidance: promptBaselineManifest.usageGuidance,
    },
    context,
    "default",
    "main_baseline",
  );

  const candidateProfiles = (promptBaselineManifest.baselineOptions ?? []).map((option) =>
    buildProfileSummary(option, context, "option", option.profileId ?? option.label ?? "candidate_profile"),
  );

  const recommendedProfile =
    defaultProfile.applicable
      ? defaultProfile
      : candidateProfiles.find((profile) => profile.applicable) ?? null;
  const operationalChecks = (promptBaselineManifest.operationalChecks ?? []).map((item) =>
    buildOperationalCheckSummary(item, context, recommendedProfile),
  );
  const executionHint = buildExecutionHint(recommendedProfile, operationalChecks);

  return {
    baselineId: promptBaselineManifest.baselineId,
    status: promptBaselineManifest.status,
    scope: promptBaselineManifest.scope,
    recommendationOnly: true,
    context,
    defaultProfile,
    recommendedProfile,
    candidateProfiles,
    executionHint,
    coverageHint: buildCoverageHint(recommendedProfile, defaultProfile, candidateProfiles, context),
    policyHint: buildPolicyHint(executionHint),
    operationalChecks,
  };
}
