# Test Scenario 181

## 목적

- `EXP-179` 이후 priority band가 어떻게 재정렬됐는지 확인합니다.

## 실행

- `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact "E:\\Codeit\\AI6_5Team_Advanced_Project\\docs\\experiments\\artifacts\\exp-179-prompt-baseline-coverage-audit-after-review-highlight-price-shorter-copy-off-profile.json" --experiment-id EXP-180 --experiment-title "Prompt Baseline Quick Option Gap Priority After Review Highlight Price Shorter Copy Off Profile" --artifact-name exp-180-prompt-baseline-quick-option-gap-priority-after-review-highlight-price-shorter-copy-off-profile.json`

## 기대 결과

- `P2=1`
- 마지막 top `P2`가 `review highlightPrice=true / shorterCopy=true`로 정리됨

## 실제 결과

- `totalQuickOptionGaps=12`
- `P2=1`
- `P3=10`
- `P4=1`

## 판정

- 통과
