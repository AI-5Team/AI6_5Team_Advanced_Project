# EXP-109 Strict anchor benefit budget repeatability

## 1. 기본 정보

- 실험 ID: `EXP-109`
- 작성일: `2026-04-10`
- 작성자: Codex
- 관련 축: `repeatability / Gemma 4 vs gpt-5-mini / strict prompt stability`

## 2. 왜 이 작업을 했는가

- `EXP-108` 한 번 결과만으로도 `Gemma 4 우위` 신호가 보였지만, 본선 후보 판단은 repeatability가 더 중요합니다.
- 그래서 같은 strict prompt를 기준으로 `Gemma 4`와 `gpt-5-mini`를 각 3회씩 다시 돌렸습니다.

## 3. 실행 조건

1. source experiment
   - `EXP-108`
2. repeat
   - 각 3회
3. 실행 스크립트
   - `scripts/run_prompt_repeatability_spot_check.py`

artifact:

- `docs/experiments/artifacts/exp-108-repeatability.json`

## 4. 요약 결과

### Gemma 4

- run count: `3`
- success count: `3`
- avg score: `100.0`
- avg hook length: `15.3`
- avg cta length: `9.3`
- all runs passed: `true`

관찰:

- hook가 3회 모두 `규카츠 할인, 오늘만 맞나요?`로 같았습니다.
- exact region slot도 모두 채웠습니다.
- CTA는 여전히 조금 길지만, 자동 평가 기준으로는 전부 통과했습니다.

### GPT-5 Mini

- run count: `3`
- success count: `3`
- avg score: `91.1`
- avg hook length: `11.0`
- avg cta length: `2.0`
- all runs passed: `false`

관찰:

- hook는 짧고 CTA도 매우 짧습니다.
- 1회차는 `region appears in fewer than required areas`와 `nearby location leaked into strict region budget`가 같이 발생했습니다.
- 2회차와 3회차도 `서울숲 근처`, `#서울숲근처`가 다시 섞여 leakage 실패가 남았습니다.

## 5. 자동 점수와 수동 해석

- `EXP-110` 패치 전에는 자동 점수가 이 leakage를 놓쳤습니다.
- 지금은 아래 경우가 자동 실패로 반영됩니다.
  1. `성수동`을 넣으면서 같은 caption에 `서울숲 근처`를 같이 붙이는 경우
  2. `#성수동` 외에 `#서울숲근처` 같은 hashtag를 같이 넣는 경우
- 이번 repeatability 결과에서 `gpt-5-mini`가 정확히 이 failure를 반복적으로 보여줬습니다.

## 6. 결론

- strict prompt 기준 repeatability까지 보면 현재 본선 baseline 후보는 `Gemma 4`가 더 타당합니다.
- `gpt-5-mini`는 톤과 길이는 매력적이지만, exact region anchor와 nearby-location leakage 억제에서 아직 불안정합니다.

## 7. 다음 액션

1. 현재 기준 main prompt model은 `Gemma 4`로 우선 유지합니다.
2. `gpt-5-mini`는 `짧은 hook 후보 생성`, `보조 아이디어 모델`처럼 제한된 역할로 보는 편이 맞습니다.
3. 다음엔 prompt를 더 깎기보다 `evaluation blind spot`을 줄이는 쪽이 필요합니다.
