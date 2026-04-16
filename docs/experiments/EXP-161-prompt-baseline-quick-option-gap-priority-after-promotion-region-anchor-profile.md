# EXP-161 Prompt Baseline Quick Option Gap Priority After Promotion Region Anchor Profile

## 목표

- `EXP-160` audit 결과를 기준으로 남은 quick option gap 우선순위를 다시 정렬합니다.

## 실행

- `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact E:\\Codeit\\AI6_5Team_Advanced_Project\\docs\\experiments\\artifacts\\exp-160-prompt-baseline-coverage-audit-after-promotion-region-anchor-profile.json --experiment-id EXP-161 --experiment-title "Prompt Baseline Quick Option Gap Priority After Promotion Region Anchor Profile" --artifact-name exp-161-prompt-baseline-quick-option-gap-priority-after-promotion-region-anchor-profile.json`

artifact:

- `docs/experiments/artifacts/exp-161-prompt-baseline-quick-option-gap-priority-after-promotion-region-anchor-profile.json`

## 결과

- `totalQuickOptionGaps=17`
- `P2=4`
- `P3=5`
- `P4=8`

top `P2`:

1. `new_menu / T01 / friendly / highlightPrice=false / shorterCopy=true / emphasizeRegion=true`
2. `new_menu / T01 / friendly / highlightPrice=true / shorterCopy=false / emphasizeRegion=true`
3. `review / T04 / b_grade_fun / highlightPrice=false / shorterCopy=false / emphasizeRegion=false`
4. `review / T04 / b_grade_fun / highlightPrice=true / shorterCopy=true / emphasizeRegion=false`

남은 promotion `P3`:

- `highlightPrice=false / shorterCopy=true / emphasizeRegion=true`
- `highlightPrice=true / shorterCopy=false / emphasizeRegion=true`
- `highlightPrice=true / shorterCopy=true / emphasizeRegion=true`

## 해석

1. promotion region-emphasis 1건을 줄였어도 최상위 우선순위는 여전히 `new_menu/review P2`입니다.
2. 다만 현재 세션에서는 `gpt-5-mini` 경로가 `OPENAI_API_KEY` 문제로 막혀 있어, 이 4건은 provider access 복구 전까지 실험 판단을 미루는 편이 맞습니다.
3. 따라서 다음 세션의 첫 작업은 새 prompt 실험보다 `OpenAI credential 복구 여부 확인`입니다.
