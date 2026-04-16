# Test Scenario 162

## 목적

- `EXP-160` 이후 priority band가 어떻게 바뀌는지 확인합니다.

## 실행

- `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact E:\\Codeit\\AI6_5Team_Advanced_Project\\docs\\experiments\\artifacts\\exp-160-prompt-baseline-coverage-audit-after-promotion-region-anchor-profile.json --experiment-id EXP-161 --experiment-title "Prompt Baseline Quick Option Gap Priority After Promotion Region Anchor Profile" --artifact-name exp-161-prompt-baseline-quick-option-gap-priority-after-promotion-region-anchor-profile.json`

## 기대 결과

- `P3`가 1건 줄어야 합니다.
- 최상위 `P2`는 계속 `new_menu/review`여야 합니다.

## 실제 결과

- `P2=4`
- `P3=5`
- `P4=8`
- top `P2`는 `new_menu` 2건, `review` 2건으로 유지

## 판정

- 통과
