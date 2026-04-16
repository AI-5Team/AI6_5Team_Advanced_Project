# EXP-198 New Menu Friendly Minimal Region Anchor Highlight Price Shorter Copy Profile Snapshot

## 목표

- `EXP-197` candidate를 manifest option profile로 연결하고 snapshot acceptance를 확인합니다.

## 구현

- 파일:
  - `packages/template-spec/manifests/prompt-baseline-v1.json`
  - `packages/template-spec/README.md`
  - `services/worker/tests/test_generation_pipeline.py`
- 추가 profile:
  - `new_menu_friendly_minimal_region_anchor_highlight_price_shorter_copy`

## 실행

- `python scripts/run_prompt_baseline_snapshot.py --profile-id new_menu_friendly_minimal_region_anchor_highlight_price_shorter_copy`
- `uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py -q`
- `uv run --project services/api pytest services/api/tests/test_api_smoke.py -q`

artifact:

- `docs/experiments/artifacts/exp-198-new-menu-friendly-minimal-region-anchor-highlight-price-shorter-copy-profile-snapshot.json`

## 결과

- snapshot acceptance:
  - `accepted=true`
  - `required_score=100.0`
  - `required_detail_location_leak_count=0`
  - `allow_over_limit_scene_count=0`
- runtime summary:
  - `status=option_match`
  - `recommendedProfileId=new_menu_friendly_minimal_region_anchor_highlight_price_shorter_copy`
- test:
  - worker `14 passed`
  - api `5 passed`

## 해석

1. 이제 `new_menu / highlightPrice=true / shorterCopy=true / emphasizeRegion=false`도 coverage gap이 아니라 exact option match입니다.
2. 결과적으로 `new_menu` 비지역 quick option 조합은 모두 option profile로 정리됐습니다.

