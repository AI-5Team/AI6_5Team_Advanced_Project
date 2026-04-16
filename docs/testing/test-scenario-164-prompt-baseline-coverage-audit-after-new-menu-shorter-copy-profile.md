# Test Scenario 164

## 목적

- `new_menu shorterCopy` profile 반영 후 coverage 숫자가 실제로 줄어드는지 확인합니다.

## 실행

- `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-163 --experiment-title "Prompt Baseline Coverage Audit After New Menu Shorter Copy Profile" --artifact-name exp-163-prompt-baseline-coverage-audit-after-new-menu-shorter-copy-profile.json`

## 기대 결과

- `option_match` 증가
- `coverage_gap` 감소

## 실제 결과

- `option_match=7`
- `coverage_gap=16`
- `exact_match=8`

## 판정

- 통과
