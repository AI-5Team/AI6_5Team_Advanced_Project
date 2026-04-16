# Test Scenario 139

## 제목

prompt baseline execution advisory payload/UI 확장 검증

## 목적

- `promptBaselineSummary`에 `executionHint`, `operationalChecks`가 추가된 뒤 worker/api/web가 모두 같은 shape를 유지하는지 확인합니다.

## 실행

1. compile
   - `python -m py_compile services/worker/pipelines/generation.py`
2. manifest parse
   - `python -c "import json, pathlib; json.loads(pathlib.Path('packages/template-spec/manifests/prompt-baseline-v1.json').read_text(encoding='utf-8')); print('ok')"`
3. worker test
   - `uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py -q`
4. api test
   - `uv run --project services/api pytest services/api/tests/test_api_smoke.py -q`
5. web build
   - `npm run build:web`

## 기대 결과

- worker smoke:
  - `recommendedProfile=null`
  - `executionHint.status=coverage_gap`
- api smoke:
  - `recommendedProfile.profileId=new_menu_friendly_strict_region_anchor`
  - `executionHint.status=option_match`
- web build:
  - `prompt-baseline-summary` component가 새 필드를 포함해 정상 빌드됩니다.

## 이번 실행 결과

- `python -m py_compile services/worker/pipelines/generation.py` 통과
- manifest parse 통과
- worker test 통과
- api test 통과
- `npm run build:web` 통과

## 판정

- execution advisory 확장은 worker/api/web 전 구간에서 일관된 shape로 반영됐습니다.
- 현재 단계는 recommendation metadata 확장까지이며, 실제 provider routing 자동화는 아직 별도 작업입니다.
