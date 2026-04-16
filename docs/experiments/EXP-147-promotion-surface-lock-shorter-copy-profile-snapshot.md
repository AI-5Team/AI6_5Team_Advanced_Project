# EXP-147 Promotion Surface Lock Shorter Copy Profile Snapshot

## 배경

- `EXP-146`에서 `Gemma 4 + surface-lock candidate + 90초/retry 1회`가 `3/3 all pass`를 기록했습니다.
- 이 정도면 실험 로그에만 남기는 것보다 `prompt-baseline-v1.json`의 option profile로 연결할 수 있는지 확인하는 편이 맞습니다.
- 이번 단계는 `T01 new_menu`에서 했던 `EXP-136`과 같은 흐름입니다.

## 목표

1. `prompt-baseline-v1.json`에 `promotion / shorterCopy=false` option profile을 추가합니다.
2. 같은 profile을 snapshot runner로 다시 실행해 acceptance를 확인합니다.
3. runtime summary가 이 profile과 transport recommendation을 실제로 읽는지도 확인합니다.

## 구현

### 1. manifest option profile 추가

- 파일: `packages/template-spec/manifests/prompt-baseline-v1.json`
- 추가 profile:
  - `promotion_surface_lock_shorter_copy_off`
- 선택 모델:
  - `Gemma 4`
- source experiment:
  - `EXP-146`

### 2. operational check 추가

- 파일: `packages/template-spec/manifests/prompt-baseline-v1.json`
- 추가 check:
  - `EXP-145`
- transport recommendation:
  - `defaultProfileId = default_60s_no_retry`
  - `fallbackProfileId = timeout_90s_retry1`
  - `trigger = use_when_profile_recommended`

### 3. README / snapshot runner 보강

- 파일:
  - `packages/template-spec/README.md`
  - `scripts/run_prompt_baseline_snapshot.py`
- 추가 내용:
  - 새 option profile 목록 반영
  - snapshot runner에 `--timeout-sec`, `--max-retries`, `--retry-backoff-sec` 지원 추가

## 실행

1. compile
   - `python -m py_compile scripts/run_prompt_baseline_snapshot.py`
2. profile snapshot
   - `python scripts/run_prompt_baseline_snapshot.py --profile-id promotion_surface_lock_shorter_copy_off --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`
3. runtime summary check
   - worker `_build_prompt_baseline_summary(...)` 호출로 `recommendedProfileId`, `transportRecommendation` 확인

## snapshot 결과

- artifact:
  - `docs/experiments/artifacts/exp-147-promotion-surface-lock-shorter-copy-profile-snapshot.json`

요약:

- `accepted = true`
- `required_score = 100.0`
- `required_detail_location_leak_count = 0`
- `allow_over_limit_scene_count = 0`

## runtime summary 확인 결과

- `recommendedProfileId = promotion_surface_lock_shorter_copy_off`
- `status = option_match`
- `recommendedModel = Gemma 4`
- `transportRecommendation`
  - `mode = transport_profile_required`
  - `defaultProfileId = default_60s_no_retry`
  - `fallbackProfileId = timeout_90s_retry1`
  - `sourceExperimentId = EXP-145`

## 해석

1. `promotion / shorterCopy=false`는 이제 더 이상 coverage gap 후보만이 아닙니다.
2. manifest 안에 실제 option profile로 연결됐고, snapshot acceptance도 통과했습니다.
3. runtime summary도 이 컨텍스트에서 해당 profile과 transport recommendation을 같이 노출할 수 있습니다.

## 판단

- 현재 기준에서 `promotion_surface_lock_shorter_copy_off`는 candidate profile로 유지해도 충분합니다.
- 다만 여전히 `main baseline`을 대체하는 것은 아닙니다.
- 이 profile은 `T02 promotion / highlightPrice=true / shorterCopy=false / emphasizeRegion=false` 조건에서만 추천하는 coverage option으로 두는 편이 맞습니다.

## 결론

- 이번 단계로 `P1` 두 번째 후보는 `실험 성공 -> candidate profile 등록 -> snapshot acceptance`까지 이어졌습니다.
- 즉 `EXP-144`에서 막혔던 축을 그대로 포기하지 않고, `transport + surface lock`으로 rescue해 manifest 레벨까지 연결한 셈입니다.

## 관련 파일

- `packages/template-spec/manifests/prompt-baseline-v1.json`
- `packages/template-spec/README.md`
- `scripts/run_prompt_baseline_snapshot.py`
- `docs/experiments/artifacts/exp-147-promotion-surface-lock-shorter-copy-profile-snapshot.json`
