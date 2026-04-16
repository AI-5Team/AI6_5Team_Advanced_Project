# EXP-171 Prompt Baseline Coverage Audit After New Menu Highlight Price Shorter Copy Profile

## 목표

- `EXP-170`까지 반영된 manifest 기준으로 coverage 분포를 다시 집계합니다.

## 실행

- `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-171 --experiment-title "Prompt Baseline Coverage Audit After New Menu Highlight Price Shorter Copy Profile" --artifact-name exp-171-prompt-baseline-coverage-audit-after-new-menu-highlight-price-shorter-copy-profile.json`

artifact:

- `docs/experiments/artifacts/exp-171-prompt-baseline-coverage-audit-after-new-menu-highlight-price-shorter-copy-profile.json`

## 결과

- `totalContexts=24`
- `option_match=9`
- `coverage_gap=14`
- `default_match=1`
- `exact_match=10`

`EXP-167` 대비 변화:

- `option_match=8 -> 9`
- `coverage_gap=15 -> 14`
- `exact_match=9 -> 10`

## 해석

1. `new_menu highlightPrice=true + shorterCopy=true / emphasizeRegion=true` 공백 1건이 실제로 메워졌습니다.
2. 이제 비지역 `P2`는 `review` 2건만 남았습니다.
