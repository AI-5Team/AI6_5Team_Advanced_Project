# EXP-184 Prompt Baseline Quick Option Gap Priority After Review Highlight Price Profile

## 목표

- `EXP-183` 이후 남은 quick option gap priority를 다시 정렬합니다.

## 실행

- `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact "E:\\Codeit\\AI6_5Team_Advanced_Project\\docs\\experiments\\artifacts\\exp-183-prompt-baseline-coverage-audit-after-review-highlight-price-profile.json" --experiment-id EXP-184 --experiment-title "Prompt Baseline Quick Option Gap Priority After Review Highlight Price Profile" --artifact-name exp-184-prompt-baseline-quick-option-gap-priority-after-review-highlight-price-profile.json`

artifact:

- `docs/experiments/artifacts/exp-184-prompt-baseline-quick-option-gap-priority-after-review-highlight-price-profile.json`

## 결과

- `totalQuickOptionGaps=11`
- `P3=11`

top 후보 예시:

1. `new_menu / T01 / friendly / emphasizeRegion=false`
2. `new_menu / T01 / friendly / shorterCopy=true / emphasizeRegion=false`
3. `new_menu / T01 / friendly / highlightPrice=true / emphasizeRegion=false`

공통 특성:

- 모두 `quickOptions.emphasizeRegion` 단일 mismatch
- 즉 남은 gap은 모두 region emphasis 포함 축입니다.

## 해석

1. 비지역 `P1/P2`는 모두 해소됐습니다.
2. 남은 quick option gap은 전부 `P3`, 즉 `emphasizeRegion` 포함 축만 남았습니다.
3. 따라서 현재 baseline 정리의 분기점은 `region emphasis 축까지 계속 확장할지`, 아니면 여기서 비지역 baseline 완료로 보고 멈출지 판단하는 것입니다.
