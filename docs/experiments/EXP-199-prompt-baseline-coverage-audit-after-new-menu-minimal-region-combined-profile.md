# EXP-199 Prompt Baseline Coverage Audit After New Menu Minimal Region Combined Profile

## 목표

- `EXP-198`까지 반영된 manifest 기준으로 coverage 분포를 다시 집계합니다.

## 실행

- `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-199 --experiment-title "Prompt Baseline Coverage Audit After New Menu Minimal Region Combined Profile" --artifact-name exp-199-prompt-baseline-coverage-audit-after-new-menu-minimal-region-combined-profile.json`

artifact:

- `docs/experiments/artifacts/exp-199-prompt-baseline-coverage-audit-after-new-menu-minimal-region-combined-profile.json`

## 결과

- `totalContexts=24`
- `option_match=16`
- `coverage_gap=7`
- `default_match=1`
- `exact_match=17`

`EXP-195` 대비 변화:

- `option_match=15 -> 16`
- `coverage_gap=8 -> 7`
- `exact_match=16 -> 17`

## 해석

1. 마지막 non-region `new_menu` combined 공백 1건이 실제로 메워졌습니다.
2. 남은 quick option gap은 모두 region emphasis `P3`입니다.

