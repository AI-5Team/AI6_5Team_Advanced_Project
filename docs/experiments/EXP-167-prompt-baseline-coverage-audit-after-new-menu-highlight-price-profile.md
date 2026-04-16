# EXP-167 Prompt Baseline Coverage Audit After New Menu Highlight Price Profile

## 목표

- `EXP-166`까지 반영된 manifest 기준으로 coverage 분포를 다시 집계합니다.

## 실행

- `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-167 --experiment-title "Prompt Baseline Coverage Audit After New Menu Highlight Price Profile" --artifact-name exp-167-prompt-baseline-coverage-audit-after-new-menu-highlight-price-profile.json`

artifact:

- `docs/experiments/artifacts/exp-167-prompt-baseline-coverage-audit-after-new-menu-highlight-price-profile.json`

## 결과

- `totalContexts=24`
- `option_match=8`
- `coverage_gap=15`
- `default_match=1`
- `exact_match=9`

`EXP-163` 대비 변화:

- `option_match=7 -> 8`
- `coverage_gap=16 -> 15`
- `exact_match=8 -> 9`

## 해석

1. `new_menu highlightPrice=true / emphasizeRegion=true` 공백 1건이 실제로 메워졌습니다.
2. 이제 `new_menu`에서 남은 최상위 비지역 공백은 `highlightPrice=true + shorterCopy=true` 조합 1건입니다.
