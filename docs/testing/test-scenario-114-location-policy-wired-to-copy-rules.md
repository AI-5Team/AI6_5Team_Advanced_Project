# Test Scenario 114 - location policy wired to copy-rules

## 목적

- `EXP-112`에서 `copy-rule.locationPolicy`가 실제 evaluation에 반영되는지 확인합니다.

## 입력 자료

1. `packages/template-spec/copy-rules/promotion.json`
2. `packages/template-spec/copy-rules/review.json`
3. `services/worker/experiments/prompt_harness.py`
4. `docs/experiments/EXP-112-location-policy-wired-to-copy-rules.md`

## 실행 명령

```bash
python -m py_compile services/worker/experiments/prompt_harness.py
python scripts/run_model_comparison_experiment.py --experiment-id EXP-108
```

## 확인 포인트

1. `promotion`, `review` copy-rule에 `locationPolicy`가 실제로 들어가 있는지 확인합니다.
2. 최신 `EXP-108` artifact에서 evaluation에 아래 필드가 포함되는지 확인합니다.
   - `detail_location_policy_surfaces`
   - `detail_location_leaks_by_surface`
3. `gpt-5-mini`가 `captions` leakage로 실패하는지 확인합니다.

## 기대 결과

1. nearby-location policy가 draft 문서가 아니라 실제 evaluation 기준선으로 연결됩니다.
2. strict region baseline 후보 판단이 계속 `Gemma 4` 우위로 유지됩니다.
