# Test Scenario 152

## 제목

P1 promotion profile 추가 후 prompt baseline coverage audit 재실행

## 목적

- `promotion_surface_lock_shorter_copy_off`, `promotion_surface_lock_highlight_price_off`가 실제 manifest coverage gap을 줄였는지 확인합니다.
- 기존 `EXP-141` 집계와 비교해 `option_match`, `coverage_gap` 변화를 확인합니다.

## 실행

1. compile
   - `python -m py_compile scripts/run_prompt_baseline_coverage_audit.py`
2. audit
   - `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-150 --experiment-title "Prompt Baseline Coverage Audit After P1 Promotions" --artifact-name exp-150-prompt-baseline-coverage-audit-after-p1-promotions.json`

## 기대 결과

- `option_match`가 기존보다 늘어야 합니다.
- `coverage_gap`가 기존보다 줄어야 합니다.

## 이번 실행 결과

- 이전:
  - `option_match = 2`
  - `coverage_gap = 21`
- 현재:
  - `option_match = 4`
  - `coverage_gap = 19`

## 판정

- 새 promotion option profile 2개는 실제 coverage reduction으로 이어졌습니다.
- 이번 audit 기준으로 가장 급한 promotion P1 공백은 해소된 것으로 봐도 됩니다.
