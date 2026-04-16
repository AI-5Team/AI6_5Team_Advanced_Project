# EXP-102 Reference hook pack repeatability spot check

## 1. 기본 정보

- 실험 ID: `EXP-102`
- 작성일: `2026-04-10`
- 작성자: Codex
- 관련 축: `repeatability / model stability / hook guidance`

## 2. 왜 이 작업을 했는가

- `EXP-100`, `EXP-101`까지로 reference hook guidance가 유효하고, `Gemma 4`와 `gpt-5-mini`가 상위권이라는 신호는 잡았습니다.
- 하지만 본선에 가까운 모델을 고르려면 `한 번 잘 나온 결과`보다 `여러 번 돌려도 비슷하게 나오는가`가 더 중요합니다.
- 이번 spot check는 `EXP-101`의 same guidance를 고정하고, `Gemma 4`와 `gpt-5-mini`를 각 3회씩 다시 돌려 안정성을 빠르게 보는 목적입니다.

## 3. 실행 조건

1. source experiment
   - `EXP-101`
2. 고정 prompt
   - `fixed_reference_hook_pack_guidance`
3. 비교 모델
   - `models/gemma-4-31b-it`
   - `gpt-5-mini`
4. 반복 횟수
   - 각 3회

## 4. 실행 스크립트

- `scripts/run_prompt_repeatability_spot_check.py`

artifact:

- `docs/experiments/artifacts/exp-102-reference-hook-pack-repeatability-spot-check.json`

## 5. 요약 결과

### Gemma 4

- run count: `3`
- success count: `2`
- avg score: `66.7`
- avg hook length: `16.0`
- avg cta length: `13.0`
- avg over-limit scene count: `1.0`

관찰:

- 성공한 2회에서는 hook가 거의 동일하게 유지됐습니다.
- 즉 hook 표현 자체는 꽤 안정적입니다.
- 다만 `urgency`가 두 번 모두 over limit였고, CTA도 `지금 바로 위치 확인하기`처럼 길게 나왔습니다.
- 3번째 run은 timeout이 났습니다.

### GPT-5 Mini

- run count: `3`
- success count: `3`
- avg score: `97.6`
- avg hook length: `14.3`
- avg cta length: `8.0`
- avg over-limit scene count: `1.0`

관찰:

- 세 번 모두 호출은 성공했습니다.
- hook/CTA는 Gemma보다 짧고 직접적이었습니다.
- 다만 run마다 결과가 꽤 흔들렸습니다.
  - run 1: `오늘만 규카츠·맥주 할인?`
  - run 2: `오늘만 규카츠+맥주 할인가?`
  - run 3: `성수동에서 이거 보셨나요?`
- run 2에서는 region repeat 초과가 다시 발생했습니다.
- 반면 run 3은 over-limit scene이 0으로 가장 좋았습니다.

## 6. 해석

### Gemma 4

- 장점:
  - hook 문구 구조가 덜 흔들립니다.
  - 동일한 방향의 카피가 반복됩니다.
- 리스크:
  - CTA/urgency가 길어지는 경향
  - 호출 latency와 timeout 리스크

### GPT-5 Mini

- 장점:
  - CTA와 hook가 더 짧고 광고 톤이 직접적입니다.
  - 호출 성공률은 더 좋았습니다.
- 리스크:
  - run-to-run variation이 더 큽니다.
  - region repeat나 scene length가 일부 run에서 다시 튈 수 있습니다.

## 7. 지금 기준의 판단

- `Gemma 4`는 `카피 톤의 일관성` 쪽이 강합니다.
- `gpt-5-mini`는 `짧고 공격적인 광고 카피` 쪽이 강합니다.
- 하지만 둘 다 아직 완전한 본선 답은 아닙니다.
  - Gemma 4는 길이/timeout 리스크
  - gpt-5-mini는 변동성 리스크

## 8. 다음 액션

1. `gpt-5-mini`
   - region repeat와 scene length를 더 직접적으로 묶는 output constraint를 한 단계 추가합니다.
2. `Gemma 4`
   - CTA/urgency 길이 상한을 더 직접적으로 넣고, timeout 여부를 한 번 더 확인합니다.
3. 본선 후보 판단은 지금 단계에서 이렇게 정리합니다.
   - 짧고 광고스러운 톤 우선: `gpt-5-mini`
   - 문구 구조 일관성 우선: `Gemma 4`

## 9. 결론

- 모델을 `어떻게 깎아내느냐` 기준으로 보면, 지금은 단순한 모델 우열보다 `각 모델이 어디서 흔들리는지`가 더 중요합니다.
- 즉 다음은 모델 교체보다 `모델별 약점을 직접 묶는 constraint tuning`으로 가는 편이 맞습니다.
