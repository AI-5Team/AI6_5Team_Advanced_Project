# EXP-164 Prompt Baseline Quick Option Gap Priority After New Menu Shorter Copy Profile

## 목표

- `EXP-163` audit 결과를 기준으로 남은 quick option gap 우선순위를 다시 정렬합니다.

## 실행

- `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact "E:\\Codeit\\AI6_5Team_Advanced_Project\\docs\\experiments\\artifacts\\exp-163-prompt-baseline-coverage-audit-after-new-menu-shorter-copy-profile.json" --experiment-id EXP-164 --experiment-title "Prompt Baseline Quick Option Gap Priority After New Menu Shorter Copy Profile" --artifact-name exp-164-prompt-baseline-quick-option-gap-priority-after-new-menu-shorter-copy-profile.json`

artifact:

- `docs/experiments/artifacts/exp-164-prompt-baseline-quick-option-gap-priority-after-new-menu-shorter-copy-profile.json`

## 결과

- `totalQuickOptionGaps=16`
- `P2=4`
- `P3=6`
- `P4=6`

top `P2`:

1. `new_menu / T01 / friendly / highlightPrice=true / shorterCopy=false / emphasizeRegion=true`
2. `new_menu / T01 / friendly / highlightPrice=true / shorterCopy=true / emphasizeRegion=true`
3. `review / T04 / b_grade_fun / highlightPrice=false / shorterCopy=false / emphasizeRegion=false`
4. `review / T04 / b_grade_fun / highlightPrice=true / shorterCopy=true / emphasizeRegion=false`

## 해석

1. `new_menu shorterCopy=false/true` 계열 중 `highlightPrice=false` 쪽은 이제 정리됐습니다.
2. 다음 최상위 공백은 `new_menu highlightPrice=true` 2건과 `review` 2건입니다.
3. 특히 `P4`가 `8 -> 6`으로 줄어, 이제 남은 gap 분포도 조금 더 단순해졌습니다.
