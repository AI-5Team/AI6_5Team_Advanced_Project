# EXP-180 Prompt Baseline Quick Option Gap Priority After Review Highlight Price Shorter Copy Off Profile

## 목표

- `EXP-179` 이후 남은 quick option gap priority를 다시 정렬합니다.

## 실행

- `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact "E:\\Codeit\\AI6_5Team_Advanced_Project\\docs\\experiments\\artifacts\\exp-179-prompt-baseline-coverage-audit-after-review-highlight-price-shorter-copy-off-profile.json" --experiment-id EXP-180 --experiment-title "Prompt Baseline Quick Option Gap Priority After Review Highlight Price Shorter Copy Off Profile" --artifact-name exp-180-prompt-baseline-quick-option-gap-priority-after-review-highlight-price-shorter-copy-off-profile.json`

artifact:

- `docs/experiments/artifacts/exp-180-prompt-baseline-quick-option-gap-priority-after-review-highlight-price-shorter-copy-off-profile.json`

## 결과

- `totalQuickOptionGaps=12`
- `P2=1`
- `P3=10`
- `P4=1`

현재 top `P2`:

1. `review / T04 / b_grade_fun / highlightPrice=true / shorterCopy=true / emphasizeRegion=false`
   - nearest: `review_strict_fallback_surface_lock`
   - mismatch: `quickOptions.highlightPrice`

## 해석

1. 최상위 `P2`는 이제 1건만 남았습니다.
2. 다음 coverage completion은 `review highlightPrice=true / shorterCopy=true`를 메우는 것입니다.
