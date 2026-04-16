# Test Scenario 166

## 목적

- `EXP-165`에서 `new_menu / highlightPrice=true / emphasizeRegion=true` candidate가 가격 환각 없이 통과하는지 확인합니다.

## 실행

- `python scripts/run_prompt_experiment.py --experiment-id EXP-165`
- `python scripts/run_prompt_variant_repeatability_spot_check.py --experiment-id EXP-165 --repeat 3`

## 기대 결과

- baseline/candidate 모두 `score=100.0`
- candidate가 가격 숫자나 할인율을 새로 만들지 않음
- repeatability `3/3 pass`

## 실제 결과

- baseline `100.0`
- candidate `100.0`
- repeatability:
  - baseline `3/3`
  - candidate `3/3`

## 판정

- 통과
