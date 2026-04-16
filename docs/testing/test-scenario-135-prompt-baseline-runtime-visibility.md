# Test Scenario 135

## 제목

Prompt baseline summary가 worker/API/web에 동일하게 노출되는지 확인

## 목적

- `render-meta.json`에 `promptBaselineSummary`가 포함되는지 확인합니다.
- `/api/projects/{projectId}/result`가 같은 field를 반환하는지 확인합니다.
- web build가 새 summary component와 shared contract 확장까지 포함해 깨지지 않는지 확인합니다.

## 절차

1. python compile
   - `python -m py_compile services/worker/pipelines/generation.py services/api/app/services/runtime.py services/api/app/schemas/api.py`
2. manifest parse
   - `python -c "import json, pathlib; json.loads(pathlib.Path('packages/template-spec/manifests/prompt-baseline-v1.json').read_text(encoding='utf-8')); print('ok')"`
3. worker pipeline test
   - `uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py -q`
4. api smoke test
   - `uv run --project services/api pytest services/api/tests/test_api_smoke.py -q`
5. web build
   - `npm run build:web`

## 기대 결과

### worker

- `render_meta["promptBaselineSummary"]["baselineId"] == "PB-001"`
- `render_meta["promptBaselineSummary"]["defaultProfile"]["profileId"] == "main_baseline"`
- `render_meta["promptBaselineSummary"]["recommendedProfile"] is None` for `T01 new_menu` test fixture

### api

- `/result` payload에 `promptBaselineSummary`가 포함됩니다.
- smoke fixture에서는 `defaultProfile.profileId == "main_baseline"`이고 `recommendedProfile == null`입니다.

### web

- type check / Next build가 통과합니다.
- workbench/history 결과 화면에서 prompt baseline summary component가 렌더될 수 있습니다.

## 이번 실행 결과

- 통과
  - `python -m py_compile services/worker/pipelines/generation.py services/api/app/services/runtime.py services/api/app/schemas/api.py`
  - `python -c "import json, pathlib; json.loads(pathlib.Path('packages/template-spec/manifests/prompt-baseline-v1.json').read_text(encoding='utf-8')); print('ok')"`
  - `uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py -q`
  - `uv run --project services/api pytest services/api/tests/test_api_smoke.py -q`
  - `npm run build:web`
