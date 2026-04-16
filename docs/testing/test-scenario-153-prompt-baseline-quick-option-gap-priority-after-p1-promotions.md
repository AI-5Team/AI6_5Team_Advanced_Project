# Test Scenario 153

## 제목

P1 promotion rescue 이후 quick option gap priority 재정렬

## 목적

- `EXP-150` audit 결과를 기준으로 다음 quick option 실험 우선순위를 다시 정렬합니다.
- priority band가 option profile 추가 이후에도 올바르게 계산되는지 확인합니다.

## 실행

1. compile
   - `python -m py_compile scripts/run_prompt_baseline_quick_option_gap_priority.py`
2. priority refresh
   - `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact docs/experiments/artifacts/exp-150-prompt-baseline-coverage-audit-after-p1-promotions.json --experiment-id EXP-151 --experiment-title "Prompt Baseline Quick Option Gap Priority After P1 Promotions" --artifact-name exp-151-prompt-baseline-quick-option-gap-priority-after-p1-promotions.json`

## 기대 결과

- 이전 `P1` 두 건은 더 이상 최상위 band에 남지 않아야 합니다.
- 최상위 후보는 option profile 인접 단일 토글(`P2`)들로 재정렬돼야 합니다.

## 이번 실행 결과

- band counts:
  - `P2 = 5`
  - `P3 = 5`
  - `P4 = 9`
- `P1 = 0`
- 최상위 후보:
  - `promotion / highlightPrice=false / shorterCopy=false / emphasizeRegion=false`
  - `new_menu` 단일 토글 2건
  - `review` 단일 토글 2건

## 판정

- priority 재정렬은 의도대로 동작했습니다.
- 이제 다음 실험은 `promotion` 잔여 P2 1건 또는 `new_menu/review` P2 단일 토글 중 하나를 고르면 됩니다.
