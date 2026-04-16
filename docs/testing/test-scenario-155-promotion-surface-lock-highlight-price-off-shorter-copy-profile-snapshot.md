# Test Scenario 155

## 제목

promotion surface-lock highlightPrice=false + shorterCopy=false profile snapshot 및 runtime summary 확인

## 목적

- `prompt-baseline-v1.json`에 추가한 `promotion_surface_lock_highlight_price_off_shorter_copy_off` profile이 snapshot acceptance를 통과하는지 확인합니다.
- worker runtime summary가 이 profile과 transport recommendation을 같이 읽는지 확인합니다.

## 실행

1. manifest 검증
   - `python -c "import json; json.load(open(r'...\\packages\\template-spec\\manifests\\prompt-baseline-v1.json', encoding='utf-8')); print('manifest_ok')"`
2. snapshot
   - `python scripts/run_prompt_baseline_snapshot.py --profile-id promotion_surface_lock_highlight_price_off_shorter_copy_off --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`
3. runtime summary check
   - worker `_build_prompt_baseline_summary(...)` 호출

## 기대 결과

- snapshot acceptance가 `accepted=true`여야 합니다.
- runtime summary는 `option_match`, `promotion_surface_lock_highlight_price_off_shorter_copy_off`, `timeout_90s_retry1` recommendation을 반환해야 합니다.

## 이번 실행 결과

- snapshot:
  - `accepted=true`
- runtime summary:
  - `recommendedProfileId=promotion_surface_lock_highlight_price_off_shorter_copy_off`
  - `status=option_match`
  - `transportRecommendation.fallbackProfileId=timeout_90s_retry1`

## 판정

- combined promotion option profile은 manifest acceptance와 runtime recommendation 연결까지 정상 동작했습니다.
