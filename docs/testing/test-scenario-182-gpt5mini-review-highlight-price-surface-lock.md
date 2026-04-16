# Test Scenario 182

## 목적

- `EXP-181`에서 `review / highlightPrice=true / shorterCopy=true / emphasizeRegion=false` candidate가 짧은 만족감 foreground를 유지하는지 확인합니다.

## 실행

- `python scripts/run_prompt_experiment.py --experiment-id EXP-181`
- `python scripts/run_prompt_variant_repeatability_spot_check.py --experiment-id EXP-181 --repeat 3`

## 기대 결과

- baseline/candidate 모두 `score=100.0`
- 새로운 가격 숫자, 할인율, 세일 문구 생성 없음
- repeatability `3/3 pass`

## 실제 결과

- baseline `100.0`
- candidate `100.0`
- repeatability:
  - baseline `3/3`
  - candidate `3/3`

## 판정

- 통과
