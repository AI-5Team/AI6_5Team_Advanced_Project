# Test Scenario 179

## 목적

- `EXP-178`에서 `review_strict_fallback_surface_lock_highlight_price_shorter_copy_off` profile이 snapshot acceptance와 runtime summary에 정상 반영되는지 확인합니다.

## 실행

- `python scripts/run_prompt_baseline_snapshot.py --profile-id review_strict_fallback_surface_lock_highlight_price_shorter_copy_off`
- worker `_build_prompt_baseline_summary(...)`
- `uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py -q`
- `uv run --project services/api pytest services/api/tests/test_api_smoke.py -q`

## 기대 결과

- `accepted=true`
- runtime `status=option_match`
- `recommendedProfileId=review_strict_fallback_surface_lock_highlight_price_shorter_copy_off`

## 실제 결과

- `accepted=true`
- runtime `status=option_match`
- `recommendedProfileId=review_strict_fallback_surface_lock_highlight_price_shorter_copy_off`
- worker `9 passed`
- api `5 passed`

## 판정

- 통과
