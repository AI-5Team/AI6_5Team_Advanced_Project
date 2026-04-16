# EXP-206 Promotion Surface Lock Shorter Copy Off Region Anchor Profile Snapshot

## 목표

- `EXP-205` candidate를 manifest option profile로 연결하고 snapshot acceptance를 확인합니다.

## 구현

- 파일:
  - `packages/template-spec/manifests/prompt-baseline-v1.json`
  - `packages/template-spec/README.md`
  - `services/worker/tests/test_generation_pipeline.py`
- 추가 profile:
  - `promotion_surface_lock_shorter_copy_off_region_anchor`
- 추가 operational check:
  - `EXP-205`

## 실행

- `python -c "import json; json.load(open(r'E:\\Codeit\\AI6_5Team_Advanced_Project\\packages\\template-spec\\manifests\\prompt-baseline-v1.json', encoding='utf-8')); print('manifest_ok')"`
- `python scripts/run_prompt_baseline_snapshot.py --profile-id promotion_surface_lock_shorter_copy_off_region_anchor --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`
- worker `_build_prompt_baseline_summary(...)`
- `uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py -q`
- `uv run --project services/api pytest services/api/tests/test_api_smoke.py -q`

artifact:

- `docs/experiments/artifacts/exp-206-promotion-surface-lock-shorter-copy-off-region-anchor-profile-snapshot.json`

## 결과

- snapshot acceptance:
  - `accepted=true`
  - `required_score=100.0`
  - `required_detail_location_leak_count=0`
  - `allow_over_limit_scene_count=0`
- runtime summary:
  - `status=option_match`
  - `recommendedProfileId=promotion_surface_lock_shorter_copy_off_region_anchor`
  - `transportRecommendation.fallbackProfileId=timeout_90s_retry1`
- test:
  - worker `17 passed`
  - api `5 passed`

## 해석

1. `highlightPrice=true / shorterCopy=false / emphasizeRegion=true` 조합도 이제 exact option match로 추천됩니다.
2. 설명 여유가 있는 profile이지만 region policy와 transport hint가 함께 묶여 runtime 사용성이 더 좋아졌습니다.

