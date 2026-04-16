# EXP-218 Review Strict Fallback Surface Lock Highlight Price Shorter Copy Off Region Anchor Profile Snapshot

## 목표

- `EXP-217` candidate를 manifest option profile로 연결하고 snapshot acceptance를 확인합니다.

## 구현

- 파일:
  - `packages/template-spec/manifests/prompt-baseline-v1.json`
  - `packages/template-spec/README.md`
  - `services/worker/tests/test_generation_pipeline.py`
- 추가 profile:
  - `review_strict_fallback_surface_lock_highlight_price_shorter_copy_off_region_anchor`

## 실행

- `python scripts/run_prompt_baseline_snapshot.py --profile-id review_strict_fallback_surface_lock_highlight_price_shorter_copy_off_region_anchor`
- worker `_build_prompt_baseline_summary(...)`
- `uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py`
- `uv run --project services/api pytest services/api/tests/test_api_smoke.py -q`

artifact:

- `docs/experiments/artifacts/exp-218-review-strict-fallback-surface-lock-highlight-price-shorter-copy-off-region-anchor-profile-snapshot.json`

## 결과

- snapshot acceptance:
  - `accepted=true`
  - `required_score=100.0`
  - `required_detail_location_leak_count=0`
  - `allow_over_limit_scene_count=0`
- runtime summary:
  - `status=option_match`
  - `recommendedProfileId=review_strict_fallback_surface_lock_highlight_price_shorter_copy_off_region_anchor`
- test:
  - worker `21 passed`
  - api `5 passed`

## 해석

1. `review / highlightPrice=true / shorterCopy=false / emphasizeRegion=true` 조합도 runtime 추천 경로에 반영됐습니다.
2. manifest 기준에서 `highlightPrice=true`는 여전히 숫자 가격이 아니라 value foreground 의미로만 유지됩니다.
