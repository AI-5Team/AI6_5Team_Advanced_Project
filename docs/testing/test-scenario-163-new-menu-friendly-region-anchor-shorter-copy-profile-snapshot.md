# Test Scenario 163

## 목적

- `new_menu_friendly_region_anchor_shorter_copy` profile이 snapshot acceptance와 runtime summary에 실제 연결되는지 확인합니다.

## 실행

- `python scripts/run_prompt_baseline_snapshot.py --profile-id new_menu_friendly_region_anchor_shorter_copy`
- worker `_build_prompt_baseline_summary(...)`
- `uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py -q`
- `uv run --project services/api pytest services/api/tests/test_api_smoke.py -q`

## 기대 결과

- snapshot `accepted=true`
- runtime summary `status=option_match`
- `recommendedProfileId=new_menu_friendly_region_anchor_shorter_copy`

## 실제 결과

- snapshot `accepted=true`
- `recommendedProfileId=new_menu_friendly_region_anchor_shorter_copy`
- worker `5 passed`
- api `5 passed`

## 판정

- 통과
