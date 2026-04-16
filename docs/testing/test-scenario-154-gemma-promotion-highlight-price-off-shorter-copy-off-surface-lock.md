# Test Scenario 154

## 제목

Gemma promotion highlightPrice=false + shorterCopy=false surface-lock prompt 비교 및 repeatability 검증

## 목적

- `promotion / T02 / b_grade_fun / highlightPrice=false / shorterCopy=false / emphasizeRegion=false` 조건에서 `Gemma 4` baseline prompt와 combined surface-lock candidate를 비교합니다.
- Google transport는 `90초 / retry 1회`로 고정합니다.

## 실행

1. compile
   - `python -m py_compile services/worker/experiments/prompt_harness.py scripts/run_google_prompt_experiment_with_transport.py scripts/run_google_prompt_variant_repeatability_with_transport.py`
2. single run
   - `python scripts/run_google_prompt_experiment_with_transport.py --experiment-id EXP-152 --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`
3. repeatability
   - `python scripts/run_google_prompt_variant_repeatability_with_transport.py --experiment-id EXP-152 --repeat 3 --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`

## 기대 결과

- baseline과 candidate 모두 transport timeout 없이 응답해야 합니다.
- candidate는 combined option profile 후보로 쓸 수 있을 만큼 안정적이어야 합니다.

## 이번 실행 결과

- single run:
  - baseline `100.0`
  - candidate `100.0`
- repeatability:
  - baseline `3/3`, `avg_score 100.0`, `all_runs_passed=true`
  - candidate `3/3`, `avg_score 100.0`, `all_runs_passed=true`

## 판정

- 이번 combined 조합은 candidate profile 승격 가능한 상태입니다.
- candidate는 점수 우위보다도 `highlightPrice=false + shorterCopy=false` 조합을 명시적으로 고정한다는 점에서 가치가 있습니다.
