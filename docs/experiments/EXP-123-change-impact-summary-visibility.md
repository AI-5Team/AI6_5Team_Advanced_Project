# EXP-123 Change Impact Summary Visibility

## 목적

- quick action과 regenerate change set이 실제로 어떤 층을 바꾸는지 `result` payload와 결과 화면에서 바로 읽을 수 있게 합니다.
- `copyDeck`, `sceneLayerSummary`에 이어 `이번 run이 무엇을 바꿨는가`를 별도 요약 구조로 노출합니다.

## 변경 범위

- `packages/contracts/schemas/generation.ts`
  - `ChangeImpactSummary`와 action item shape를 추가했습니다.
- `services/worker/pipelines/generation.py`
  - `run_type`, `quickOptions` 기준으로 `changeImpactSummary`를 생성해 `render-meta.json`에 넣습니다.
- `services/api/app/services/runtime.py`
- `services/api/app/schemas/api.py`
  - `/api/projects/{projectId}/result` 응답에 `changeImpactSummary`를 포함합니다.
- `apps/web/src/lib/demo-store.ts`
  - demo fallback result도 같은 `changeImpactSummary` shape를 생성합니다.
- `apps/web/src/components/change-impact-summary.tsx`
  - 변경 영향 요약 카드를 추가했습니다.
- `apps/web/src/components/demo-workbench.tsx`
- `apps/web/src/components/history-board.tsx`
  - 결과/이력 화면 모두 `changeImpactSummary`를 직접 노출합니다.

## 결과

- 이제 `result` payload는 `copyPolicy`, `copyDeck`, `sceneLayerSummary`뿐 아니라 `changeImpactSummary`도 같이 가집니다.
- 사용자는 `shorterCopy`, `highlightPrice`, `emphasizeRegion`, `styleOverride`, `templateId` 같은 action이 `hook/body/cta/visual/structure` 중 어디에 영향을 줬는지 결과 카드에서 바로 확인할 수 있습니다.
- 초기 생성 run과 재생성 run도 같은 기준으로 비교할 수 있습니다.

## 판단

- 이 구조는 quick action이 실제로 어떤 층을 바꿨는지 설명 가능한 상태로 만드는 첫 단계입니다.
- 이후 quick action 버튼, scene preview, regenerate diff를 더 직접 연결할 때도 같은 `changeImpactSummary`를 공통 기준으로 재사용할 수 있습니다.
