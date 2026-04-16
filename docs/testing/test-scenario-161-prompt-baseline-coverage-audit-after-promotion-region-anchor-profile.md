# Test Scenario 161

## 목적

- promotion region-anchor profile 반영 후 coverage 숫자가 실제로 한 칸 줄어드는지 확인합니다.

## 실행

- `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-160 --experiment-title "Prompt Baseline Coverage Audit After Promotion Region Anchor Profile" --artifact-name exp-160-prompt-baseline-coverage-audit-after-promotion-region-anchor-profile.json`

## 기대 결과

- `option_match` 증가
- `coverage_gap` 감소

## 실제 결과

- `option_match=6`
- `coverage_gap=17`
- `exact_match=7`

## 판정

- 통과
