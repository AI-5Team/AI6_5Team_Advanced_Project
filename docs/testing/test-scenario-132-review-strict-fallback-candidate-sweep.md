# Test Scenario 132 - Review Strict Fallback Candidate Sweep

## 목적

- `EXP-130`의 review strict fallback 후보 비교를 재현합니다.
- OpenAI Responses request shape 호환성 패치 이후에도 실제 project access가 후보 제약이 되는지 확인합니다.

## 실행 명령

```powershell
python -m py_compile services/worker/experiments/prompt_harness.py
python -m py_compile scripts/run_prompt_repeatability_spot_check.py
python scripts/run_model_comparison_experiment.py --experiment-id EXP-130
```

## 기대 결과

- artifact:
  - `docs/experiments/artifacts/exp-130-review-strict-fallback-candidate-sweep.json`
- `Gemma 4`는 `100.0`을 유지해야 합니다.
- `gpt-5-mini`는 nearby-location leakage로 `93.3`에 머물 가능성이 높습니다.
- `gpt-4.1-mini`는 현재 project access 기준으로 `403 model_not_found`가 날 수 있습니다.

## 확인 포인트

- `Gemma 4`가 strict review baseline에서 계속 통과하는지
- `gpt-5-mini`가 여전히 `captions` 등 public copy surface에 nearby landmark를 흘리는지
- `gpt-4.1-mini`가 실제 품질 비교 이전에 access 문제로 막히는지
