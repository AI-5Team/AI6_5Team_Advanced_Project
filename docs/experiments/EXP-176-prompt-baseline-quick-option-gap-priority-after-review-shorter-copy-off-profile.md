# EXP-176 Prompt Baseline Quick Option Gap Priority After Review Shorter Copy Off Profile

## 목표

- `EXP-175` 이후 남은 quick option gap priority를 다시 정렬합니다.

## 실행

- `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact "E:\\Codeit\\AI6_5Team_Advanced_Project\\docs\\experiments\\artifacts\\exp-175-prompt-baseline-coverage-audit-after-review-shorter-copy-off-profile.json" --experiment-id EXP-176 --experiment-title "Prompt Baseline Quick Option Gap Priority After Review Shorter Copy Off Profile" --artifact-name exp-176-prompt-baseline-quick-option-gap-priority-after-review-shorter-copy-off-profile.json`

artifact:

- `docs/experiments/artifacts/exp-176-prompt-baseline-quick-option-gap-priority-after-review-shorter-copy-off-profile.json`

## 결과

- `totalQuickOptionGaps=13`
- `P2=2`
- `P3=9`
- `P4=2`

현재 top `P2`:

1. `review / T04 / b_grade_fun / highlightPrice=true / shorterCopy=false / emphasizeRegion=false`
   - nearest: `review_strict_fallback_surface_lock_shorter_copy_off`
   - mismatch: `quickOptions.highlightPrice`
2. `review / T04 / b_grade_fun / highlightPrice=true / shorterCopy=true / emphasizeRegion=false`
   - nearest: `review_strict_fallback_surface_lock`
   - mismatch: `quickOptions.highlightPrice`

## 해석

1. 최상위 `P2` 개수는 그대로 `2`지만, 이제 둘 다 `review highlightPrice=true` 축으로 정리됐습니다.
2. `shorterCopy=false` 공백을 해소하면서 priority가 `review`의 가격/가치 포인트 해석 문제로 더 선명하게 좁혀졌습니다.
3. 다음 coverage completion은 `review highlightPrice=true / shorterCopy=false`를 먼저 보는 편이 가장 자연스럽습니다.
