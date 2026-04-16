# EXP-179 Prompt Baseline Coverage Audit After Review Highlight Price Shorter Copy Off Profile

## 목표

- `EXP-178`까지 반영된 manifest 기준으로 coverage 분포를 다시 집계합니다.

## 실행

- `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-179 --experiment-title "Prompt Baseline Coverage Audit After Review Highlight Price Shorter Copy Off Profile" --artifact-name exp-179-prompt-baseline-coverage-audit-after-review-highlight-price-shorter-copy-off-profile.json`

artifact:

- `docs/experiments/artifacts/exp-179-prompt-baseline-coverage-audit-after-review-highlight-price-shorter-copy-off-profile.json`

## 결과

- `totalContexts=24`
- `option_match=11`
- `coverage_gap=12`
- `default_match=1`
- `exact_match=12`

`EXP-175` 대비 변화:

- `option_match=10 -> 11`
- `coverage_gap=13 -> 12`
- `exact_match=11 -> 12`

## 해석

1. `review / highlightPrice=true / shorterCopy=false / emphasizeRegion=false` 공백 1건이 실제로 메워졌습니다.
2. 남은 최상위 비지역 공백은 이제 `review / highlightPrice=true / shorterCopy=true` 한 건으로 좁혀졌습니다.
