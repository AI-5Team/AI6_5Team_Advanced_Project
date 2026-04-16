# EXP-210 Promotion Surface Lock Region Anchor Profile Snapshot

## 목표

- `EXP-209` candidate를 manifest option profile로 연결하고 snapshot acceptance를 확인합니다.

## 구현

- 파일:
  - `packages/template-spec/manifests/prompt-baseline-v1.json`
  - `packages/template-spec/README.md`
  - `services/worker/tests/test_generation_pipeline.py`
- 추가 profile:
  - `promotion_surface_lock_region_anchor`
- 추가 operational check:
  - `EXP-209`

## 실행

- `python -c "import json; json.load(open(r'E:\\Codeit\\AI6_5Team_Advanced_Project\\packages\\template-spec\\manifests\\prompt-baseline-v1.json', encoding='utf-8')); print('manifest_ok')"`
- `python scripts/run_prompt_baseline_snapshot.py --profile-id promotion_surface_lock_region_anchor --timeout-sec 120 --max-retries 1 --retry-backoff-sec 3`
- worker `_build_prompt_baseline_summary(...)`
- `uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py -q`
- `uv run --project services/api pytest services/api/tests/test_api_smoke.py -q`

artifact:

- `docs/experiments/artifacts/exp-210-promotion-surface-lock-region-anchor-profile-snapshot.json`

## 결과

- snapshot acceptance:
  - `accepted=true`
  - `required_score=100.0`
  - `required_detail_location_leak_count=0`
  - `allow_over_limit_scene_count=0`
- runtime summary:
  - `status=option_match`
  - `recommendedProfileId=promotion_surface_lock_region_anchor`
  - `transportRecommendation.fallbackProfileId=timeout_90s_retry1`
- test:
  - worker `17 passed`
  - api `5 passed`

## 해석

1. default promotion + region emphasis 조합도 이제 runtime이 직접 추천할 수 있는 option profile이 됐습니다.
2. snapshot은 `120초 / retry 1회`로 확인했지만, runtime transport hint는 현재 manifest 구조상 `timeout_90s_retry1` retry guard를 기본 fallback으로 유지합니다.

