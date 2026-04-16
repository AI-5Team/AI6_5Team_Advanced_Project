# Test Scenario 176

## 목적

- `EXP-175` 이후 coverage 집계가 실제로 개선됐는지 확인합니다.

## 실행

- `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-175 --experiment-title "Prompt Baseline Coverage Audit After Review Shorter Copy Off Profile" --artifact-name exp-175-prompt-baseline-coverage-audit-after-review-shorter-copy-off-profile.json`

## 기대 결과

- `coverage_gap` 감소
- `option_match`, `exact_match` 증가

## 실제 결과

- `option_match=10`
- `coverage_gap=13`
- `exact_match=11`

## 판정

- 통과
