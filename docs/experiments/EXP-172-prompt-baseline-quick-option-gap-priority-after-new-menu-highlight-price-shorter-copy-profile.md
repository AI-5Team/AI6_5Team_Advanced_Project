# EXP-172 Prompt Baseline Quick Option Gap Priority After New Menu Highlight Price Shorter Copy Profile

## 목표

- `EXP-171` 이후 남은 quick option gap priority를 다시 정렬합니다.

## 실행

- `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact "E:\\Codeit\\AI6_5Team_Advanced_Project\\docs\\experiments\\artifacts\\exp-171-prompt-baseline-coverage-audit-after-new-menu-highlight-price-shorter-copy-profile.json" --experiment-id EXP-172 --experiment-title "Prompt Baseline Quick Option Gap Priority After New Menu Highlight Price Shorter Copy Profile" --artifact-name exp-172-prompt-baseline-quick-option-gap-priority-after-new-menu-highlight-price-shorter-copy-profile.json`

artifact:

- `docs/experiments/artifacts/exp-172-prompt-baseline-quick-option-gap-priority-after-new-menu-highlight-price-shorter-copy-profile.json`

## 결과

- `totalQuickOptionGaps=14`
- `P2=2`
- `P3=8`
- `P4=4`

현재 top `P2`:

1. `review / T04 / b_grade_fun / highlightPrice=false / shorterCopy=false / emphasizeRegion=false`
   - nearest: `review_strict_fallback_surface_lock`
   - mismatch: `quickOptions.shorterCopy`
2. `review / T04 / b_grade_fun / highlightPrice=true / shorterCopy=true / emphasizeRegion=false`
   - nearest: `review_strict_fallback_surface_lock`
   - mismatch: `quickOptions.highlightPrice`

## 해석

1. 최상위 `P2`는 `3 -> 2`로 줄었습니다.
2. `new_menu` 비지역 `P2`는 모두 정리됐고, 다음 우선순위는 `review` 2건입니다.
