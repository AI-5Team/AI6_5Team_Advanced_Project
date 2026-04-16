# Test Scenario 150

## 제목

Gemma promotion highlightPrice=false surface-lock prompt 비교 및 repeatability 검증

## 목적

- `promotion / T02 / b_grade_fun / highlightPrice=false / shorterCopy=true / emphasizeRegion=false` 조건에서 `Gemma 4` baseline prompt와 `surface-lock` candidate를 비교합니다.
- Google transport는 `90초 / retry 1회`로 고정해 transport와 prompt를 분리합니다.

## 실행

1. compile
   - `python -m py_compile services/worker/experiments/prompt_harness.py scripts/run_google_prompt_experiment_with_transport.py scripts/run_google_prompt_variant_repeatability_with_transport.py`
2. single run
   - `python scripts/run_google_prompt_experiment_with_transport.py --experiment-id EXP-148 --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`
3. repeatability
   - `python scripts/run_google_prompt_variant_repeatability_with_transport.py --experiment-id EXP-148 --repeat 3 --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`

## 기대 결과

- baseline과 candidate 모두 transport timeout 없이 응답해야 합니다.
- candidate는 `highlightPrice=false`와 strict region guard를 동시에 만족하는 option profile 후보여야 합니다.

## 이번 실행 결과

- single run:
  - baseline `100.0`
  - candidate `100.0`
- repeatability:
  - baseline `3/3`, `avg_score 100.0`, `all_runs_passed=true`
  - candidate `3/3`, `avg_score 100.0`, `all_runs_passed=true`

## 판정

- 이번 축은 `90초 / retry 1회` 기준으로 profile 승격 가능한 상태입니다.
- candidate는 baseline보다 점수 우위가 크다기보다, `가격 비강조 + nearby leakage 금지` 제약을 명시적으로 고정할 수 있는 prompt variant라는 점에서 승격 가치가 있습니다.
