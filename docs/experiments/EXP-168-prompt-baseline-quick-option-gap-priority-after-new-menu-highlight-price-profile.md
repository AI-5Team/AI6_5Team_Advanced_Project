# EXP-168 Prompt Baseline Quick Option Gap Priority After New Menu Highlight Price Profile

## 목표

- `EXP-167` 이후 남은 quick option gap priority를 다시 정렬합니다.

## 실행

- `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact "E:\\Codeit\\AI6_5Team_Advanced_Project\\docs\\experiments\\artifacts\\exp-167-prompt-baseline-coverage-audit-after-new-menu-highlight-price-profile.json" --experiment-id EXP-168 --experiment-title "Prompt Baseline Quick Option Gap Priority After New Menu Highlight Price Profile" --artifact-name exp-168-prompt-baseline-quick-option-gap-priority-after-new-menu-highlight-price-profile.json`

artifact:

- `docs/experiments/artifacts/exp-168-prompt-baseline-quick-option-gap-priority-after-new-menu-highlight-price-profile.json`

## 결과

- `totalQuickOptionGaps=15`
- `P2=3`
- `P3=7`
- `P4=5`

현재 top `P2`:

1. `new_menu / T01 / friendly / highlightPrice=true / shorterCopy=true / emphasizeRegion=true`
   - nearest: `new_menu_friendly_region_anchor_shorter_copy`
   - mismatch: `quickOptions.highlightPrice`
2. `review / T04 / b_grade_fun / highlightPrice=false / shorterCopy=false / emphasizeRegion=false`
   - nearest: `review_strict_fallback_surface_lock`
   - mismatch: `quickOptions.shorterCopy`
3. `review / T04 / b_grade_fun / highlightPrice=true / shorterCopy=true / emphasizeRegion=false`
   - nearest: `review_strict_fallback_surface_lock`
   - mismatch: `quickOptions.highlightPrice`

## 해석

1. 최상위 `P2`는 `4 -> 3`으로 줄었습니다.
2. `new_menu` 쪽은 이제 `highlightPrice + shorterCopy` combined profile 1건만 남았습니다.
3. 그 다음 우선순위는 `review`의 단일 토글 2건입니다.
