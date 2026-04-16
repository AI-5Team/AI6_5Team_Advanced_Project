# EXP-183 Prompt Baseline Coverage Audit After Review Highlight Price Profile

## 목표

- `EXP-182`까지 반영된 manifest 기준으로 coverage 분포를 다시 집계합니다.

## 실행

- `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-183 --experiment-title "Prompt Baseline Coverage Audit After Review Highlight Price Profile" --artifact-name exp-183-prompt-baseline-coverage-audit-after-review-highlight-price-profile.json`

artifact:

- `docs/experiments/artifacts/exp-183-prompt-baseline-coverage-audit-after-review-highlight-price-profile.json`

## 결과

- `totalContexts=24`
- `option_match=12`
- `coverage_gap=11`
- `default_match=1`
- `exact_match=13`

`EXP-179` 대비 변화:

- `option_match=11 -> 12`
- `coverage_gap=12 -> 11`
- `exact_match=12 -> 13`

## 해석

1. 마지막 비지역 `review highlightPrice=true / shorterCopy=true` 공백 1건이 실제로 메워졌습니다.
2. quick option coverage gap은 11건까지 줄었고, exact match는 13건까지 올라왔습니다.
3. 남은 gap은 모두 `emphasizeRegion`이 포함된 `P3` 계열입니다.
