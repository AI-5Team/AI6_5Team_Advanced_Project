# Test Scenario 180

## 목적

- `EXP-179` 이후 coverage 집계가 실제로 개선됐는지 확인합니다.

## 실행

- `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-179 --experiment-title "Prompt Baseline Coverage Audit After Review Highlight Price Shorter Copy Off Profile" --artifact-name exp-179-prompt-baseline-coverage-audit-after-review-highlight-price-shorter-copy-off-profile.json`

## 기대 결과

- `coverage_gap` 감소
- `option_match`, `exact_match` 증가

## 실제 결과

- `option_match=11`
- `coverage_gap=12`
- `exact_match=12`

## 판정

- 통과
