# EXP-170 New Menu Friendly Region Anchor Highlight Price Shorter Copy Profile Snapshot

## 목표

- `EXP-169` candidate를 manifest option profile로 연결하고 snapshot acceptance를 확인합니다.

## 구현

- 파일:
  - `packages/template-spec/manifests/prompt-baseline-v1.json`
  - `packages/template-spec/README.md`
  - `services/worker/tests/test_generation_pipeline.py`
- 추가 profile:
  - `new_menu_friendly_region_anchor_highlight_price_shorter_copy`

## 실행

- `python -c "import json; json.load(open(r'E:\\Codeit\\AI6_5Team_Advanced_Project\\packages\\template-spec\\manifests\\prompt-baseline-v1.json', encoding='utf-8')); print('manifest_ok')"`
- `python scripts/run_prompt_baseline_snapshot.py --profile-id new_menu_friendly_region_anchor_highlight_price_shorter_copy`
- worker `_build_prompt_baseline_summary(...)`
- `uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py -q`
- `uv run --project services/api pytest services/api/tests/test_api_smoke.py -q`

artifact:

- `docs/experiments/artifacts/exp-170-new-menu-friendly-region-anchor-highlight-price-shorter-copy-profile-snapshot.json`

## 결과

- snapshot acceptance:
  - `accepted=true`
  - `required_score=100.0`
  - `required_detail_location_leak_count=0`
  - `allow_over_limit_scene_count=0`
- runtime summary:
  - `status=option_match`
  - `recommendedProfileId=new_menu_friendly_region_anchor_highlight_price_shorter_copy`
  - `transportRecommendation=null`
- test:
  - worker `7 passed`
  - api `5 passed`

## 해석

1. `new_menu / highlightPrice=true / shorterCopy=true / emphasizeRegion=true`는 이제 manifest 안의 실제 candidate option profile입니다.
2. runtime summary도 이 조건에서 새 profile을 exact match로 추천합니다.
3. 이제 `new_menu` 비지역 quick option 공백은 사실상 모두 정리됐습니다.
