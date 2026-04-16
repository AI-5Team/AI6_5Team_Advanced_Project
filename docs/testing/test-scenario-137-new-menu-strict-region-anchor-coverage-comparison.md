# Test Scenario 137

## 제목

T01 new_menu strict region anchor coverage 비교

## 목적

- `T01 new_menu / friendly / emphasizeRegion=true`에서 strict baseline 원칙이 실제로 전이되는지 확인합니다.
- `Gemma 4`와 `gpt-5-mini` 중 누가 coverage candidate로 적합한지 봅니다.

## 고정 조건

- scenario: `scenario-cafe-new-menu-fixed`
- template: `T01`
- style: `friendly`
- quick options:
  - `highlightPrice=false`
  - `shorterCopy=false`
  - `emphasizeRegion=true`

## 실행

1. compile
   - `python -m py_compile services/worker/experiments/prompt_harness.py scripts/run_model_comparison_experiment.py scripts/run_prompt_repeatability_spot_check.py`
2. single run
   - `python scripts/run_model_comparison_experiment.py --experiment-id EXP-135`
3. repeatability
   - `python scripts/run_prompt_repeatability_spot_check.py --experiment-id EXP-135 --repeat 3 --model-names models/gemma-4-31b-it,gpt-5-mini`

## 기대 결과

- single run artifact에 `Gemma 4`, `gpt-5-mini` 결과가 모두 기록됩니다.
- repeatability artifact에 model별 `success_count`, `avg_score`, `all_runs_passed`가 기록됩니다.

## 이번 실행 결과

- artifact:
  - `docs/experiments/artifacts/exp-135-new-menu-strict-region-anchor-coverage-comparison.json`
  - `docs/experiments/artifacts/exp-135-repeatability.json`
- summary:
  - single run:
    - `Gemma 4`: `100.0`
    - `gpt-5-mini`: `100.0`
  - repeatability:
    - `Gemma 4`: `0/3`, `avg_score=0.0`, timeout 3회
    - `gpt-5-mini`: `3/3`, `avg_score=100.0`

## 판정

- `T01` strict coverage prompt 자체는 유효합니다.
- 다만 이번 세션에서 실용 후보는 `gpt-5-mini`이고, `Gemma 4`는 품질이 아니라 transport timeout 때문에 탈락했습니다.
