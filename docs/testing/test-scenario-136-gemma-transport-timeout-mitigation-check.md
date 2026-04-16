# Test Scenario 136

## 제목

Gemma 4 review transfer prompt에서 timeout/retry transport profile 비교

## 목적

- `EXP-128`에서 관찰된 Gemma 4 timeout risk가 지금도 재현되는지 다시 확인합니다.
- prompt는 고정하고 transport만 바꿨을 때 품질과 성공률이 유지되는지 봅니다.

## 고정 조건

- source experiment: `EXP-128`
- source variant: `promotion_baseline_principles_translated_to_review`
- model: `models/gemma-4-31b-it`
- repeat: `3`

## 실행

1. compile
   - `python -m py_compile services/worker/experiments/prompt_harness.py scripts/run_gemma_transport_profile_check.py`
2. transport profile check
   - `python scripts/run_gemma_transport_profile_check.py --experiment-id EXP-128 --variant-id promotion_baseline_principles_translated_to_review --repeat 3 --api-key-env GEMINI_API_KEY`

## 비교 profile

- `default_60s_no_retry`
- `timeout_90s_retry1`
- `timeout_120s_retry1`

## 기대 결과

- 각 profile별 `success_count`, `timeout_fail_count`, `avg_score`, `avg_attempt_count`가 artifact에 기록됩니다.
- retry profile에서는 필요 시 `attemptCount > 1`이 관찰될 수 있습니다.

## 이번 실행 결과

- artifact:
  - `docs/experiments/artifacts/exp-134-gemma-transport-timeout-mitigation-check.json`
- summary:
  - `default_60s_no_retry`: `3/3`, `avg_score=100.0`, `avg_attempt_count=1.0`
  - `timeout_90s_retry1`: `3/3`, `avg_score=100.0`, `avg_attempt_count=1.33`
  - `timeout_120s_retry1`: `3/3`, `avg_score=100.0`, `avg_attempt_count=1.0`

## 판정

- 이번 세션에서는 기본 60초 profile도 timeout 없이 통과했습니다.
- 다만 `90초 / retry 1회` profile은 실제 retry가 한 번 작동한 흔적이 남았습니다.
- 따라서 retry는 상시 필수라기보다 간헐적 transport guard로 해석합니다.
