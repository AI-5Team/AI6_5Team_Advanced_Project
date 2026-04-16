# EXP-202 Promotion Surface Lock Highlight Price Off Region Anchor Profile Snapshot

## 목표

- `EXP-201` candidate를 manifest option profile로 연결하고 snapshot acceptance를 확인합니다.

## 구현

- 파일:
  - `packages/template-spec/manifests/prompt-baseline-v1.json`
  - `packages/template-spec/README.md`
  - `services/worker/tests/test_generation_pipeline.py`
- 추가 profile:
  - `promotion_surface_lock_highlight_price_off_region_anchor`
- 추가 operational check:
  - `EXP-201`

## 실행

- `python -c "import json; json.load(open(r'E:\\Codeit\\AI6_5Team_Advanced_Project\\packages\\template-spec\\manifests\\prompt-baseline-v1.json', encoding='utf-8')); print('manifest_ok')"`
- `python scripts/run_prompt_baseline_snapshot.py --profile-id promotion_surface_lock_highlight_price_off_region_anchor --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`
- worker `_build_prompt_baseline_summary(...)`
- `uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py -q`
- `uv run --project services/api pytest services/api/tests/test_api_smoke.py -q`

artifact:

- `docs/experiments/artifacts/exp-202-promotion-surface-lock-highlight-price-off-region-anchor-profile-snapshot.json`

## 결과

- snapshot acceptance:
  - `accepted=true`
  - `required_score=100.0`
  - `required_detail_location_leak_count=0`
  - `allow_over_limit_scene_count=0`
- runtime summary:
  - `status=option_match`
  - `recommendedProfileId=promotion_surface_lock_highlight_price_off_region_anchor`
  - `transportRecommendation.fallbackProfileId=timeout_90s_retry1`
- test:
  - worker `17 passed`
  - api `5 passed`

## 해석

1. `highlightPrice=false / shorterCopy=true / emphasizeRegion=true` 조합은 이제 runtime이 직접 추천할 수 있는 option profile이 됐습니다.
2. prompt 근거와 transport recommendation이 함께 묶였기 때문에 다음 세션부터는 수동 매핑 없이 exact option match로 볼 수 있습니다.

