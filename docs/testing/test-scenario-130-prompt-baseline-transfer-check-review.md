# Test Scenario 130 - Prompt Baseline Transfer Check Review

## 목적

- `EXP-128`이 `T02 promotion` baseline 원칙을 `T04 review`로 옮겼을 때 실제로 통과하는지 재현합니다.
- prompt variant repeatability에서 실패 원인이 품질 저하가 아니라 timeout인지 같이 확인합니다.

## 실행 명령

```powershell
python -m py_compile services/worker/experiments/prompt_harness.py
python scripts/run_prompt_experiment.py --experiment-id EXP-128 --api-key-env GEMINI_API_KEY
python -m py_compile scripts/run_prompt_variant_repeatability_spot_check.py
python scripts/run_prompt_variant_repeatability_spot_check.py --experiment-id EXP-128 --repeat 3 --api-key-env GEMINI_API_KEY
```

## 기대 결과

- single run artifact:
  - `docs/experiments/artifacts/exp-128-prompt-baseline-transfer-check-t02-promotion-to-t04-review.json`
- repeatability artifact:
  - `docs/experiments/artifacts/exp-128-variant-repeatability.json`
- single run에서는 두 variant 모두 `score=100.0`이어야 합니다.
- repeatability에서는 실패가 나더라도, 실패 이유가 `The read operation timed out`인지 먼저 확인합니다.

## 확인 포인트

- deterministic reference가 여전히 `93.3`에 머무르는지
- direct transfer와 translated transfer가 single run에서는 모두 pass하는지
- repeatability failure가 policy collapse인지 timeout인지
