# Test Scenario 185

## 목적

- `EXP-183` 이후 priority band가 어떻게 재정렬됐는지 확인합니다.

## 실행

- `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact "E:\\Codeit\\AI6_5Team_Advanced_Project\\docs\\experiments\\artifacts\\exp-183-prompt-baseline-coverage-audit-after-review-highlight-price-profile.json" --experiment-id EXP-184 --experiment-title "Prompt Baseline Quick Option Gap Priority After Review Highlight Price Profile" --artifact-name exp-184-prompt-baseline-quick-option-gap-priority-after-review-highlight-price-profile.json`

## 기대 결과

- `P2=0`
- 남은 gap이 모두 `P3`로 정리됨

## 실제 결과

- `totalQuickOptionGaps=11`
- `P3=11`

## 판정

- 통과
