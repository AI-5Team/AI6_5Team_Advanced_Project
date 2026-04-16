import { describeQuickActionPreview } from "./change-impact";
import { type ProjectResultResponse, type Purpose, type Style, type TemplateId } from "./contracts";

type QuickActionId = NonNullable<ReturnType<typeof describeQuickActionPreview>>["actionId"] | "friendly" | "fun" | "template";

export type QuickActionRecommendation = {
  actionId: QuickActionId;
  reason: string;
  priority: number;
};

type RecommendationInput = {
  result: ProjectResultResponse;
  purpose: Purpose;
  detailLocation?: string | null;
  currentTemplateId: TemplateId;
  currentStyle: Style;
  preferredTemplateId: TemplateId;
};

function maxBodyLength(result: ProjectResultResponse) {
  const deckLengths =
    result.copyDeck?.body.blocks.map((block) => Math.max(block.primaryLine.length, block.supportLine?.length ?? 0)) ?? [];
  const captionLengths = result.copySet.captions.map((caption) => caption.length);
  return Math.max(0, ...deckLengths, ...captionLengths);
}

export function recommendQuickActions({
  result,
  purpose,
  detailLocation,
  currentTemplateId,
  currentStyle,
  preferredTemplateId,
}: RecommendationInput): QuickActionRecommendation[] {
  const recommendations: QuickActionRecommendation[] = [];
  const activeActionIds = new Set(result.changeImpactSummary?.activeActions.map((action) => action.actionId) ?? []);
  const hookLength = Math.max(result.copyDeck?.hook?.primaryLine.length ?? 0, result.copyDeck?.hook?.supportLine?.length ?? 0, result.copySet.hookText.length);
  const bodyLength = maxBodyLength(result);

  if ((hookLength >= 22 || bodyLength >= 30) && !activeActionIds.has("shorterCopy")) {
    recommendations.push({
      actionId: "shorterCopy",
      reason: "현재 hook/body 길이가 길어서, 먼저 문장 밀도를 줄여 보는 편이 안전합니다.",
      priority: 96,
    });
  }

  if (purpose === "promotion" && !activeActionIds.has("highlightPrice")) {
    recommendations.push({
      actionId: "highlightPrice",
      reason: "행사형 결과라면 가격/혜택을 body 쪽에서 더 세게 보여 주는 것이 우선순위가 높습니다.",
      priority: 88,
    });
  }

  if (
    detailLocation &&
    result.copyPolicy?.guardActive &&
    !result.copyPolicy.emphasizeRegionRequested &&
    !activeActionIds.has("emphasizeRegion")
  ) {
    recommendations.push({
      actionId: "emphasizeRegion",
      reason: "상세 위치 guard는 유지한 채 regionName만 더 세게 밀 수 있어서 안전한 다음 수순입니다.",
      priority: 84,
    });
  }

  if (currentTemplateId !== preferredTemplateId && !activeActionIds.has("templateId")) {
    recommendations.push({
      actionId: "template",
      reason: `${purpose} 목적의 기본 템플릿과 현재 결과가 달라, 구조 자체를 바꿔 보는 가치가 있습니다.`,
      priority: 80,
    });
  }

  if (purpose === "promotion" && currentStyle !== "b_grade_fun") {
    recommendations.push({
      actionId: "fun",
      reason: "행사형 목적은 더 직접적이고 과장된 톤이 먹힐 가능성이 있어 `더 웃기게`를 같이 검토할 만합니다.",
      priority: 62,
    });
  }

  if ((purpose === "new_menu" || purpose === "review") && currentStyle !== "friendly") {
    recommendations.push({
      actionId: "friendly",
      reason: "현재 목적은 공격적인 톤보다 친근한 톤이 결과 안정성이 더 높을 가능성이 있습니다.",
      priority: 58,
    });
  }

  return recommendations
    .sort((a, b) => b.priority - a.priority)
    .filter((item, index, array) => array.findIndex((candidate) => candidate.actionId === item.actionId) === index)
    .slice(0, 3);
}
