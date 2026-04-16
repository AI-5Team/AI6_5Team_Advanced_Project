# EXP-149 Promotion Surface Lock Highlight Price Profile Snapshot

## 배경

- `EXP-148`에서 `promotion / highlightPrice=false` 축은 `Gemma 4 + 90초 / retry 1회` 기준으로 `3/3 all pass`를 기록했습니다.
- 지금까지 manifest에는 `highlightPrice=false` 전용 option profile이 없어서, runtime recommendation metadata도 이 축을 직접 가리키지 못했습니다.
- 따라서 이번 단계는 실험 로그를 남기는 수준이 아니라, 실제 `prompt-baseline-v1.json`에 연결하고 snapshot acceptance까지 확인하는 것입니다.

## 목표

1. `prompt-baseline-v1.json`에 `promotion / highlightPrice=false` option profile을 추가합니다.
2. `EXP-143`의 기본 `60초` timeout evidence와 `EXP-148`의 `90초 / retry 1회` evidence를 operational check로 연결합니다.
3. snapshot acceptance와 worker runtime summary가 새 profile을 정상적으로 읽는지 확인합니다.

## 구현

### 1. manifest option profile 추가

- 파일: `packages/template-spec/manifests/prompt-baseline-v1.json`
- 추가 profile:
  - `promotion_surface_lock_highlight_price_off`
- 선택 모델:
  - `Gemma 4`
- source experiment:
  - `EXP-148`

### 2. operational check 추가

- 파일: `packages/template-spec/manifests/prompt-baseline-v1.json`
- 추가 check:
  - `EXP-148`
- transport recommendation:
  - `defaultProfileId = default_60s_no_retry`
  - `fallbackProfileId = timeout_90s_retry1`
  - `trigger = use_when_profile_recommended`
- notes:
  - `EXP-143` repeatability의 기본 `60초` timeout evidence
  - `EXP-148`의 `90초 / retry 1회` validation evidence

### 3. README 갱신

- 파일:
  - `packages/template-spec/README.md`
- 추가 내용:
  - 새 option profile 목록 반영

## 실행

1. manifest 검증
   - `python -c "import json; json.load(open(r'...\\packages\\template-spec\\manifests\\prompt-baseline-v1.json', encoding='utf-8')); print('manifest_ok')"`
2. profile snapshot
   - `python scripts/run_prompt_baseline_snapshot.py --profile-id promotion_surface_lock_highlight_price_off --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`
3. runtime summary check
   - worker `_build_prompt_baseline_summary(...)` 호출

## snapshot 결과

- artifact:
  - `docs/experiments/artifacts/exp-149-promotion-surface-lock-highlight-price-profile-snapshot.json`

요약:

- `accepted = true`
- `required_score = 100.0`
- `required_detail_location_leak_count = 0`
- `allow_over_limit_scene_count = 0`

## runtime summary 확인 결과

- `recommendedProfileId = promotion_surface_lock_highlight_price_off`
- `status = option_match`
- `recommendedModel = Gemma 4`
- `transportRecommendation`
  - `mode = transport_profile_required`
  - `defaultProfileId = default_60s_no_retry`
  - `fallbackProfileId = timeout_90s_retry1`
  - `sourceExperimentId = EXP-148`

## 해석

1. `promotion / highlightPrice=false`는 이제 manifest 안에서 직접 참조 가능한 option profile이 됐습니다.
2. runtime summary도 이 컨텍스트에서 해당 profile과 transport recommendation을 같이 노출할 수 있습니다.
3. 즉 이번 축은 더 이상 “예전에 한번 실험해 본 조합”이 아니라, 운영 기준에서 조건부로 추천 가능한 baseline option입니다.

## 판단

- `promotion_surface_lock_highlight_price_off`는 candidate profile로 유지할 수 있습니다.
- 이 profile은 `main baseline`을 대체하지 않고, `highlightPrice=false` coverage gap을 메우는 용도로만 사용하는 편이 맞습니다.

## 결론

- 이번 단계로 남아 있던 `P1` 첫 후보도 `실험 통과 -> candidate profile 등록 -> snapshot acceptance -> runtime recommendation 연결`까지 이어졌습니다.
- 다음 기준선은 새 profile들이 실제 manifest coverage gap을 얼마나 줄였는지 다시 audit하거나, `P2` 축으로 넘어가는 것입니다.

## 관련 파일

- `packages/template-spec/manifests/prompt-baseline-v1.json`
- `packages/template-spec/README.md`
- `docs/experiments/artifacts/exp-149-promotion-surface-lock-highlight-price-profile-snapshot.json`
