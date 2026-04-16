# EXP-196 Prompt Baseline Quick Option Gap Priority After New Menu Minimal Region Shorter And Highlight Profiles

## 목표

- `EXP-195` audit 기준으로 남은 quick option gap 우선순위를 다시 계산합니다.

## 실행

- `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact E:\\Codeit\\AI6_5Team_Advanced_Project\\docs\\experiments\\artifacts\\exp-195-prompt-baseline-coverage-audit-after-new-menu-minimal-region-shorter-and-highlight-profiles.json --experiment-id EXP-196 --experiment-title "Prompt Baseline Quick Option Gap Priority After New Menu Minimal Region Shorter and Highlight Profiles" --artifact-name exp-196-prompt-baseline-quick-option-gap-priority-after-new-menu-minimal-region-shorter-and-highlight-profiles.json`

artifact:

- `docs/experiments/artifacts/exp-196-prompt-baseline-quick-option-gap-priority-after-new-menu-minimal-region-shorter-and-highlight-profiles.json`

## 결과

- `totalQuickOptionGaps=8`
- `bandCounts={ P2: 1, P3: 7 }`

top candidate:

1. `new_menu / highlightPrice=true / shorterCopy=true / emphasizeRegion=false`

## 해석

1. non-region 축에서는 combined 1건만 남았습니다.
2. 이 combined를 닫으면 남는 gap은 모두 region emphasis `P3`만 됩니다.

