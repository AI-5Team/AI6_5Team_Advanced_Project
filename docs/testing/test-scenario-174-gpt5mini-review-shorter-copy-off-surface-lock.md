# Test Scenario 174

## 목적

- `EXP-173`에서 `review / highlightPrice=false / shorterCopy=false / emphasizeRegion=false` candidate가 설명 한 줄 확장을 허용하면서도 strict location discipline을 유지하는지 확인합니다.

## 실행

- `python scripts/run_prompt_experiment.py --experiment-id EXP-173`
- `python scripts/run_prompt_variant_repeatability_spot_check.py --experiment-id EXP-173 --repeat 3`

## 기대 결과

- baseline/candidate 모두 `score=100.0`
- candidate가 `subText`에서 식감/풍미/재방문 이유를 한 줄 더 설명함
- repeatability `3/3 pass`

## 실제 결과

- baseline `100.0`
- candidate `100.0`
- repeatability:
  - baseline `3/3`
  - candidate `3/3`

## 판정

- 통과
