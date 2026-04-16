# Test Scenario 144

## 제목

prompt baseline quick option gap priority 산출 검증

## 목적

- `quick_option_gap` 21건이 우선순위 밴드 `P1~P4`로 안정적으로 분류되는지 확인합니다.
- 다음 실험 후보가 `main baseline` 인접 단일 토글부터 정렬되는지 확인합니다.

## 실행

1. compile
   - `python -m py_compile scripts/run_prompt_baseline_quick_option_gap_priority.py`
2. priority run
   - `python scripts/run_prompt_baseline_quick_option_gap_priority.py`

## 기대 결과

- aggregate:
  - `totalQuickOptionGaps=21`
  - `P1=2`
  - `P2=4`
  - `P3=3`
  - `P4=12`
- top candidates:
  - 첫 2개가 `promotion / T02 / b_grade_fun`의 단일 토글 gap
  - `highlightPrice only`
  - `shorterCopy only`

## 이번 실행 결과

- `python -m py_compile scripts/run_prompt_baseline_quick_option_gap_priority.py` 통과
- `python scripts/run_prompt_baseline_quick_option_gap_priority.py` 통과
- artifact 생성:
  - `docs/experiments/artifacts/exp-142-prompt-baseline-quick-option-gap-priority.json`

## 판정

- quick option gap priority는 현재 coverage audit 결과를 실험 우선순위로 바로 연결하는 artifact를 정상 생성했습니다.
- 다음 baseline 실험은 `P1` 2건부터 시작하는 편이 가장 타당합니다.
