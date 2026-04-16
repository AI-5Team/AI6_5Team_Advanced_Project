# Test Scenario 131 - Review Baseline Fallback Model Comparison

## 목적

- `EXP-129`에서 `Gemma 4`와 `gpt-5-mini`를 같은 review baseline prompt로 비교한 결과를 재현합니다.
- `gpt-5-mini`가 strict review fallback candidate인지 아닌지 다시 확인합니다.

## 실행 명령

```powershell
python -m py_compile services/worker/experiments/prompt_harness.py
python scripts/run_model_comparison_experiment.py --experiment-id EXP-129
python -m py_compile scripts/run_prompt_repeatability_spot_check.py
python scripts/run_prompt_repeatability_spot_check.py --experiment-id EXP-129 --repeat 3
```

## 기대 결과

- comparison artifact:
  - `docs/experiments/artifacts/exp-129-review-baseline-transfer-fallback-model-comparison.json`
- repeatability artifact:
  - `docs/experiments/artifacts/exp-129-repeatability.json`
- `Gemma 4`는 single run과 repeatability 모두 `100.0`을 유지해야 합니다.
- `gpt-5-mini`는 nearby-location leakage로 `93.3`에 머무를 가능성이 높습니다.

## 확인 포인트

- `Gemma 4`가 `strict_all_surfaces`에서 안정적으로 통과하는지
- `gpt-5-mini`가 `captions` 또는 `subText`에 nearby landmark를 반복적으로 흘리는지
- `timeout risk`와 `policy leakage risk` 중 어느 쪽이 더 큰 운영 리스크인지
