# Test Scenario 125 - Change Impact Summary Visibility

## 목적

- worker/api/web이 모두 `changeImpactSummary`를 같은 shape로 다루는지 확인합니다.

## 확인 항목

1. worker pipeline
   - `render-meta.json`에 `changeImpactSummary`가 포함됩니다.
   - 초기 생성은 `runType=initial`, `activeActions=[]`, `impactLayers=[]`를 유지합니다.
2. API smoke
   - `/result` 응답에 `changeImpactSummary`가 포함됩니다.
   - regenerate sample에서는 `emphasizeRegion` 같은 active action과 `hook` 영향 레이어가 보입니다.
3. web build
   - result/history 화면에서 `ChangeImpactSummary` 카드가 타입 오류 없이 빌드됩니다.

## 실행

```powershell
python -m py_compile services/worker/pipelines/generation.py
uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py -q
uv run --project services/api pytest services/api/tests/test_api_smoke.py -q
npm run build:web
```

## 기대 결과

- `result.changeImpactSummary` 기준으로 현재 run이 어떤 action 때문에 어떤 층을 바꿨는지 결과/이력 화면에서 바로 확인할 수 있습니다.
