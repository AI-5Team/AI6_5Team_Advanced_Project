# Test Scenario 123 - Copy Deck Result Structure Visibility

## 목적

- worker/api/web이 모두 `copyDeck`를 같은 shape로 다루는지 확인합니다.

## 확인 항목

1. worker pipeline
   - `render-meta.json`에 `copyDeck`가 포함됩니다.
   - `T01` 기준 body block이 2개 생성됩니다.
2. API smoke
   - `/result` 응답에 `copyDeck`가 포함됩니다.
3. web build
   - result/history 화면에서 `CopyDeckSummary`가 타입 오류 없이 빌드됩니다.

## 실행

```powershell
python -m py_compile services/worker/pipelines/generation.py
uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py -q
uv run --project services/api pytest services/api/tests/test_api_smoke.py -q
npm run build:web
```

## 기대 결과

- `result.copyDeck` 기준으로 hook / body / cta 구조를 결과/이력 화면에서 바로 확인할 수 있습니다.
