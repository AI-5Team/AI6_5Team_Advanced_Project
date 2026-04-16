# Test Scenario 110 - strict anchor benefit budget comparison

## 목적

- `EXP-108`에서 exact region anchor와 tighter benefit budget을 함께 고정했을 때 `Gemma 4`와 `gpt-5-mini` 중 누가 더 production-near한지 재현합니다.

## 입력 자료

1. `scripts/run_model_comparison_experiment.py`
2. `services/worker/experiments/prompt_harness.py`
3. `docs/experiments/EXP-108-strict-anchor-benefit-budget-comparison.md`

## 실행 명령

```bash
python scripts/run_model_comparison_experiment.py --experiment-id EXP-108
```

## 확인 포인트

1. 두 모델이 정확히 같은 strict prompt를 쓰는지 확인합니다.
2. `Gemma 4`가 exact region slot과 headline budget을 같이 만족하는지 확인합니다.
3. `gpt-5-mini`가 caption에서 `성수동`을 빼고 `서울숲 근처`로 우회하는지 확인합니다.

## 기대 결과

1. `Gemma 4`가 현재 strict prompt 기준 더 안정적으로 통과합니다.
2. `gpt-5-mini`는 길이/CTA는 강하지만 region anchor에서 더 잘 흔들립니다.
3. 따라서 현재 main baseline 후보는 `Gemma 4`가 됩니다.
