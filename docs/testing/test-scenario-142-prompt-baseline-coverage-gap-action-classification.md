# Test Scenario 142

## 제목

prompt baseline coverage gap action classification 검증

## 목적

- `coverageHint`가 nearest profile과 mismatch 축뿐 아니라, gap 분류와 추천 액션까지 일관되게 계산하는지 확인합니다.
- exact match가 있는 API 시나리오에서는 `coverageHint=null`이 유지되는지 확인합니다.

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
  - `coverageHint.nearestProfileId=new_menu_friendly_strict_region_anchor`
  - `coverageHint.mismatchDimensions=["quickOptions.emphasizeRegion"]`
  - `coverageHint.gapClass=quick_option_gap`
  - `coverageHint.recommendedAction=consider_option_profile`
- api smoke:
  - `coverageHint=null`
- web build:
  - `CoverageHintCard`가 `gap class / recommended action`을 포함해 정상 빌드됩니다.

## 이번 실행 결과

- `python -m py_compile services/worker/pipelines/generation.py` 통과
- worker test 통과
- api test 통과
- `npm run build:web` 통과

## 판정

- coverage gap action classification은 worker/api/web 전 구간에서 의도한 shape로 반영됐습니다.
- 이제 coverage gap도 단순 미커버리지 알림이 아니라, 다음 실험 액션 후보까지 같이 보여줍니다.
