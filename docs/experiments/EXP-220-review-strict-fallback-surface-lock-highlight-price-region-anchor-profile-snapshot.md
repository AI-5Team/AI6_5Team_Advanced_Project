# EXP-220 Review Strict Fallback Surface Lock Highlight Price Region Anchor Profile Snapshot

## 목표

- `EXP-219` candidate를 manifest option profile로 연결하고 snapshot acceptance를 확인합니다.

## 구현

- 파일:
  - `packages/template-spec/manifests/prompt-baseline-v1.json`
  - `packages/template-spec/README.md`
  - `services/worker/tests/test_generation_pipeline.py`
- 추가 profile:
  - `review_strict_fallback_surface_lock_highlight_price_region_anchor`

## 실행

- `python scripts/run_prompt_baseline_snapshot.py --profile-id review_strict_fallback_surface_lock_highlight_price_region_anchor`
- worker `_build_prompt_baseline_summary(...)`
- `uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py`
- `uv run --project services/api pytest services/api/tests/test_api_smoke.py -q`

artifact:

- `docs/experiments/artifacts/exp-220-review-strict-fallback-surface-lock-highlight-price-region-anchor-profile-snapshot.json`

## 결과

- snapshot acceptance:
  - `accepted=true`
  - `required_score=100.0`
  - `required_detail_location_leak_count=0`
  - `allow_over_limit_scene_count=0`
- runtime summary:
  - `status=option_match`
  - `recommendedProfileId=review_strict_fallback_surface_lock_highlight_price_region_anchor`
- test:
  - worker `21 passed`
  - api `5 passed`

## 해석

1. review default region 강조 조합도 runtime에서 직접 추천 가능한 option profile이 됐습니다.
2. 이 snapshot까지 통과하면서 review region emphasis 4건은 모두 manifest, runtime summary, test 기준으로 연결됐습니다.
