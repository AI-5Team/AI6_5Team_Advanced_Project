# Test Scenario 168

## 목적

- `EXP-166` 이후 coverage 분포가 실제로 한 칸 더 개선됐는지 확인합니다.

## 실행

- `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-167 --experiment-title "Prompt Baseline Coverage Audit After New Menu Highlight Price Profile" --artifact-name exp-167-prompt-baseline-coverage-audit-after-new-menu-highlight-price-profile.json`

## 기대 결과

- `option_match` 증가
- `coverage_gap` 감소

## 실제 결과

- `option_match=8`
- `coverage_gap=15`
- `exact_match=9`

## 판정

- 통과
