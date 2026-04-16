# Test Scenario 156

## 제목

combined promotion profile 추가 후 prompt baseline coverage audit 재실행

## 목적

- `promotion_surface_lock_highlight_price_off_shorter_copy_off`가 실제 coverage gap을 줄였는지 확인합니다.

## 실행

1. `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-154 --experiment-title "Prompt Baseline Coverage Audit After Combined Promotion Profile" --artifact-name exp-154-prompt-baseline-coverage-audit-after-combined-promotion-profile.json`

## 기대 결과

- `option_match`가 기존보다 늘고, `coverage_gap`가 줄어야 합니다.

## 이번 실행 결과

- 이전:
  - `option_match = 4`
  - `coverage_gap = 19`
- 현재:
  - `option_match = 5`
  - `coverage_gap = 18`

## 판정

- combined promotion profile은 실제 coverage reduction으로 이어졌습니다.
