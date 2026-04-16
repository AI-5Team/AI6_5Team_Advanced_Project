# EXP-195 Prompt Baseline Coverage Audit After New Menu Minimal Region Shorter And Highlight Profiles

## 목표

- `EXP-190`, `EXP-194`까지 반영된 manifest 기준으로 coverage 분포를 다시 집계합니다.

## 실행

- `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-195 --experiment-title "Prompt Baseline Coverage Audit After New Menu Minimal Region Shorter and Highlight Profiles" --artifact-name exp-195-prompt-baseline-coverage-audit-after-new-menu-minimal-region-shorter-and-highlight-profiles.json`

artifact:

- `docs/experiments/artifacts/exp-195-prompt-baseline-coverage-audit-after-new-menu-minimal-region-shorter-and-highlight-profiles.json`

## 결과

- `totalContexts=24`
- `option_match=15`
- `coverage_gap=8`
- `default_match=1`
- `exact_match=16`

`EXP-187` 대비 변화:

- `option_match=13 -> 15`
- `coverage_gap=10 -> 8`
- `exact_match=14 -> 16`

## 해석

1. `new_menu / shorterCopy=true / emphasizeRegion=false`와 `new_menu / highlightPrice=true / emphasizeRegion=false` 두 공백이 실제로 메워졌습니다.
2. 비지역 quick option gap은 이제 combined 1건만 남았고, 나머지는 region emphasis `P3`입니다.

