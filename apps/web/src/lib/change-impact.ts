import {
  QUICK_ACTIONS,
  type ProjectResultResponse,
  type QuickOptions,
  type RegenerateChangeSet,
  type Style,
  type TemplateId,
} from "./contracts";

type ChangeImpactSummary = NonNullable<ProjectResultResponse["changeImpactSummary"]>;
type ChangeImpactAction = ChangeImpactSummary["activeActions"][number];
type QuickActionId = (typeof QUICK_ACTIONS)[number]["id"];

function createDescriptor(
  actionId: string,
  label: string,
  affectedLayers: string[],
  note: string,
): ChangeImpactAction {
  return { actionId, label, affectedLayers, note };
}

function uniqueLayers(actions: ChangeImpactAction[]) {
  return actions.flatMap((item) => item.affectedLayers).filter((layer, index, array) => array.indexOf(layer) === index);
}

export function describeChangeImpact(kind: "shorterCopy"): ChangeImpactAction;
export function describeChangeImpact(kind: "highlightPrice"): ChangeImpactAction;
export function describeChangeImpact(kind: "emphasizeRegion"): ChangeImpactAction;
export function describeChangeImpact(kind: "styleOverride", value: Style): ChangeImpactAction;
export function describeChangeImpact(kind: "templateId", value: TemplateId): ChangeImpactAction;
export function describeChangeImpact(kind: string, value?: string): ChangeImpactAction {
  switch (kind) {
    case "shorterCopy":
      return createDescriptor("shorterCopy", "문구 더 짧게", ["hook", "body", "cta"], "전체 카피 길이를 줄여 hook/body/cta 전반에 영향을 줍니다.");
    case "highlightPrice":
      return createDescriptor("highlightPrice", "가격 더 크게", ["body"], "혜택이나 가격 설명이 들어가는 body block을 우선적으로 바꿉니다.");
    case "emphasizeRegion":
      return createDescriptor("emphasizeRegion", "지역명 강조", ["hook", "body"], "regionName 노출을 더 세게 만들어 hook과 body 문구에 영향을 줍니다.");
    case "styleOverride":
      return createDescriptor(
        "styleOverride",
        value === "b_grade_fun" ? "더 웃기게" : value === "friendly" ? "더 친근하게" : "스타일 변경",
        ["visual"],
        `스타일을 \`${value}\`로 바꿔 시각 톤과 말투에 영향을 줍니다.`,
      );
    case "templateId":
      return createDescriptor(
        "templateId",
        "다른 템플릿으로",
        ["hook", "body", "cta", "structure"],
        `템플릿을 \`${value}\`로 바꿔 scene 구조와 카피 슬롯 전체에 영향을 줍니다.`,
      );
    default:
      return createDescriptor(kind, kind, [], "영향 범위 정보가 아직 정리되지 않았습니다.");
  }
}

export function buildChangeImpactSummary(
  runType: ChangeImpactSummary["runType"],
  quickOptions: QuickOptions,
  changeSet: RegenerateChangeSet,
): ChangeImpactSummary {
  const merged = { ...quickOptions, ...changeSet };
  const activeActions: ChangeImpactAction[] = [];

  if (merged.shorterCopy) {
    activeActions.push(describeChangeImpact("shorterCopy"));
  }
  if (merged.highlightPrice) {
    activeActions.push(describeChangeImpact("highlightPrice"));
  }
  if (merged.emphasizeRegion) {
    activeActions.push(describeChangeImpact("emphasizeRegion"));
  }
  if (merged.styleOverride) {
    activeActions.push(describeChangeImpact("styleOverride", merged.styleOverride));
  }
  if (merged.templateId) {
    activeActions.push(describeChangeImpact("templateId", merged.templateId));
  }

  return {
    runType,
    impactLayers: uniqueLayers(activeActions),
    activeActions,
  };
}

export function describeQuickActionPreview(actionId: QuickActionId, nextTemplateId: TemplateId) {
  switch (actionId) {
    case "highlightPrice":
      return describeChangeImpact("highlightPrice");
    case "shorterCopy":
      return describeChangeImpact("shorterCopy");
    case "emphasizeRegion":
      return describeChangeImpact("emphasizeRegion");
    case "friendly":
      return describeChangeImpact("styleOverride", "friendly");
    case "fun":
      return describeChangeImpact("styleOverride", "b_grade_fun");
    case "template":
      return describeChangeImpact("templateId", nextTemplateId);
  }
}
