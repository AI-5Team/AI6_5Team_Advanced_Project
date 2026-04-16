# EXP-174 Review Strict Fallback Surface Lock Shorter Copy Off Profile Snapshot

## 목표

- `EXP-173` candidate를 manifest option profile로 연결하고 snapshot acceptance를 확인합니다.

## 구현

- 파일:
  - `packages/template-spec/manifests/prompt-baseline-v1.json`
  - `packages/template-spec/README.md`
  - `services/worker/tests/test_generation_pipeline.py`
- 추가 profile:
  - `review_strict_fallback_surface_lock_shorter_copy_off`

## 실행

- `python -c "import json; json.load(open(r'E:\\Codeit\\AI6_5Team_Advanced_Project\\packages\\template-spec\\manifests\\prompt-baseline-v1.json', encoding='utf-8')); print('manifest_ok')"`
- `python scripts/run_prompt_baseline_snapshot.py --profile-id review_strict_fallback_surface_lock_shorter_copy_off`
- worker `_build_prompt_baseline_summary(...)`
- `uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py -q`
- `uv run --project services/api pytest services/api/tests/test_api_smoke.py -q`

artifact:

- `docs/experiments/artifacts/exp-174-review-strict-fallback-surface-lock-shorter-copy-off-snapshot.json`

## 결과

- snapshot acceptance:
  - `accepted=true`
  - `required_score=100.0`
  - `required_detail_location_leak_count=0`
  - `allow_over_limit_scene_count=0`
- runtime summary:
  - `status=option_match`
  - `recommendedProfileId=review_strict_fallback_surface_lock_shorter_copy_off`
  - `transportRecommendation=null`
- test:
  - worker `8 passed`
  - api `5 passed`

## 해석

1. `review / highlightPrice=false / shorterCopy=false / emphasizeRegion=false`는 이제 manifest 안의 실제 option profile입니다.
2. runtime summary도 이 조건에서 새 profile을 정확히 추천합니다.
3. `review` 축에서 남은 비지역 `P2`는 이제 `highlightPrice=true` 해석 2건뿐입니다.
