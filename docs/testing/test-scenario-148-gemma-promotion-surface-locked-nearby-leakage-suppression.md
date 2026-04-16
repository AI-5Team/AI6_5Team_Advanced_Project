# Test Scenario 148

## 제목

Gemma promotion surface-lock prompt 비교 및 repeatability 검증

## 목적

- `promotion / T02 / b_grade_fun / highlightPrice=true / shorterCopy=false / emphasizeRegion=false` 조건에서 `Gemma 4` baseline prompt와 `surface-lock` candidate를 비교합니다.
- Google transport는 `90초 / retry 1회`로 고정해 transport와 prompt를 분리합니다.

## 실행

1. compile
   - `python -m py_compile services/worker/experiments/prompt_harness.py scripts/run_google_prompt_experiment_with_transport.py scripts/run_google_prompt_variant_repeatability_with_transport.py`
2. single run
   - `python scripts/run_google_prompt_experiment_with_transport.py --experiment-id EXP-146 --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`
3. repeatability
   - `python scripts/run_google_prompt_variant_repeatability_with_transport.py --experiment-id EXP-146 --repeat 3 --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`

## 기대 결과

- baseline과 candidate 모두 transport timeout 없이 응답해야 합니다.
- repeatability에서는 baseline보다 candidate가 nearby leakage를 더 안정적으로 억제해야 합니다.

## 이번 실행 결과

- single run:
  - baseline `100.0`
  - candidate `100.0`
- repeatability:
  - baseline `3/3`, `avg_score 97.8`, `all_runs_passed=false`
  - candidate `3/3`, `avg_score 100.0`, `all_runs_passed=true`

## 판정

- 이번 candidate는 `Gemma 4` 기준 `promotion strict anchor` 축에서 실질적인 개선으로 봐도 됩니다.
- transport를 고정했을 때, baseline에 남아 있던 nearby leakage를 surface-lock prompt가 repeatability 수준에서 제거했습니다.
