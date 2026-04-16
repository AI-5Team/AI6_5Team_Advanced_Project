# EXP-153 Promotion Surface Lock Highlight Price Off Shorter Copy Profile Snapshot

## 배경

- `EXP-152`에서 combined promotion 조합이 `3/3 all pass`를 기록했습니다.
- 이 조합은 기존 promotion option 두 개 사이의 공백 한 칸이었고, 현재 기준으로는 manifest에 직접 연결해도 되는 상태입니다.

## 목표

1. `prompt-baseline-v1.json`에 combined promotion option profile을 추가합니다.
2. transport recommendation까지 같이 연결합니다.
3. snapshot acceptance와 runtime summary recommendation을 확인합니다.

## 구현

### 1. manifest option profile 추가

- 파일: `packages/template-spec/manifests/prompt-baseline-v1.json`
- 추가 profile:
  - `promotion_surface_lock_highlight_price_off_shorter_copy_off`

### 2. operational check 추가

- 파일: `packages/template-spec/manifests/prompt-baseline-v1.json`
- 추가 check:
  - `EXP-152`
- notes:
  - `EXP-143` highlightPrice=false 기본 `60초` timeout evidence
  - `EXP-145` shorterCopy=false 기본 `60초` timeout evidence
  - `EXP-152` combined scenario `90초 / retry 1회` validation evidence

### 3. README 갱신

- 파일:
  - `packages/template-spec/README.md`

## 실행

1. manifest 검증
   - `python -c "import json; json.load(open(r'...\\packages\\template-spec\\manifests\\prompt-baseline-v1.json', encoding='utf-8')); print('manifest_ok')"`
2. snapshot
   - `python scripts/run_prompt_baseline_snapshot.py --profile-id promotion_surface_lock_highlight_price_off_shorter_copy_off --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`
3. runtime summary check
   - worker `_build_prompt_baseline_summary(...)` 호출

## 결과

- artifact:
  - `docs/experiments/artifacts/exp-153-promotion-surface-lock-highlight-price-off-shorter-copy-profile-snapshot.json`
- snapshot:
  - `accepted = true`
- runtime summary:
  - `recommendedProfileId = promotion_surface_lock_highlight_price_off_shorter_copy_off`
  - `status = option_match`
  - `transportRecommendation.fallbackProfileId = timeout_90s_retry1`

## 해석

1. combined promotion 조합도 이제 manifest 안에서 직접 추천 가능한 option profile이 됐습니다.
2. runtime summary도 이 컨텍스트에서 profile과 transport recommendation을 같이 반환할 수 있습니다.

## 판단

- 이 profile은 `main baseline`을 대체하는 것이 아니라, `highlightPrice=false + shorterCopy=false` coverage gap을 메우는 candidate로 유지하는 편이 맞습니다.

## 결론

- promotion의 non-region 단일/인접 조합 공백은 이 단계까지 오면서 대부분 메워졌습니다.

## 관련 파일

- `packages/template-spec/manifests/prompt-baseline-v1.json`
- `packages/template-spec/README.md`
- `docs/experiments/artifacts/exp-153-promotion-surface-lock-highlight-price-off-shorter-copy-profile-snapshot.json`
