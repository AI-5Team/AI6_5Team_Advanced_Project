# EXP-222 Prompt Baseline Quick Option Gap Priority After Review Region Anchor Profiles

## 목표

- `EXP-221` coverage audit 이후 quick-option gap priority band가 실제로 0이 됐는지 확인합니다.

## 실행

- `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact "E:\\Codeit\\AI6_5Team_Advanced_Project\\docs\\experiments\\artifacts\\exp-221-prompt-baseline-coverage-audit-after-review-region-anchor-profiles.json" --experiment-id EXP-222 --experiment-title "Prompt Baseline Quick Option Gap Priority After Review Region Anchor Profiles" --artifact-name exp-222-prompt-baseline-quick-option-gap-priority-after-review-region-anchor-profiles.json`

artifact:

- `docs/experiments/artifacts/exp-222-prompt-baseline-quick-option-gap-priority-after-review-region-anchor-profiles.json`

## 결과

- `totalQuickOptionGaps=0`
- `bandCounts={}`

## 해석

1. quick-option 기준으로는 더 이상 우선순위 band를 매길 gap이 남아 있지 않습니다.
2. 다음 실험은 baseline 빈칸 메우기가 아니라, baseline 자체를 다시 비교하거나 운영 경계를 넓히는 방향으로 전환해야 합니다.
