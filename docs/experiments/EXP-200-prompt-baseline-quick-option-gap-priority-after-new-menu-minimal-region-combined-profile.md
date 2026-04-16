# EXP-200 Prompt Baseline Quick Option Gap Priority After New Menu Minimal Region Combined Profile

## 목표

- `EXP-199` audit 기준으로 남은 quick option gap 우선순위를 다시 계산합니다.

## 실행

- `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact E:\\Codeit\\AI6_5Team_Advanced_Project\\docs\\experiments\\artifacts\\exp-199-prompt-baseline-coverage-audit-after-new-menu-minimal-region-combined-profile.json --experiment-id EXP-200 --experiment-title "Prompt Baseline Quick Option Gap Priority After New Menu Minimal Region Combined Profile" --artifact-name exp-200-prompt-baseline-quick-option-gap-priority-after-new-menu-minimal-region-combined-profile.json`

artifact:

- `docs/experiments/artifacts/exp-200-prompt-baseline-quick-option-gap-priority-after-new-menu-minimal-region-combined-profile.json`

## 결과

- `totalQuickOptionGaps=7`
- `bandCounts={ P3: 7 }`

remaining gaps:

1. `promotion / highlightPrice=false / shorterCopy=true / emphasizeRegion=true`
2. `promotion / highlightPrice=true / shorterCopy=false / emphasizeRegion=true`
3. `promotion / highlightPrice=true / shorterCopy=true / emphasizeRegion=true`
4. `review / highlightPrice=false / shorterCopy=false / emphasizeRegion=true`
5. `review / highlightPrice=false / shorterCopy=true / emphasizeRegion=true`
6. `review / highlightPrice=true / shorterCopy=false / emphasizeRegion=true`
7. `review / highlightPrice=true / shorterCopy=true / emphasizeRegion=true`

## 해석

1. baseline closure 관점에서 남은 숙제는 이제 전부 `emphasizeRegion=true` 축입니다.
2. 다음 우선순위는 `promotion` 3건과 `review` 4건 중 어느 쪽을 먼저 열지 결정하는 문제이며, 둘 다 location policy 리스크를 전제로 봐야 합니다.

