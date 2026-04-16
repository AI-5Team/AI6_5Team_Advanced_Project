# Test Scenario 177

## 목적

- `EXP-175` 이후 priority band가 어떻게 재정렬됐는지 확인합니다.

## 실행

- `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact "E:\\Codeit\\AI6_5Team_Advanced_Project\\docs\\experiments\\artifacts\\exp-175-prompt-baseline-coverage-audit-after-review-shorter-copy-off-profile.json" --experiment-id EXP-176 --experiment-title "Prompt Baseline Quick Option Gap Priority After Review Shorter Copy Off Profile" --artifact-name exp-176-prompt-baseline-quick-option-gap-priority-after-review-shorter-copy-off-profile.json`

## 기대 결과

- `totalQuickOptionGaps` 감소
- top `P2`가 `review highlightPrice=true` 2건으로 정리됨

## 실제 결과

- `totalQuickOptionGaps=13`
- `P2=2`
- `P3=9`
- `P4=2`

## 판정

- 통과
