# Test Scenario 172

## 목적

- `EXP-170` 이후 coverage 분포가 실제로 한 칸 더 개선됐는지 확인합니다.

## 실행

- `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-171 --experiment-title "Prompt Baseline Coverage Audit After New Menu Highlight Price Shorter Copy Profile" --artifact-name exp-171-prompt-baseline-coverage-audit-after-new-menu-highlight-price-shorter-copy-profile.json`

## 기대 결과

- `option_match` 증가
- `coverage_gap` 감소

## 실제 결과

- `option_match=9`
- `coverage_gap=14`
- `exact_match=10`

## 판정

- 통과
