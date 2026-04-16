# Test Scenario 111 - strict anchor benefit budget repeatability

## 목적

- `EXP-109`에서 `EXP-108` strict prompt를 각 모델에 3회씩 다시 돌렸을 때 안정성 차이가 재현되는지 확인합니다.

## 입력 자료

1. `scripts/run_prompt_repeatability_spot_check.py`
2. `docs/experiments/EXP-109-strict-anchor-benefit-budget-repeatability.md`

## 실행 명령

```bash
python scripts/run_prompt_repeatability_spot_check.py --experiment-id EXP-108 --repeat 3
```

## 확인 포인트

1. `Gemma 4`가 3회 모두 통과하는지 확인합니다.
2. `gpt-5-mini`에서 `region appears in fewer than required areas`가 재발하는지 확인합니다.
3. 자동 score 100인 run에서도 `서울숲 근처`, `#서울숲근처` 같은 nearby-location leakage가 남는지 수동으로 확인합니다.

## 기대 결과

1. `Gemma 4`는 strict prompt에서 더 안정적입니다.
2. `gpt-5-mini`는 짧고 직접적이지만 compliance가 흔들립니다.
3. 자동 점수와 수동 해석을 분리해야 한다는 결론이 나옵니다.
