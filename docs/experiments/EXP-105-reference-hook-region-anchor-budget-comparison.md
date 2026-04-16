# EXP-105 Reference hook region anchor budget comparison

## 1. 기본 정보

- 실험 ID: `EXP-105`
- 작성일: `2026-04-10`
- 작성자: Codex
- 관련 축: `final budget prompt / region anchor / Gemma 4 vs gpt-5-mini`

## 2. 왜 이 작업을 했는가

- `EXP-103`, `EXP-104`를 보면 두 모델 모두 길이 constraint는 잘 따르지만, region minimum slot을 놓치는 문제가 남았습니다.
- 그래서 이번에는 `region anchor + length budget`를 같이 고정한 prompt를 만들고, `Gemma 4`와 `gpt-5-mini`를 다시 붙였습니다.

## 3. 고정한 budget

1. `hook / benefit / urgency / cta` headline 길이 상한
2. `cta` 행동 단어 시작
3. 지역명은 primary headline에 넣지 않음
4. 지역명은 `captions 중 정확히 1개`, `지역 hashtag 정확히 1개`에만 넣도록 지시

## 4. 실행 결과

artifact:

- `docs/experiments/artifacts/exp-105-reference-hook-region-anchor-budget-comparison.json`

### Gemma 4

- score: `100.0`
- hook:
  - `오늘만 할인, 진짜 맞나요?`
- cta:
  - `방문하기`
- over-limit:
  - `s2`
- failed:
  - 없음

관찰:

- region anchor는 지켰습니다.
  - caption에 `성수동`
  - hashtag에 `#성수동맛집`
- 다만 benefit가 17자로 한 글자 넘으면서 `s2`만 over limit였습니다.

### GPT-5 Mini

- score: `92.9`
- hook:
  - `오늘만 규카츠 할인?`
- cta:
  - `방문 저장`
- over-limit:
  - 없음
- failed:
  - `region appears in fewer than required areas`

관찰:

- 길이 budget은 잘 지켰습니다.
- 하지만 region anchor를 `성수동` 대신 `서울숲 근처` 같은 표현으로 우회해 버렸습니다.
- hashtag에는 `#성수동맛집`이 들어갔지만 caption에는 exact region string이 없어서 평가 기준상 실패했습니다.

## 5. 해석

- 현재 기준으로는 `Gemma 4`가 region anchor를 더 충실하게 따릅니다.
- `gpt-5-mini`는 길이는 더 잘 맞추지만, 지역명 exact anchor는 더 자주 우회할 수 있습니다.
- 즉:
  - `Gemma 4`: region anchoring 강점
  - `gpt-5-mini`: length/CTA 직접성 강점

## 6. 결론

- 본선 prompt tuning 기준으로는 두 모델의 약점이 더 분명해졌습니다.
- `gpt-5-mini`는 `exact region token`을 더 직접적으로 강제해야 합니다.
- `Gemma 4`는 benefit headline만 한 단계 더 짧게 묶으면 바로 더 나아질 수 있습니다.

## 7. 다음 액션

1. `gpt-5-mini`
   - `caption 1개에 정확히 '{region}' 문자열을 포함하라`를 더 직접적으로 적습니다.
   - `서울숲 근처` 같은 우회 표현을 금지하는 제약을 추가합니다.
2. `Gemma 4`
   - benefit primary를 14자 안팎으로 한 단계 더 낮춰 봅니다.
3. 지금 기준의 우선순위
   - region 정확도 우선: `Gemma 4`
   - 짧고 직설적인 톤 우선: `gpt-5-mini`
