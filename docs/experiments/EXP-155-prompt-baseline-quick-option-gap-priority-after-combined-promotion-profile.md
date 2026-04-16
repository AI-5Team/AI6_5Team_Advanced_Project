# EXP-155 Prompt Baseline Quick Option Gap Priority After Combined Promotion Profile

## 배경

- `EXP-154` 기준으로 promotion non-region 공백이 사실상 정리됐습니다.
- 따라서 다음 우선순위는 다시 계산해야 합니다.

## 목표

1. 새 audit 결과를 기준으로 quick option gap priority를 다시 정렬합니다.
2. 다음 실험이 `promotion`인지 `new_menu/review`인지 숫자로 확인합니다.

## 실행

1. `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact docs/experiments/artifacts/exp-154-prompt-baseline-coverage-audit-after-combined-promotion-profile.json --experiment-id EXP-155 --experiment-title "Prompt Baseline Quick Option Gap Priority After Combined Promotion Profile" --artifact-name exp-155-prompt-baseline-quick-option-gap-priority-after-combined-promotion-profile.json`

## 결과

- artifact:
  - `docs/experiments/artifacts/exp-155-prompt-baseline-quick-option-gap-priority-after-combined-promotion-profile.json`

### aggregate

- `P2 = 4`
- `P3 = 6`
- `P4 = 8`
- `P1 = 0`

### 현재 top candidate

1. `new_menu / T01 / friendly / highlightPrice=false / shorterCopy=true / emphasizeRegion=true`
2. `new_menu / T01 / friendly / highlightPrice=true / shorterCopy=false / emphasizeRegion=true`
3. `review / T04 / b_grade_fun / highlightPrice=false / shorterCopy=false / emphasizeRegion=false`
4. `review / T04 / b_grade_fun / highlightPrice=true / shorterCopy=true / emphasizeRegion=false`

## 해석

1. 이제 최상위 `P2`는 promotion이 아니라 `new_menu`, `review`입니다.
2. promotion은 남아 있어도 전부 `emphasizeRegion=true`가 포함된 `P3`로 내려갔습니다.

## 판단

- 다음 기준선은 `new_menu` 또는 `review`의 option-adjacent single-toggle 4건 중 하나를 고르는 편이 맞습니다.

## 결론

- promotion 축은 한 단계 정리됐고, 다음 주도권은 `new_menu/review P2`로 넘어갔습니다.

## 관련 파일

- `scripts/run_prompt_baseline_quick_option_gap_priority.py`
- `docs/experiments/artifacts/exp-155-prompt-baseline-quick-option-gap-priority-after-combined-promotion-profile.json`
