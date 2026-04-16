# EXP-125 Quick Action Impact Preview

## 목적

- quick action 버튼을 누르기 전에도 각 액션이 어떤 층을 바꾸는지 바로 읽을 수 있게 합니다.
- 결과 화면에서만 보이던 `changeImpactSummary` 기준을 quick action 선택 단계까지 끌어옵니다.

## 변경 범위

- `apps/web/src/lib/change-impact.ts`
  - quick action 영향 descriptor와 `changeImpactSummary` builder를 공통 helper로 분리했습니다.
- `apps/web/src/lib/demo-store.ts`
  - demo fallback도 새 helper를 사용해 결과 summary를 생성합니다.
- `apps/web/src/components/demo-workbench.tsx`
  - quick action 버튼을 정보형 카드로 확장하고, 각 버튼 아래에 영향 레이어와 설명을 같이 보여줍니다.

## 결과

- 이제 `가격 더 크게`, `문구 더 짧게`, `지역명 강조`, `더 친근하게`, `더 웃기게`, `다른 템플릿으로` 버튼은 각각 `BODY`, `HOOK/BODY/CTA`, `HOOK/BODY`, `VISUAL`, `VISUAL`, `HOOK/BODY/CTA/STRUCTURE` 영향 범위를 미리 보여줍니다.
- 사용자는 regenerate를 누르기 전부터 어떤 축이 바뀔지 보고 액션을 고를 수 있습니다.

## 판단

- 이 단계로 quick action은 단순 토글 모음이 아니라, `어떤 층을 바꾸는 도구인지` 설명 가능한 조작 패널이 됐습니다.
- 다음에는 이 preview와 실제 `changeImpactSummary`를 더 직접 비교하거나, active result 기준으로 추천 quick action을 얹는 방향이 자연스럽습니다.
