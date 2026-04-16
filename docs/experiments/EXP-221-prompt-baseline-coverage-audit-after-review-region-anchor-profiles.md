# EXP-221 Prompt Baseline Coverage Audit After Review Region Anchor Profiles

## 목표

- review region emphasis 4개 profile을 manifest에 반영한 뒤 quick-option coverage가 실제로 모두 닫혔는지 확인합니다.

## 실행

- `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-221 --experiment-title "Prompt Baseline Coverage Audit After Review Region Anchor Profiles" --artifact-name exp-221-prompt-baseline-coverage-audit-after-review-region-anchor-profiles.json`

artifact:

- `docs/experiments/artifacts/exp-221-prompt-baseline-coverage-audit-after-review-region-anchor-profiles.json`

## 결과

- `totalContexts=24`
- `executionStatusCounts={ option_match: 23, default_match: 1 }`
- `gapClassCounts={ exact_match: 24 }`
- `recommendedActionCounts={ none: 24 }`

## 해석

1. 현재 quick-option catalog 24개 문맥이 모두 `exact_match`로 정리됐습니다.
2. `default_match=1`은 main baseline 문맥이고, 나머지 23개는 모두 option profile이 직접 매칭됩니다.
3. 즉 baseline manifest 기준으로는 더 이상 coverage hint나 scenario gap이 남아 있지 않습니다.
