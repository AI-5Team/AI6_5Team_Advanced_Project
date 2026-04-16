# EXP-160 Prompt Baseline Coverage Audit After Promotion Region Anchor Profile

## 목표

- `EXP-159`까지 반영된 manifest 기준으로 coverage 분포가 어떻게 바뀌는지 다시 집계합니다.

## 실행

- `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-160 --experiment-title "Prompt Baseline Coverage Audit After Promotion Region Anchor Profile" --artifact-name exp-160-prompt-baseline-coverage-audit-after-promotion-region-anchor-profile.json`

artifact:

- `docs/experiments/artifacts/exp-160-prompt-baseline-coverage-audit-after-promotion-region-anchor-profile.json`

## 결과

- `totalContexts=24`
- `option_match=6`
- `coverage_gap=17`
- `default_match=1`
- `exact_match=7`

`EXP-154` 대비 변화:

- `option_match=5 -> 6`
- `coverage_gap=18 -> 17`
- `exact_match=6 -> 7`

## 해석

1. 이번 profile 추가로 promotion `P3` 공백 1건이 실제로 줄었습니다.
2. promotion에서 남은 region-emphasis gap은 이제 3건입니다.
3. 전체 최상위 미해결 축은 여전히 `new_menu/review P2` 쪽입니다.
