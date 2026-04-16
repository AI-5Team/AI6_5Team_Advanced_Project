# EXP-126 Active Result Quick Action Recommendation

## 목적

- quick action 영향 레이어 preview를 한 단계 더 발전시켜, 현재 결과 기준 추천 action도 같이 제안하게 합니다.
- 사용자가 result를 보고 직접 다음 액션을 해석하는 비용을 줄이고, 추천 후보를 먼저 좁혀 줍니다.

## 변경 범위

- `apps/web/src/lib/quick-action-recommendation.ts`
  - 현재 result, purpose, detailLocation, template, style를 기준으로 추천 quick action을 고르는 얇은 heuristic helper를 추가했습니다.
- `apps/web/src/components/demo-workbench.tsx`
  - 추천 action 요약 패널을 추가했습니다.
  - 각 quick action 카드에 추천 badge, priority, 추천 이유를 같이 붙였습니다.

## 결과

- 이제 메인 결과 화면은 단순 quick action 목록이 아니라, `현재 결과 기준 추천 action`까지 먼저 보여줍니다.
- 예를 들어 copy가 길면 `문구 더 짧게`, promotion이면 `가격 더 크게`, detailLocation guard가 살아 있고 region 강조가 아직 없으면 `지역명 강조`를 먼저 제안합니다.

## 판단

- 이 추천은 정답 자동화가 아니라, 결과 해석 비용을 줄이는 lightweight guidance입니다.
- 이후 실제 클릭 로그나 품질 평가와 연결하면 heuristic을 더 정교하게 조정할 수 있습니다.
