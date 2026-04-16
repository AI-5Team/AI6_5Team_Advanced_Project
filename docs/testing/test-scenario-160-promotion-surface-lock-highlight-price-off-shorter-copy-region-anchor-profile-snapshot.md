# Test Scenario 160

## 목적

- `promotion_surface_lock_highlight_price_off_shorter_copy_off_region_anchor` profile이 snapshot acceptance와 runtime summary에 실제 연결되는지 확인합니다.

## 실행

- `python scripts/run_prompt_baseline_snapshot.py --profile-id promotion_surface_lock_highlight_price_off_shorter_copy_off_region_anchor --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`
- worker `_build_prompt_baseline_summary(...)`
- `uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py -q`
- `uv run --project services/api pytest services/api/tests/test_api_smoke.py -q`

## 기대 결과

- snapshot `accepted=true`
- runtime summary `status=option_match`
- recommended profile id 일치
- worker/api tests 통과

## 실제 결과

- snapshot `accepted=true`
- `recommendedProfileId=promotion_surface_lock_highlight_price_off_shorter_copy_off_region_anchor`
- `fallbackProfileId=timeout_90s_retry1`
- worker `4 passed`
- api `5 passed`

## 판정

- 통과
