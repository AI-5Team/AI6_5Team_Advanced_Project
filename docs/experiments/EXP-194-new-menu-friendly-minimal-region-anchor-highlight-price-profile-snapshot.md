# EXP-194 New Menu Friendly Minimal Region Anchor Highlight Price Profile Snapshot

## 목표

- `EXP-193` candidate를 manifest option profile로 연결하고 snapshot acceptance를 확인합니다.

## 구현

- 파일:
  - `packages/template-spec/manifests/prompt-baseline-v1.json`
  - `packages/template-spec/README.md`
  - `services/worker/tests/test_generation_pipeline.py`
- 추가 profile:
  - `new_menu_friendly_minimal_region_anchor_highlight_price`

## 실행

- `python scripts/run_prompt_baseline_snapshot.py --profile-id new_menu_friendly_minimal_region_anchor_highlight_price`
- `uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py -q`
- `uv run --project services/api pytest services/api/tests/test_api_smoke.py -q`

artifact:

- `docs/experiments/artifacts/exp-194-new-menu-friendly-minimal-region-anchor-highlight-price-profile-snapshot.json`

## 결과

- snapshot acceptance:
  - `accepted=true`
  - `required_score=100.0`
  - `required_detail_location_leak_count=0`
  - `allow_over_limit_scene_count=0`
- runtime summary:
  - `status=option_match`
  - `recommendedProfileId=new_menu_friendly_minimal_region_anchor_highlight_price`
- test:
  - worker `13 passed`
  - api `5 passed`

## 해석

1. 이제 `new_menu / highlightPrice=true / emphasizeRegion=false`도 coverage gap이 아니라 exact option match입니다.
2. `highlightPrice=true`를 숫자 가격 대신 menu value foreground로 해석하는 non-region 기준선이 생겼습니다.

