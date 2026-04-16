# Test Scenario 157

## 제목

combined promotion profile 반영 후 quick option gap priority 재정렬

## 목적

- `EXP-154` audit 결과를 기준으로 다음 quick option 실험 우선순위를 다시 정렬합니다.

## 실행

1. `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact docs/experiments/artifacts/exp-154-prompt-baseline-coverage-audit-after-combined-promotion-profile.json --experiment-id EXP-155 --experiment-title "Prompt Baseline Quick Option Gap Priority After Combined Promotion Profile" --artifact-name exp-155-prompt-baseline-quick-option-gap-priority-after-combined-promotion-profile.json`

## 기대 결과

- promotion non-region gap은 최상위에서 빠지고, `new_menu/review` P2가 앞으로 와야 합니다.

## 이번 실행 결과

- band counts:
  - `P2 = 4`
  - `P3 = 6`
  - `P4 = 8`
- top candidate:
  - `new_menu` 2건
  - `review` 2건

## 판정

- priority 재정렬은 의도대로 동작했습니다.
- 다음 실험은 promotion이 아니라 `new_menu/review` P2에서 고르는 편이 맞습니다.
