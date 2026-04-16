# EXP-212 Prompt Baseline Quick Option Gap Priority After Promotion Region Anchor Profiles

## 목표

- `EXP-211` audit 기준으로 남은 quick option gap 우선순위를 다시 계산합니다.

## 실행

- `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact E:\\Codeit\\AI6_5Team_Advanced_Project\\docs\\experiments\\artifacts\\exp-211-prompt-baseline-coverage-audit-after-promotion-region-anchor-profiles.json --experiment-id EXP-212 --experiment-title "Prompt Baseline Quick Option Gap Priority After Promotion Region Anchor Profiles" --artifact-name exp-212-prompt-baseline-quick-option-gap-priority-after-promotion-region-anchor-profiles.json`

artifact:

- `docs/experiments/artifacts/exp-212-prompt-baseline-quick-option-gap-priority-after-promotion-region-anchor-profiles.json`

## 결과

- `totalQuickOptionGaps=4`
- `bandCounts={ P3: 4 }`

remaining gaps:

1. `review / highlightPrice=false / shorterCopy=false / emphasizeRegion=true`
2. `review / highlightPrice=false / shorterCopy=true / emphasizeRegion=true`
3. `review / highlightPrice=true / shorterCopy=false / emphasizeRegion=true`
4. `review / highlightPrice=true / shorterCopy=true / emphasizeRegion=true`

## 해석

1. baseline closure 관점에서 promotion 축은 이제 region emphasis까지 모두 정리됐습니다.
2. 다음 우선순위는 `review region emphasis` 4건을 같은 방식으로 닫을지, 여기서 baseline closure를 멈출지 판단하는 문제만 남았습니다.

