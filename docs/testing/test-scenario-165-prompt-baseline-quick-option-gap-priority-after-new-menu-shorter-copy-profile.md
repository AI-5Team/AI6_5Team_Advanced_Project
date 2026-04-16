# Test Scenario 165

## 목적

- `EXP-163` 이후 priority band가 어떻게 바뀌는지 확인합니다.

## 실행

- `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact "E:\\Codeit\\AI6_5Team_Advanced_Project\\docs\\experiments\\artifacts\\exp-163-prompt-baseline-coverage-audit-after-new-menu-shorter-copy-profile.json" --experiment-id EXP-164 --experiment-title "Prompt Baseline Quick Option Gap Priority After New Menu Shorter Copy Profile" --artifact-name exp-164-prompt-baseline-quick-option-gap-priority-after-new-menu-shorter-copy-profile.json`

## 기대 결과

- `totalQuickOptionGaps` 감소
- top `P2`가 `new_menu highlightPrice=true`와 `review` 축으로 재정렬

## 실제 결과

- `totalQuickOptionGaps=16`
- `P2=4`
- `P3=6`
- `P4=6`

## 판정

- 통과
