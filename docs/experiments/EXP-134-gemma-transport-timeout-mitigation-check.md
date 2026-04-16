# EXP-134 Gemma Transport Timeout Mitigation Check

## 배경

- `EXP-128` repeatability에서는 `Gemma 4` 품질 자체보다 transport timeout이 더 큰 리스크로 보였습니다.
- 당시 `promotion_baseline_direct_transfer_to_review`, `promotion_baseline_principles_translated_to_review` 두 variant 모두 single run은 통과했지만 repeatability에서는 `The read operation timed out`로 `1/3 success`에 머물렀습니다.
- 현재 baseline 논의에서 중요한 질문은 두 가지였습니다.
  1. timeout이 지금도 같은 수준으로 재현되는가
  2. 된다면 timeout/retry 조정이 품질을 해치지 않고 운영 리스크를 줄이는가

## 목표

- prompt 자체는 그대로 두고 transport만 바꿔 `Gemma 4` timeout risk를 다시 확인합니다.
- 같은 prompt에서 아래 3개 profile을 비교합니다.
  - `default_60s_no_retry`
  - `timeout_90s_retry1`
  - `timeout_120s_retry1`

## 고정 조건

- source experiment: `EXP-128`
- source variant: `promotion_baseline_principles_translated_to_review`
- scenario: `scenario-restaurant-review-b-grade-real-photo`
- model: `models/gemma-4-31b-it`
- repeat: `3`

## 구현

### 1. harness 확장

- 파일: `services/worker/experiments/prompt_harness.py`
- `generate_copy_bundle_with_google_model_with_meta()`를 추가했습니다.
- 추가 정보:
  - `timeoutSec`
  - `maxRetries`
  - `retryBackoffSec`
  - `attemptCount`
  - `retriesUsed`
- 기본 `generate_copy_bundle_with_google_model()`은 새 함수를 래핑하는 형태로 유지해 기존 실험 경로를 깨지 않도록 했습니다.

### 2. 전용 비교 스크립트 추가

- 파일: `scripts/run_gemma_transport_profile_check.py`
- 동일 prompt/동일 모델에서 transport profile만 바꿔 repeatability를 비교합니다.

## 결과

artifact:
- `docs/experiments/artifacts/exp-134-gemma-transport-timeout-mitigation-check.json`

요약:

| profile | success | avg score | avg attempts | timeout fail |
|---|---:|---:|---:|---:|
| `default_60s_no_retry` | 3/3 | 100.0 | 1.0 | 0 |
| `timeout_90s_retry1` | 3/3 | 100.0 | 1.33 | 0 |
| `timeout_120s_retry1` | 3/3 | 100.0 | 1.0 | 0 |

sample hook:
- default:
  - `한 입 먹고 바로 기절함`
  - `한 입 먹자마자 기절각임`
- 90s/retry1:
  - `진짜 한 번 먹고 기억남`
  - `한 입 먹고 바로 기절함`
- 120s/retry1:
  - `한 입 먹고 바로 기절함`
  - `진심 한 입 먹고 기억남`

## 해석

1. 이번 세션에서는 과거의 timeout risk가 기본 60초 profile에서 재현되지 않았습니다.
2. 따라서 `Gemma 4는 항상 timeout 난다`고 일반화할 수는 없습니다.
3. 다만 `90초 / retry 1회` profile에서 평균 attempt가 `1.33`으로 기록됐습니다.
4. 이 말은 실제로 내부 retry가 한 번 작동했고, transport retry가 간헐적 보호장치로는 의미가 있다는 뜻입니다.
5. 반면 품질 지표는 세 profile 모두 `100.0`으로 같았습니다.
6. 즉 이번 실험의 결론은 `prompt 품질 개선`이 아니라 `transport risk는 간헐적이며 retry는 안전망으로 유효할 수 있다`입니다.

## 판단

- 현재 기준에서 `Gemma 4 main baseline` 자체를 바꿀 이유는 없습니다.
- 대신 운영 메모는 이렇게 정리하는 편이 맞습니다.
  - timeout risk는 여전히 관찰 대상
  - 하지만 이번 세션에서는 기본 60초도 안정적
  - retry는 상시 필수라기보다 sporadic guard

## 다음 액션 제안

1. 실제 runtime routing을 붙이기 전까지는 transport profile을 manifest `operationalChecks` 수준으로만 관리합니다.
2. 만약 이후 세션에서 timeout이 다시 반복되면:
   - `90초 / retry 1회`를 우선 operational fallback으로 고려합니다.
3. 지금 당장은 runtime provider routing 연결 또는 다음 baseline coverage 확장 쪽이 더 우선입니다.

## 관련 파일

- `services/worker/experiments/prompt_harness.py`
- `scripts/run_gemma_transport_profile_check.py`
- `packages/template-spec/manifests/prompt-baseline-v1.json`
