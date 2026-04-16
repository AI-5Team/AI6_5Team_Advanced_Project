# EXP-175 Prompt Baseline Coverage Audit After Review Shorter Copy Off Profile

## 목표

- `EXP-174`까지 반영된 manifest 기준으로 coverage 분포를 다시 집계합니다.

## 실행

- `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-175 --experiment-title "Prompt Baseline Coverage Audit After Review Shorter Copy Off Profile" --artifact-name exp-175-prompt-baseline-coverage-audit-after-review-shorter-copy-off-profile.json`

artifact:

- `docs/experiments/artifacts/exp-175-prompt-baseline-coverage-audit-after-review-shorter-copy-off-profile.json`

## 결과

- `totalContexts=24`
- `option_match=10`
- `coverage_gap=13`
- `default_match=1`
- `exact_match=11`

`EXP-171` 대비 변화:

- `option_match=9 -> 10`
- `coverage_gap=14 -> 13`
- `exact_match=10 -> 11`

## 해석

1. `review / shorterCopy=false / emphasizeRegion=false` 공백 1건이 실제로 메워졌습니다.
2. coverage gap은 이제 13건으로 줄었고, exact match는 11건까지 올라왔습니다.
3. 남은 최상위 비지역 공백은 `review highlightPrice=true` 축으로 수렴했습니다.
