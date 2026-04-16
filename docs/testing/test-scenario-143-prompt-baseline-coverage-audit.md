# Test Scenario 143

## 제목

prompt baseline coverage audit 및 nearest-profile weighting 검증

## 목적

- coverage audit script가 현재 manifest coverage 분포를 artifact로 남기는지 확인합니다.
- nearest profile 선택 시 구조 mismatch보다 quick option mismatch를 덜 심각하게 보도록 weighting이 반영됐는지 확인합니다.

## 실행

1. compile
   - `python -m py_compile services/worker/pipelines/generation.py scripts/run_prompt_baseline_coverage_audit.py`
2. worker test
   - `uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py -q`
3. api test
   - `uv run --project services/api pytest services/api/tests/test_api_smoke.py -q`
4. web build
   - `npm run build:web`
5. coverage audit
   - `python scripts/run_prompt_baseline_coverage_audit.py`

## 기대 결과

- worker 회귀 테스트:
  - `new_menu / T01 / friendly / highlightPrice=true / shorterCopy=true / emphasizeRegion=false`
  - `coverageHint.nearestProfileId=new_menu_friendly_strict_region_anchor`
  - `coverageHint.gapClass=quick_option_gap`
- coverage audit aggregate:
  - `totalContexts=24`
  - `default_match=1`
  - `option_match=2`
  - `coverage_gap=21`
  - `quick_option_gap=21`
  - `exact_match=3`

## 이번 실행 결과

- `python -m py_compile services/worker/pipelines/generation.py scripts/run_prompt_baseline_coverage_audit.py` 통과
- worker test 통과
- api test 통과
- `npm run build:web` 통과
- `python scripts/run_prompt_baseline_coverage_audit.py` 통과

## 판정

- coverage audit는 현재 manifest coverage 분포를 artifact로 정상 기록했습니다.
- nearest profile weighting 보정 이후, quick option 차이만 있는 케이스가 더 이상 잘못 `scenario_gap`로 분류되지 않습니다.
