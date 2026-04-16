# EXP-186 New Menu Friendly Minimal Region Anchor Profile Snapshot

## 목표

- `EXP-185` candidate를 manifest option profile로 연결하고 snapshot acceptance를 확인합니다.

## 구현

- 파일:
  - `packages/template-spec/manifests/prompt-baseline-v1.json`
  - `packages/template-spec/README.md`
  - `services/worker/tests/test_generation_pipeline.py`
- 추가 profile:
  - `new_menu_friendly_minimal_region_anchor`

## 실행

- `python -c "import json; json.load(open(r'E:\\Codeit\\AI6_5Team_Advanced_Project\\packages\\template-spec\\manifests\\prompt-baseline-v1.json', encoding='utf-8')); print('manifest_ok')"`
- `python scripts/run_prompt_baseline_snapshot.py --profile-id new_menu_friendly_minimal_region_anchor`
- `uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py -q`
- `uv run --project services/api pytest services/api/tests/test_api_smoke.py -q`

artifact:

- `docs/experiments/artifacts/exp-186-new-menu-friendly-minimal-region-anchor-profile-snapshot.json`

## 결과

- snapshot acceptance:
  - `accepted=true`
  - `required_score=100.0`
  - `required_detail_location_leak_count=0`
  - `allow_over_limit_scene_count=0`
- runtime summary:
  - `status=option_match`
  - `recommendedProfileId=new_menu_friendly_minimal_region_anchor`
- test:
  - worker `11 passed`
  - api `5 passed`

## 해석

1. 이제 기본 `new_menu / emphasizeRegion=false` 컨텍스트는 coverage gap이 아니라 실제 option profile로 추천됩니다.
2. generation pipeline 기본 smoke도 새 profile을 반영해 통과했습니다.

