# EXP-187 Prompt Baseline Coverage Audit After New Menu Minimal Region Profile

## 목표

- `EXP-186`까지 반영된 manifest 기준으로 coverage 분포를 다시 집계합니다.

## 실행

- `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-187 --experiment-title "Prompt Baseline Coverage Audit After New Menu Minimal Region Profile" --artifact-name exp-187-prompt-baseline-coverage-audit-after-new-menu-minimal-region-profile.json`

artifact:

- `docs/experiments/artifacts/exp-187-prompt-baseline-coverage-audit-after-new-menu-minimal-region-profile.json`

## 결과

- `totalContexts=24`
- `option_match=13`
- `coverage_gap=10`
- `default_match=1`
- `exact_match=14`

`EXP-183` 대비 변화:

- `option_match=12 -> 13`
- `coverage_gap=11 -> 10`
- `exact_match=13 -> 14`

## 해석

1. `new_menu / emphasizeRegion=false / no extra quick option` 공백 1건이 실제로 메워졌습니다.
2. 남은 non-region gap은 `shorterCopy=true`, `highlightPrice=true`, 그리고 combined 1건으로 재정렬됐습니다.

