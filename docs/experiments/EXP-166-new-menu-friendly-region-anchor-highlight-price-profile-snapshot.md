# EXP-166 New Menu Friendly Region Anchor Highlight Price Profile Snapshot

## 목표

- `EXP-165` candidate를 manifest option profile로 연결하고 snapshot acceptance를 확인합니다.

## 구현

- 파일:
  - `packages/template-spec/manifests/prompt-baseline-v1.json`
  - `packages/template-spec/README.md`
  - `services/worker/tests/test_generation_pipeline.py`
- 추가 profile:
  - `new_menu_friendly_region_anchor_highlight_price`

## 실행

- `python -c "import json; json.load(open(r'E:\\Codeit\\AI6_5Team_Advanced_Project\\packages\\template-spec\\manifests\\prompt-baseline-v1.json', encoding='utf-8')); print('manifest_ok')"`
- `python scripts/run_prompt_baseline_snapshot.py --profile-id new_menu_friendly_region_anchor_highlight_price`
- worker `_build_prompt_baseline_summary(...)`
- `uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py -q`
- `uv run --project services/api pytest services/api/tests/test_api_smoke.py -q`

artifact:

- `docs/experiments/artifacts/exp-166-new-menu-friendly-region-anchor-highlight-price-profile-snapshot.json`

## 결과

- snapshot acceptance:
  - `accepted=true`
  - `required_score=100.0`
  - `required_detail_location_leak_count=0`
  - `allow_over_limit_scene_count=0`
- runtime summary:
  - `status=option_match`
  - `recommendedProfileId=new_menu_friendly_region_anchor_highlight_price`
  - `transportRecommendation=null`
- test:
  - worker `6 passed`
  - api `5 passed`

## 해석

1. `new_menu / highlightPrice=true / emphasizeRegion=true`는 이제 manifest 안의 실제 candidate option profile입니다.
2. runtime summary도 이 조건에서 새 profile을 exact match로 추천합니다.
3. `highlightPrice=true`를 숫자 가격 환각 없이 value emphasis로 해석하는 기준이 manifest 수준까지 연결됐습니다.
