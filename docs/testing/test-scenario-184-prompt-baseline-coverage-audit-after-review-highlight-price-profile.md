# Test Scenario 184

## 목적

- `EXP-183` 이후 coverage 집계가 실제로 개선됐는지 확인합니다.

## 실행

- `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-183 --experiment-title "Prompt Baseline Coverage Audit After Review Highlight Price Profile" --artifact-name exp-183-prompt-baseline-coverage-audit-after-review-highlight-price-profile.json`

## 기대 결과

- `coverage_gap` 감소
- `option_match`, `exact_match` 증가

## 실제 결과

- `option_match=12`
- `coverage_gap=11`
- `exact_match=13`

## 판정

- 통과
