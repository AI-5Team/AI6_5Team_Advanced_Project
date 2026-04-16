# Test Scenario 134 - Review Strict Fallback Surface Lock Profile

## 목적

- `prompt-baseline-v1.json` 안의 `review_strict_fallback_surface_lock` profile이 실제로 snapshot runner에서 재현 가능한지 확인합니다.

## 실행 명령

```powershell
python -m py_compile scripts/run_prompt_baseline_snapshot.py
python -c "import json, pathlib; json.loads(pathlib.Path('packages/template-spec/manifests/prompt-baseline-v1.json').read_text(encoding='utf-8')); print('ok')"
python scripts/run_prompt_baseline_snapshot.py --profile-id review_strict_fallback_surface_lock
```

## 기대 결과

- artifact:
  - `docs/experiments/artifacts/exp-132-review-strict-fallback-surface-lock-snapshot.json`
- baseline acceptance:
  - `accepted=true`
- score:
  - `100.0`
- detail location leak count:
  - `0`
- over-limit scene count:
  - `0`

## 확인 포인트

- runner가 `prompt_experiment` source와 `promptVariantId`를 정상적으로 읽는지
- `gpt-5-mini + review_surface_locked_exact_region_anchor` 조합이 실제 snapshot에서도 통과하는지
- main baseline과 별개로 conditional fallback profile을 재현할 수 있는지
