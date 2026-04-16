# EXP-124 Scene Preview Change Impact Visibility

## 목적

- `changeImpactSummary`를 결과 카드에만 두지 않고, scene preview 진입 카드에서도 같이 보이게 합니다.
- opening/closing scene을 열기 전 단계에서 `이번 결과가 어떤 변경을 반영한 상태인지` 바로 판단할 수 있게 합니다.

## 변경 범위

- `apps/web/src/components/scene-plan-preview-links.tsx`
  - `changeImpactSummary`를 받아 run type, impact layer, active action label을 같이 보여주도록 확장했습니다.
- `apps/web/src/components/demo-workbench.tsx`
- `apps/web/src/components/history-board.tsx`
  - scene preview 카드에 현재 result의 `changeImpactSummary`를 전달합니다.

## 결과

- 이제 scene preview 카드에서도 `재생성 / 초기 생성`, `HOOK/BODY/CTA/VISUAL/STRUCTURE` 영향 레이어, active quick action label을 바로 볼 수 있습니다.
- 따라서 사용자는 scene-frame을 열기 전에도 `이 씬 검토가 어떤 변경이 반영된 결과인지`를 먼저 이해할 수 있습니다.

## 판단

- `copyPolicy`, `sceneLayerSummary`, `changeImpactSummary`가 scene preview 카드에 함께 모이면서, scene 검토 진입점이 단순 링크 모음이 아니라 결과 해석 패널에 가까워졌습니다.
- 다음 단계에서는 quick action 버튼 자체에 이 영향 레이어를 역으로 붙일지, 아니면 여기서 멈추고 prompt baseline 실험으로 돌아갈지 판단하면 됩니다.
