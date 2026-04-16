# EXP-188 Prompt Baseline Quick Option Gap Priority After New Menu Minimal Region Profile

## 목표

- `EXP-187` audit 기준으로 다음 quick option gap 우선순위를 다시 계산합니다.

## 실행

- `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact E:\\Codeit\\AI6_5Team_Advanced_Project\\docs\\experiments\\artifacts\\exp-187-prompt-baseline-coverage-audit-after-new-menu-minimal-region-profile.json --experiment-id EXP-188 --experiment-title "Prompt Baseline Quick Option Gap Priority After New Menu Minimal Region Profile" --artifact-name exp-188-prompt-baseline-quick-option-gap-priority-after-new-menu-minimal-region-profile.json`

artifact:

- `docs/experiments/artifacts/exp-188-prompt-baseline-quick-option-gap-priority-after-new-menu-minimal-region-profile.json`

## 결과

- `totalQuickOptionGaps=10`
- `bandCounts={ P2: 2, P3: 8 }`

top candidate:

1. `new_menu / highlightPrice=false / shorterCopy=true / emphasizeRegion=false`
2. `new_menu / highlightPrice=true / shorterCopy=false / emphasizeRegion=false`

## 해석

1. minimal anchor base profile이 생기면서, 남은 `new_menu` 비지역 공백 두 건이 다시 `P2`로 올라왔습니다.
2. 즉 다음 단계는 region 연구가 아니라 같은 minimal anchor 계열의 단일 토글 두 건을 닫는 것이 맞습니다.

