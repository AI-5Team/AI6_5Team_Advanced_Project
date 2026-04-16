import type { ApprovedHybridInventoryResponse, BusinessType, TemplateId } from "./contracts";

type HybridLaneHintConfidence = "high" | "medium" | "low" | "none";

export interface HybridLaneHint {
  lane: string | null;
  confidence: HybridLaneHintConfidence;
  evidence: string[];
  scoreByLane: Record<string, number>;
  recommendedCandidateKey: string | null;
  consideredAssetFileNames: string[];
}

type HybridLaneHintInput = {
  businessType: BusinessType;
  templateId: TemplateId;
  assetFileNames: string[];
  inventory: ApprovedHybridInventoryResponse | null;
};

const DRINK_KEYWORDS = ["맥주", "커피", "아메리카노", "라떼", "beer", "coffee", "latte", "drink", "beverage"];
const TRAY_KEYWORDS = ["규카츠", "라멘", "장어덮밥", "덮밥", "짬뽕", "타코야키", "plate", "tray", "ramen", "katsu", "meal", "sandwich"];

function normalizeToken(value: string) {
  return value.trim().toLowerCase();
}

function addScore(scoreByLane: Record<string, number>, lane: string, points: number) {
  scoreByLane[lane] = (scoreByLane[lane] ?? 0) + points;
}

export function inferHybridLaneHint({
  businessType,
  templateId,
  assetFileNames,
  inventory,
}: HybridLaneHintInput): HybridLaneHint {
  const knownLanes = Object.keys(inventory?.laneCounts ?? {});
  const scoreByLane = Object.fromEntries(knownLanes.map((lane) => [lane, 0])) as Record<string, number>;
  const evidenceByLane = Object.fromEntries(knownLanes.map((lane) => [lane, [] as string[]])) as Record<string, string[]>;

  const addEvidence = (lane: string, reason: string, points: number) => {
    addScore(scoreByLane, lane, points);
    evidenceByLane[lane] = [...(evidenceByLane[lane] ?? []), `${reason} (+${points})`];
  };

  if (businessType === "cafe") {
    addEvidence("drink_glass_lane", "업종이 cafe라서 drink lane 우선", 2);
  }
  if (businessType === "restaurant") {
    addEvidence("tray_full_plate_lane", "업종이 restaurant라서 tray/full-plate lane 우선", 2);
  }

  if (templateId === "T02" && businessType === "restaurant") {
    addEvidence("tray_full_plate_lane", "행사형 음식점 템플릿이라 tray/full-plate lane 쪽 맥락이 강함", 1);
  }

  const normalizedFileNames = assetFileNames.map((fileName) => ({
    original: fileName,
    normalized: normalizeToken(fileName),
  }));

  const inventoryLabels = Object.keys(inventory?.labelCounts ?? {}).map((label) => ({
    label,
    normalized: normalizeToken(label),
    lane: inventory?.recommendedByLabel?.[label]?.serviceLane ?? null,
  }));

  normalizedFileNames.forEach(({ original, normalized }) => {
    inventoryLabels.forEach(({ label, normalized: normalizedLabel, lane }) => {
      if (!lane || !normalizedLabel || !normalized.includes(normalizedLabel)) return;
      addEvidence(lane, `파일명 '${original}'에 approved label '${label}'이 포함됨`, 4);
    });

    if (DRINK_KEYWORDS.some((keyword) => normalized.includes(normalizeToken(keyword)))) {
      addEvidence("drink_glass_lane", `파일명 '${original}'이 drink 계열 키워드를 포함함`, 2);
    }
    if (TRAY_KEYWORDS.some((keyword) => normalized.includes(normalizeToken(keyword)))) {
      addEvidence("tray_full_plate_lane", `파일명 '${original}'이 tray/full-plate 계열 키워드를 포함함`, 2);
    }
  });

  const ranked = Object.entries(scoreByLane).sort((left, right) => right[1] - left[1]);
  const [topLane, topScore] = ranked[0] ?? [null, 0];
  const [, secondScore] = ranked[1] ?? [null, 0];

  if (!topLane || topScore <= 0 || topScore === secondScore) {
    return {
      lane: null,
      confidence: "none",
      evidence: topScore === secondScore && topScore > 0 ? ["서로 다른 lane 근거가 비슷해 명확한 추천을 내리지 않았습니다."] : [],
      scoreByLane,
      recommendedCandidateKey: null,
      consideredAssetFileNames: assetFileNames,
    };
  }

  const scoreGap = topScore - secondScore;
  const confidence: HybridLaneHintConfidence =
    topScore >= 6 && scoreGap >= 3 ? "high" : topScore >= 4 && scoreGap >= 2 ? "medium" : "low";

  return {
    lane: topLane,
    confidence,
    evidence: evidenceByLane[topLane] ?? [],
    scoreByLane,
    recommendedCandidateKey: inventory?.recommendedByLane?.[topLane]?.candidateKey ?? null,
    consideredAssetFileNames: assetFileNames,
  };
}
