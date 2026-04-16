# Test Scenario 141

## 제목

prompt baseline coverage gap diagnostics 검증

## 목적

- exact match가 없을 때 `coverageHint`가 nearest profile과 mismatch 축을 일관되게 계산하는지 확인합니다.
- exact match가 있는 API 시나리오에서는 `coverageHint=null`로 유지되는지 확인합니다.

## 실행

1. compile
   - `python -m py_compile services/worker/pipelines/generation.py`
2. worker test
   - `uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py -q`
3. api test
   - `uv run --project services/api pytest services/api/tests/test_api_smoke.py -q`
4. web build
   - `npm run build:web`

## 기대 결과

- worker smoke:
  - `executionHint.status=coverage_gap`
  - `coverageHint.nearestProfileId=new_menu_friendly_strict_region_anchor`
  - `coverageHint.nearestProfileKind=option`
  - `coverageHint.mismatchDimensions=["quickOptions.emphasizeRegion"]`
- api smoke:
  - `executionHint.status=option_match`
  - `coverageHint=null`
- web build:
  - `prompt-baseline-summary` component가 `CoverageHintCard`를 포함해 정상 빌드됩니다.

## 이번 실행 결과

- `python -m py_compile services/worker/pipelines/generation.py` 통과
- worker test 통과
- api test 통과
- `npm run build:web` 통과

## 판정

- coverage gap 진단 정보는 worker/api/web 전 구간에서 의도한 shape로 반영됐습니다.
- 이제 exact match가 없는 케이스도 "가장 가까운 profile"과 "mismatch 축" 기준으로 바로 해석할 수 있습니다.
