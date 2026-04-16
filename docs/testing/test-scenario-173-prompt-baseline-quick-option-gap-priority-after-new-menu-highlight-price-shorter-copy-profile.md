# Test Scenario 173

## 목적

- `EXP-171` 이후 priority band가 어떻게 바뀌는지 확인합니다.

## 실행

- `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact "E:\\Codeit\\AI6_5Team_Advanced_Project\\docs\\experiments\\artifacts\\exp-171-prompt-baseline-coverage-audit-after-new-menu-highlight-price-shorter-copy-profile.json" --experiment-id EXP-172 --experiment-title "Prompt Baseline Quick Option Gap Priority After New Menu Highlight Price Shorter Copy Profile" --artifact-name exp-172-prompt-baseline-quick-option-gap-priority-after-new-menu-highlight-price-shorter-copy-profile.json`

## 기대 결과

- `totalQuickOptionGaps` 감소
- top `P2`가 `review` 2건으로 재정렬

## 실제 결과

- `totalQuickOptionGaps=14`
- `P2=2`
- `P3=8`
- `P4=4`

## 판정

- 통과
