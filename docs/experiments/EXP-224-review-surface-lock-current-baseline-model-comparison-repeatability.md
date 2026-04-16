# EXP-224 Review Surface Lock Current Baseline Model Comparison Repeatability

## 배경

- `EXP-223` single run에서는 Gemma 4와 `gpt-5-mini`가 둘 다 `100.0`을 기록했습니다.
- 하지만 Gemma 4 latency가 이미 `59초` 수준이었기 때문에, 실제 운영 판단에는 기본 transport repeatability를 같이 봐야 했습니다.

## 목표

- `EXP-223`과 동일한 fixed prompt / 동일한 두 모델로 3회 반복 실행합니다.
- 품질 점수보다 먼저, 기본 transport에서 어느 쪽이 실제로 재현 가능한지 확인합니다.

## 실행

- inline runner로 `EXP-223` model comparison을 `3회` 반복 실행

artifact:

- `docs/experiments/artifacts/exp-224-review-surface-lock-current-baseline-model-comparison-repeatability.json`

## 결과

### 요약

| model | pass | avg_score | avg_latency_ms | failed union |
|---|---:|---:|---:|---|
| Gemma 4 | `0/3` | `0.0` | `60278.7` | `google model transport failed after 1 attempt(s): The read operation timed out` |
| GPT-5 Mini | `3/3` | `100.0` | `5233.7` | 없음 |

### hook / cta 샘플

- Gemma 4
  - 모든 run이 timeout이라 결과 없음
- GPT-5 Mini hooks
  - `한 번 먹고 기억나요`
  - `한 번 먹고 기억남`
  - `한 번 먹고 기억남`
- GPT-5 Mini cta
  - `방문해보세요`
  - `방문해보기`
  - `방문해보기`

## 해석

1. `현재 review surface-lock prompt`는 품질 single run 기준으로는 양쪽 모델이 모두 통과할 수 있습니다.
2. 하지만 기본 transport repeatability까지 포함하면 결과는 완전히 갈립니다.
3. Gemma 4는 같은 prompt에서 3회 연속 timeout으로 실질적 fallback 후보가 되지 못했습니다.
4. `gpt-5-mini`는 같은 조건에서 `3/3 pass`와 약 `5.2초` 평균 latency를 유지했습니다.

## 결론

- review fallback 현재 분리는 `Gemma가 못 써서`라기보다, `기본 transport repeatability까지 포함하면 gpt-5-mini가 훨씬 실용적이라서`라는 쪽이 더 정확합니다.
- 즉 review lane에서 `gpt-5-mini` 유지 판단은 여전히 타당합니다.
- 반대로 Gemma 4를 review current prompt에 다시 올려보려면, 다음에는 prompt 수정이 아니라 `timeout/retry transport 조건`을 붙인 운영성 검증이 먼저입니다.
