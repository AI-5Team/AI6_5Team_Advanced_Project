# Test Scenario 145

## 제목

promotion highlightPrice=false coverage candidate 비교 및 repeatability 검증

## 목적

- `promotion / T02 / b_grade_fun / highlightPrice=false / shorterCopy=true / emphasizeRegion=false` 단일 토글 gap이 실제 option profile 후보인지 확인합니다.

## 실행

1. compile
   - `python -m py_compile services/worker/experiments/prompt_harness.py`
2. model comparison
   - `python scripts/run_model_comparison_experiment.py --experiment-id EXP-143`
3. repeatability
   - `python scripts/run_prompt_repeatability_spot_check.py --experiment-id EXP-143 --repeat 3 --model-names models/gemma-4-31b-it,gpt-5-mini`

## 기대 결과

- single run:
  - 최소 한 모델은 strict baseline coverage 후보로 통과 여부를 보여야 합니다.
- repeatability:
  - single-run winner가 실제 profile 승격 후보가 될 만큼 재현되는지 확인해야 합니다.

## 이번 실행 결과

- `python -m py_compile services/worker/experiments/prompt_harness.py` 통과
- single run:
  - `Gemma 4 = 100.0`
  - `gpt-5-mini = 86.7`
- repeatability:
  - `Gemma 4 = success 0/3`, 모두 transport timeout
  - `gpt-5-mini = success 3/3`, `avg_score 86.7`, `all_runs_passed=false`

## 판정

- 이번 후보는 아직 option profile 승격 조건을 만족하지 못했습니다.
- single-run pass만으로는 부족했고, repeatability에서 `Gemma 4`의 transport instability와 `gpt-5-mini`의 quality shortfall이 함께 드러났습니다.
