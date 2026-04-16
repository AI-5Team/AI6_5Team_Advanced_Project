# EXP-163 Prompt Baseline Coverage Audit After New Menu Shorter Copy Profile

## 목표

- `EXP-162`까지 반영된 manifest 기준으로 coverage 분포를 다시 집계합니다.

## 실행

- `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-163 --experiment-title "Prompt Baseline Coverage Audit After New Menu Shorter Copy Profile" --artifact-name exp-163-prompt-baseline-coverage-audit-after-new-menu-shorter-copy-profile.json`

artifact:

- `docs/experiments/artifacts/exp-163-prompt-baseline-coverage-audit-after-new-menu-shorter-copy-profile.json`

## 결과

- `totalContexts=24`
- `option_match=7`
- `coverage_gap=16`
- `default_match=1`
- `exact_match=8`

`EXP-160` 대비 변화:

- `option_match=6 -> 7`
- `coverage_gap=17 -> 16`
- `exact_match=7 -> 8`

## 해석

1. `new_menu shorterCopy=true` 공백 1건이 실제로 메워졌습니다.
2. 전체 coverage는 한 칸 더 줄었고, `new_menu` 축의 추천 정확도도 올라갔습니다.
