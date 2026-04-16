# EXP-43 Quick Action Visible Delta (highlightPrice)

## 1. 기본 정보

- 실험 ID: `EXP-43`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `서비스 본선 quick action visible delta`

## 2. 왜 이 작업을 했는가

- `EXP-41`에서 `shorterCopy`는 regenerate 결과에 실제 반영되도록 복구했습니다.
- 이제 같은 경로로 `highlightPrice`도 실제 `scenePlan`과 scene frame에 눈에 보이는 차이를 만드는지 확인해야 했습니다.

## 3. baseline

### 고정한 조건

1. 플로우: `web demo -> 프로젝트 생성 -> 실제 샘플 자산 업로드 -> generate -> regenerate`
2. 업종/목적/스타일: `restaurant / promotion / b_grade_fun`
3. 템플릿: `T02`
4. 자산: `docs/sample/음식사진샘플(규카츠).jpg`, `docs/sample/음식사진샘플(맥주).jpg`
5. 바뀐 변수: `changeSet.highlightPrice`만 변경

### 비교 대상

- baseline: `highlightPrice=false`
- variant: `highlightPrice=true`

## 4. 무엇을 바꿨는가

- `scripts/capture_quick_action_delta.mjs`를 일반화했습니다.
  - `--lever`
  - `--output-dir`
- 이번 실행은 `--lever highlightPrice`로 수행했습니다.
- `summary.json`에는 opening뿐 아니라 `benefit(scene s2)` primary text도 기록하도록 확장했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-43-quick-action-visible-delta-highlight-price/summary.json`
- `docs/experiments/artifacts/exp-43-quick-action-visible-delta-highlight-price/baseline-s2.png`
- `docs/experiments/artifacts/exp-43-quick-action-visible-delta-highlight-price/highlight-price-s2.png`

### baseline 대비 차이

- benefit primary text
  - baseline: `짧게 봐도 느낌이 전해집니다`
  - variant: `가격 메리트가 한눈에 보입니다`
- caption 2
  - baseline: `행사 포인트를 짧게 담았습니다`
  - variant: `성수동에서 가격이 먼저 보이도록 구성했습니다`
- 관찰
  - `s2` benefit scene에서 텍스트 방향이 감성형에서 가격 포인트형으로 바뀌었습니다.
  - scene frame 캡처에서도 첫 줄부터 가격 중심 문구가 눈에 띕니다.

### 확인된 것

1. `highlightPrice`는 현재 구현에서도 실제 regenerate delta를 만듭니다.
2. `shorterCopy`와 달리 opening/CTA는 그대로고, `benefit scene`에 변화가 집중됩니다.
3. 즉 이 quick action은 `scene별 목표가 다른 delta`를 만드는 방향으로 동작합니다.

## 6. 실패/제약

1. 지금 변화는 `가격 강조형 문구` 수준이지 실제 숫자 가격/할인율을 노출하는 수준은 아닙니다.
2. structured price 데이터가 없어서 `진짜 가격 배지`까지는 못 갔습니다.
3. 따라서 현재 `highlightPrice`는 방향은 맞지만 강도는 아직 약한 편입니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - `highlightPrice`는 zero-delta가 아니며, 실제 scene frame에도 반영됩니다.
  - 다만 현재 표현은 `가격 메리트` 수준이라, 더 강한 가격 중심 UX를 원하면 추후 copy/render 쪽 보강이 필요합니다.

## 8. 다음 액션

1. quick action 본선 우선순위는 이제 `업로드 보조 흐름`과 `첫 결과 생성 시간` 점검으로 넘어가는 편이 맞습니다.
2. `highlightPrice` 강도 강화는 structured offer/price 데이터가 들어올 때 다시 검토합니다.
