# Test Scenario 133 - GPT-5 Mini Review Strict Region Leakage Suppression

## 목적

- `EXP-131`에서 `gpt-5-mini`의 review strict region leakage를 surface-lock constraint로 억제할 수 있는지 재현합니다.

## 실행 명령

```powershell
python -m py_compile services/worker/experiments/prompt_harness.py
python scripts/run_prompt_experiment.py --experiment-id EXP-131 --api-key-env OPENAI_API_KEY
python scripts/run_prompt_variant_repeatability_spot_check.py --experiment-id EXP-131 --repeat 3 --api-key-env OPENAI_API_KEY
```

## 기대 결과

- single run artifact:
  - `docs/experiments/artifacts/exp-131-gpt-5-mini-review-strict-region-leakage-suppression.json`
- repeatability artifact:
  - `docs/experiments/artifacts/exp-131-variant-repeatability.json`
- baseline은 `93.3`에 머물 가능성이 높습니다.
- `review_surface_locked_exact_region_anchor`는 `100.0`과 `3/3 pass`를 목표로 합니다.

## 확인 포인트

- candidate가 `captions`, `subText`, `sceneText` 어디에서도 nearby-location을 흘리지 않는지
- `hook/review_quote/product_name/cta` 길이 budget이 그대로 유지되는지
- `gpt-5-mini`를 strict review fallback으로 쓸 수 있을 정도의 안정성이 나오는지
