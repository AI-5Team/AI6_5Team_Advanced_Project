# Test Scenario 140

## 제목

prompt baseline policy hint payload/UI 확장 검증

## 목적

- `promptBaselineSummary.policyHint`가 worker/api/web 전 구간에서 같은 의미로 노출되는지 확인합니다.
- `executionHint`와 `policyHint`가 서로 충돌하지 않고, `coverage_gap`과 `option_match`를 운영 판단 문장으로 안정적으로 번역하는지 확인합니다.

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
  - `policyHint.policyState=coverage_gap`
  - `policyHint.recommendedAction=manual_review_required`
  - `policyHint.requiresManualReview=true`
- api smoke:
  - `executionHint.status=option_match`
  - `policyHint.policyState=option_reference`
  - `policyHint.recommendedAction=use_option_profile_reference`
  - `policyHint.requiresManualReview=false`
- web build:
  - `prompt-baseline-summary` component가 `PolicyHintCard`를 포함해 정상 빌드됩니다.

## 이번 실행 결과

- `python -m py_compile services/worker/pipelines/generation.py` 통과
- worker test 통과
- api test 통과
- `npm run build:web` 통과

## 판정

- `policyHint`는 worker/api/web 전 구간에서 일관된 정책 해석 레이어로 반영됐습니다.
- 현재 단계는 자동 라우팅이 아니라 운영 판단 metadata 확장까지입니다.
