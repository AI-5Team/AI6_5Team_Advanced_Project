# Test Scenario 112 - nearby-location leakage evaluator patch

## 목적

- `EXP-110`에서 strict region 조건의 nearby-location leakage가 자동 평가 실패로 반영되는지 확인합니다.

## 입력 자료

1. `services/worker/experiments/prompt_harness.py`
2. `docs/experiments/EXP-110-nearby-location-leakage-evaluator-patch.md`

## 실행 명령

```bash
python scripts/run_prompt_experiment.py --experiment-id EXP-106 --api-key-env OPENAI_API_KEY
python scripts/run_prompt_experiment.py --experiment-id EXP-107 --api-key-env GEMINI_API_KEY
python scripts/run_model_comparison_experiment.py --experiment-id EXP-108
python scripts/run_prompt_repeatability_spot_check.py --experiment-id EXP-108 --repeat 3
```

## 확인 포인트

1. `서울숲 근처`, `#서울숲근처`, `#서울숲데이트` 같은 nearby-location 표현이 있으면 `failed_checks`에 새 failure가 들어가는지 확인합니다.
2. `Gemma 4`와 `gpt-5-mini`의 strict prompt 비교가 leakage 포함 기준으로 다시 벌어지는지 확인합니다.
3. repeatability 결과에서 `Gemma 4`는 통과, `gpt-5-mini`는 leakage 때문에 평균 점수가 내려가는지 확인합니다.

## 기대 결과

1. 기존 blind spot이었던 nearby-location leakage가 자동 실패로 잡힙니다.
2. strict prompt 기준 main baseline 후보가 `Gemma 4`로 더 선명해집니다.
