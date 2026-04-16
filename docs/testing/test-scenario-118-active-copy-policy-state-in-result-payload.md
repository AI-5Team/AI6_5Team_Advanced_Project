# Test Scenario 118 - Active Copy Policy State In Result Payload

## 목적

- worker packaging 결과가 `copyPolicy` active state를 `render-meta.json`과 API result payload에 남기는지 확인합니다.
- result/history 화면이 static template rule뿐 아니라 실제 payload state를 읽도록 연결됐는지 확인합니다.

## 확인 항목

1. worker pipeline test
   - `render-meta.json`에 `copyPolicy.detailLocationPolicyId = strict_all_surfaces`
   - `copyPolicy.guardActive = true`
   - `copyPolicy.detailLocationPresent = true`
2. API smoke test
   - `/api/projects/{projectId}/result` 응답에 `copyPolicy`가 포함됨
   - `quickOptions.emphasizeRegion = true`인 smoke flow에서 `copyPolicy.emphasizeRegionRequested = true`
3. web build
   - `CopyPolicySummary`가 `activePolicy` prop을 받아도 빌드가 깨지지 않음
   - `demo-workbench`, `history-board`에서 `result.copyPolicy` 전달이 정상임

## 실행

```powershell
python -m py_compile services/worker/pipelines/generation.py
uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py -q
uv run --project services/api pytest services/api/tests/test_api_smoke.py -q
npm run build:web
```

## 기대 결과

- worker/api/web 세 경로가 모두 통과합니다.
- 결과 payload와 UI 카드에서 `strict_all_surfaces · guard active` 상태를 같은 기준으로 확인할 수 있습니다.
