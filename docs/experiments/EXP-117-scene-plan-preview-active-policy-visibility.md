# EXP-117 Scene Plan Preview Active Policy Visibility

## 목적

- `copyPolicy` active state가 결과 카드까지만 보이지 않고, `scenePlan` preview 진입 직전에도 같은 기준으로 보이는지 확인합니다.
- 사용자가 opening/closing scene을 열기 전에 현재 `detailLocation` guard 상태를 다시 읽을 수 있게 합니다.

## 변경 범위

- `apps/web/src/components/scene-plan-preview-links.tsx`
  - `activePolicy` prop을 추가했습니다.
  - preview 카드 안에서 다음 정보를 함께 보여줍니다.
    - `detailLocationPolicyId`
    - `guard 활성 / 비활성`
    - 금지 surface 요약
    - `emphasizeRegionRequested`가 있어도 guard 유지됨을 다시 표시
- `apps/web/src/components/demo-workbench.tsx`
- `apps/web/src/components/history-board.tsx`
  - `result.copyPolicy`를 `ScenePlanPreviewLinks`에 직접 전달합니다.

## 결과

- 이제 `scenePlan` preview 링크도 static scene count만 보여주지 않습니다.
- opening/closing scene으로 이동하기 전에, 현재 결과 payload 기준 `locationPolicy` active state를 같은 자리에서 다시 확인할 수 있습니다.

## 판단

- `copyPolicy` active state는 결과 카드, 이력 카드, scene preview 카드까지 같은 기준으로 보이는 것이 맞습니다.
- 이후 scene-frame 자체에 정책 경고를 더 넣을지 여부는 별도 판단으로 남깁니다.
