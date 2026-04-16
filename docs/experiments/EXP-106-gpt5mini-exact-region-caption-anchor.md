# EXP-106 GPT-5 Mini exact region caption anchor

## 1. 기본 정보

- 실험 ID: `EXP-106`
- 작성일: `2026-04-10`
- 작성자: Codex
- 관련 축: `gpt-5-mini / exact region anchor / nearby-location leakage`

## 2. 왜 이 작업을 했는가

- `EXP-105`에서 `gpt-5-mini`는 길이 budget은 잘 맞췄지만, caption에서 `성수동` 대신 `서울숲 근처`로 우회하는 문제가 남았습니다.
- 그래서 이번에는 `strict region anchor` baseline 위에 `정확히 '성수동' 문자열을 caption 1개와 hashtag 1개에 넣으라`는 제약을 더 직접적으로 얹었습니다.

## 3. 비교축

1. baseline
   - `fixed_reference_hook_region_anchor_budget_openai`
2. candidate
   - `reference_hook_exact_region_caption_anchor_openai`

## 4. 추가한 constraint

1. `captions`
   - 정확히 1개 caption에 문자열 `성수동`을 그대로 1회 포함
2. `captions`
   - `서울숲 근처`, `서울숲 인근`, `성수역`, `근처`, `동네` 같은 우회 표현 금지
3. `hashtags`
   - 지역 hashtag는 정확히 1개
   - 그 hashtag는 `성수동` 문자열을 그대로 포함

## 5. 실행 결과

artifact:

- `docs/experiments/artifacts/exp-106-gpt-5-mini-prompt-lever-experiment-exact-region-caption-anchor.json`

### baseline

- score: `100.0`
- hook:
  - `오늘 안 오면 손해!`
- cta:
  - `방문 지금`
- over-limit:
  - 없음

관찰:

- 자동 평가 기준에서는 이미 통과했습니다.
- 다만 caption이 `성수동 서울숲 근처, 규카츠+맥주 오늘만 할인!`처럼 exact region 뒤에 nearby landmark를 같이 붙였습니다.

### candidate

- score: `100.0`
- hook:
  - `오늘만 규카츠 반값?`
- cta:
  - `방문 확인`
- over-limit:
  - 없음

관찰:

- exact region slot은 채웠습니다.
- 하지만 caption이 `성수동 서울숲 근처, 오늘만 할인 놓치지 마세요.`처럼 여전히 nearby landmark를 함께 썼습니다.
- 즉 `성수동 exact string`을 넣게 만드는 데는 성공했지만, `서울숲 근처` 같은 보조 위치 표현까지 제거하진 못했습니다.

## 6. 해석

- `gpt-5-mini`는 exact region hit 자체는 만들 수 있습니다.
- 다만 현재 prompt만으로는 `성수동`을 넣으면서 동시에 `서울숲 근처`도 덧붙이는 경향이 남습니다.
- 더 중요한 점은 현재 자동 평가기가 `성수동`의 slot/min-repeat만 세고, nearby landmark leakage 자체는 실패로 잡지 않는다는 것입니다.

## 7. 결론

- 이번 실험은 `gpt-5-mini`가 region slot 자체를 맞출 수 있다는 점은 보여줬습니다.
- 하지만 PM 관점의 `exact region anchor` 기준으로 보면 아직 미완입니다.
- 즉 `prompt 강화`만으로는 부족하고, 다음 둘 중 하나가 필요합니다.
  1. nearby landmark blacklist를 평가기로도 잡기
  2. 후처리 validation에서 `서울숲 근처`류를 별도 reject하기

## 8. 다음 액션

1. `EXP-109` repeatability에서 이 nearby-location leakage가 반복되는지 확인합니다.
2. 자동 score와 수동 해석을 분리해서 기록합니다.
3. 본선 기준 후보를 고를 때는 `정확한 지역 anchor`를 더 잘 지키는 모델을 우선합니다.

## 9. 평가기 보강 후 메모

- `EXP-110` 패치 후 같은 실험을 다시 실행하니 baseline은 `86.7`, candidate는 `93.3`으로 내려갔습니다.
- 이유는 두 variant 모두 `서울숲 근처` leakage가 자동 실패로 잡혔기 때문입니다.
- 즉 이 실험의 현재 해석은 `exact region slot은 복구 가능하지만, nearby-location leakage는 아직 해결되지 않음`입니다.
