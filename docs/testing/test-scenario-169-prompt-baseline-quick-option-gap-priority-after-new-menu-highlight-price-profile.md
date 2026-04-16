# Test Scenario 169

## 목적

- `EXP-167` 이후 priority band가 어떻게 바뀌는지 확인합니다.

## 실행

- `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact "E:\\Codeit\\AI6_5Team_Advanced_Project\\docs\\experiments\\artifacts\\exp-167-prompt-baseline-coverage-audit-after-new-menu-highlight-price-profile.json" --experiment-id EXP-168 --experiment-title "Prompt Baseline Quick Option Gap Priority After New Menu Highlight Price Profile" --artifact-name exp-168-prompt-baseline-quick-option-gap-priority-after-new-menu-highlight-price-profile.json`

## 기대 결과

- `totalQuickOptionGaps` 감소
- top `P2`가 `new_menu combined` 1건과 `review` 2건으로 재정렬

## 실제 결과

- `totalQuickOptionGaps=15`
- `P2=3`
- `P3=7`
- `P4=5`

## 판정

- 통과
