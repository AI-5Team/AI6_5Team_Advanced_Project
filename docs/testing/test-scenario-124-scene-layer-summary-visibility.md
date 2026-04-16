# Test Scenario 124 - Scene Layer Summary Visibility

## 목적

- worker/api/web이 `sceneLayerSummary`를 같은 shape로 다루는지 확인합니다.

## 확인 항목

1. worker pipeline
   - `render-meta.json`에 `sceneLayerSummary`가 포함됩니다.
   - `T01` 기준 item이 4개 생성됩니다.
2. API smoke
   - `/result` 응답에 `sceneLayerSummary`가 포함됩니다.
3. web build
   - `ScenePlanPreviewLinks`와 `scene-frame`에서 `sceneLayerSummary`를 사용해도 타입 오류가 없습니다.

## 실행

```powershell
python -m py_compile services/worker/pipelines/generation.py
uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py -q
uv run --project services/api pytest services/api/tests/test_api_smoke.py -q
npm run build:web
```

## 기대 결과

- preview 카드에서 각 scene의 `hook/body/cta` 담당 역할을 바로 확인할 수 있고, scene-frame 안에서도 현재 scene의 layer label이 같이 보입니다.
