import type { ErrorResponse, GenerationStep } from "./common";
import type { ProjectStatus } from "../enums/status";
import type { Style } from "../enums/style";

export interface QuickOptions {
  highlightPrice?: boolean;
  shorterCopy?: boolean;
  emphasizeRegion?: boolean;
}

export interface ChangeSet {
  highlightPrice?: boolean;
  shorterCopy?: boolean;
  emphasizeRegion?: boolean;
  templateId?: string;
  styleOverride?: Style;
  approvedHybridSourceCandidateKey?: string;
}

export interface GenerateProjectRequest {
  assetIds: string[];
  templateId: string;
  quickOptions?: QuickOptions;
  approvedHybridSourceCandidateKey?: string;
}

export interface GenerateProjectResponse {
  generationRunId: string;
  projectId: string;
  status: "queued";
}

export interface RegenerateProjectRequest {
  changeSet: ChangeSet;
}

export interface GenerationResult {
  generationRunId: string;
  variantId: string;
  videoId: string;
  postId: string;
  copySetId: string;
  previewVideoUrl: string;
  previewImageUrl: string;
  ctaText: string;
}

export interface GenerationStatusResponse {
  projectId: string;
  projectStatus: ProjectStatus;
  steps?: GenerationStep[];
  result?: GenerationResult | null;
  error?: ErrorResponse["error"] | null;
}

export interface ActiveCopyPolicyState {
  detailLocationPolicyId: string | null;
  forbiddenDetailLocationSurfaces: string[];
  guardActive: boolean;
  emphasizeRegionRequested: boolean;
  detailLocationPresent: boolean;
}

export interface CopyDeckBodyBlock {
  blockId: string;
  textRole: string;
  uiLabel: string;
  primaryLine: string;
  supportLine: string | null;
}

export interface CopyDeck {
  templateId: string;
  hook: {
    primaryLine: string;
    supportLine: string | null;
  };
  body: {
    blocks: CopyDeckBodyBlock[];
  };
  cta: {
    primaryLine: string;
    supportLine: string | null;
  };
}

export interface SceneLayerSummaryItem {
  sceneId: string;
  slotGroup: "hook" | "body" | "cta";
  textRole: string;
  uiLabel: string;
}

export interface SceneLayerSummary {
  templateId: string;
  items: SceneLayerSummaryItem[];
}

export interface ChangeImpactAction {
  actionId: string;
  label: string;
  affectedLayers: string[];
  note: string;
}

export interface ChangeImpactSummary {
  runType: "initial" | "regenerate";
  impactLayers: string[];
  activeActions: ChangeImpactAction[];
}

export interface PromptBaselineContext {
  purpose: string;
  templateId: string;
  styleId: string;
  quickOptions: QuickOptions;
}

export interface PromptBaselineProfileSummary {
  profileId: string;
  label: string;
  profileKind: "default" | "option";
  status: string;
  sourceType: string;
  evidenceExperimentIds: string[];
  snapshotExperimentId: string | null;
  promptVariantId: string | null;
  scenarioId: string | null;
  purpose: string;
  templateId: string;
  styleId: string;
  scenarioQuickOptions: QuickOptions;
  model: {
    provider: string;
    modelName: string;
    role: string;
  };
  promptPresetId: string | null;
  locationPolicyId: string | null;
  requiredScore: number | null;
  usageGuidance: string[];
  applicable: boolean;
}

export interface PromptBaselineTransportRecommendation {
  mode: string;
  defaultProfileId: string | null;
  fallbackProfileId: string | null;
  trigger: string | null;
}

export interface PromptBaselineOperationalCheckSummary {
  experimentId: string;
  targetScenarioId: string | null;
  targetTemplateId: string | null;
  result: string;
  model: {
    provider: string;
    modelName: string;
    role: string;
  } | null;
  applicable: boolean;
  appliesToRecommendedModel: boolean;
  notes: string[];
  transportRecommendation: PromptBaselineTransportRecommendation | null;
}

export interface PromptBaselineExecutionHint {
  status: "default_match" | "option_match" | "coverage_gap";
  summary: string;
  recommendedProfileId: string | null;
  recommendedModel: {
    provider: string;
    modelName: string;
    role: string;
  } | null;
  notes: string[];
  transportRecommendation: (PromptBaselineTransportRecommendation & {
    sourceExperimentId: string | null;
  }) | null;
}

export interface PromptBaselineCoverageHint {
  summary: string;
  nearestProfileId: string | null;
  nearestProfileKind: "default" | "option" | null;
  mismatchDimensions: string[];
  gapClass: "quick_option_gap" | "scenario_gap" | "mixed_gap";
  recommendedAction: "consider_option_profile" | "run_new_scenario_experiment" | "keep_manual_review";
}

export interface PromptBaselinePolicyHint {
  policyState: "main_reference" | "option_reference" | "coverage_gap";
  recommendedAction: "use_main_profile_reference" | "use_option_profile_reference" | "manual_review_required";
  requiresManualReview: boolean;
  summary: string;
  recommendedProfileId: string | null;
  recommendedModel: {
    provider: string;
    modelName: string;
    role: string;
  } | null;
  transportRecommendation: (PromptBaselineTransportRecommendation & {
    sourceExperimentId: string | null;
  }) | null;
  notes: string[];
}

export interface PromptBaselineSummary {
  baselineId: string;
  status: string;
  scope: string;
  recommendationOnly: boolean;
  context: PromptBaselineContext;
  defaultProfile: PromptBaselineProfileSummary | null;
  recommendedProfile: PromptBaselineProfileSummary | null;
  candidateProfiles: PromptBaselineProfileSummary[];
  executionHint: PromptBaselineExecutionHint | null;
  coverageHint: PromptBaselineCoverageHint | null;
  policyHint: PromptBaselinePolicyHint | null;
  operationalChecks: PromptBaselineOperationalCheckSummary[];
}

export interface RendererSummary {
  videoSourceMode?: string | null;
  motionMode?: string | null;
  framingMode?: string | null;
  durationStrategy?: string | null;
  targetDurationSec?: number | null;
  hybridSourceSelectionMode?: string | null;
  hybridSourceCandidateKey?: string | null;
}

export interface ProjectResultResponse {
  projectId: string;
  generationRunId: string;
  variantId: string;
  video: {
    videoId: string;
    url: string;
    durationSec: number;
    templateId: string;
  };
  post: {
    postId: string;
    url: string;
  };
  copySet: {
    copySetId: string;
    hookText: string;
    captions: string[];
    hashtags: string[];
    ctaText: string;
  };
  scenePlan?: {
    url: string;
    sceneCount?: number | null;
    sceneSpecVersion?: string | null;
  } | null;
  sceneLayerSummary?: SceneLayerSummary | null;
  changeImpactSummary?: ChangeImpactSummary | null;
  copyPolicy?: ActiveCopyPolicyState | null;
  copyDeck?: CopyDeck | null;
  promptBaselineSummary?: PromptBaselineSummary | null;
  rendererSummary?: RendererSummary | null;
}
