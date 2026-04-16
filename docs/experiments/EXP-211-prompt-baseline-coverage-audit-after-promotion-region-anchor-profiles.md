# EXP-211 Prompt Baseline Coverage Audit After Promotion Region Anchor Profiles

## 목표

- `EXP-202`, `EXP-206`, `EXP-210`까지 반영된 manifest 기준으로 coverage 분포를 다시 집계합니다.

## 실행

- `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-211 --experiment-title "Prompt Baseline Coverage Audit After Promotion Region Anchor Profiles" --artifact-name exp-211-prompt-baseline-coverage-audit-after-promotion-region-anchor-profiles.json`

artifact:

- `docs/experiments/artifacts/exp-211-prompt-baseline-coverage-audit-after-promotion-region-anchor-profiles.json`

## 결과

- `totalContexts=24`
- `option_match=19`
- `coverage_gap=4`
- `default_match=1`
- `exact_match=20`

`EXP-199` 대비 변화:

- `option_match=16 -> 19`
- `coverage_gap=7 -> 4`
- `exact_match=17 -> 20`

## 해석

1. 남아 있던 promotion region gap 3건이 모두 실제 coverage에서 빠졌습니다.
2. 이제 남은 quick option gap은 `review / emphasizeRegion=true` 4건뿐입니다.

