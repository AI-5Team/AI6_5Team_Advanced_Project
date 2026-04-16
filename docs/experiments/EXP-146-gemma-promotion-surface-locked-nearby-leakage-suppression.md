# EXP-146 Gemma Promotion Surface-Locked Nearby Leakage Suppression

## 배경

- `EXP-145`에서 `Gemma 4`는 `promotion / T02 / shorterCopy=false` 축에서 `60초` transport ceiling만 넘기면 다시 실험 가능한 후보라는 점이 확인됐습니다.
- 동시에 timeout이 풀린 뒤에도 `nearby location leaked into strict region budget`가 간헐적으로 남았고, leak surface는 주로 `hashtags`, `subText`에 몰렸습니다.
- 따라서 이번 단계의 질문은 단순했습니다.
  - transport를 `90초 / retry 1회`로 고정한 상태에서
  - `subText/hashtags`만 더 강하게 잠그면
  - `Gemma 4`가 strict baseline repeatability까지 통과하는가

## 목표

1. `EXP-144` baseline prompt를 `Gemma 4` 기준 baseline variant로 다시 고정합니다.
2. `hashtags/subText` nearby leakage를 막는 surface-lock candidate를 추가합니다.
3. `90초 / retry 1회` transport 조건에서 baseline 대비 candidate repeatability가 실제로 개선되는지 확인합니다.

## 구현

### 1. prompt experiment 추가

- 파일: `services/worker/experiments/prompt_harness.py`
- 추가 실험:
  - `EXP-146`
- scenario:
  - `scenario-restaurant-promotion-b-grade-real-photo-shorter-copy-off`
- baseline variant:
  - `promotion_strict_anchor_shorter_copy_off_baseline_gemma`
- candidate variant:
  - `promotion_surface_locked_nearby_leakage_suppression_gemma`

### 2. Google transport 전용 실행 스크립트 추가

- 파일:
  - `scripts/run_google_prompt_experiment_with_transport.py`
  - `scripts/run_google_prompt_variant_repeatability_with_transport.py`
- 목적:
  - Google prompt experiment에서도 `timeoutSec`, `maxRetries`, `retryBackoffSec`를 명시해 transport와 prompt를 분리해서 볼 수 있게 함

## candidate 핵심 제약

- `captions` 중 정확히 1개 caption에만 `성수동` exact string 1회 허용
- region hashtag는 정확히 `#성수동` 1개만 허용
- `#성수동맛집`, `#서울숲맛집`, `#서울숲데이트` 같은 확장형 위치 hashtag 금지
- `서울숲`, `성수역`, `근처`, `인근`, `동네`, `앞`, `옆`, `골목`, `핫플` 같은 nearby/detail-location 표현을 모든 surface에서 금지
- `subText`는 위치 설명 대신 메뉴 강점, 세트 구성, 할인 이유, 퇴근 후 보상감만 남김

## 실행

1. compile
   - `python -m py_compile services/worker/experiments/prompt_harness.py scripts/run_google_prompt_experiment_with_transport.py scripts/run_google_prompt_variant_repeatability_with_transport.py`
2. single run
   - `python scripts/run_google_prompt_experiment_with_transport.py --experiment-id EXP-146 --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`
3. repeatability
   - `python scripts/run_google_prompt_variant_repeatability_with_transport.py --experiment-id EXP-146 --repeat 3 --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`

## 결과

### single run

- artifact:
  - `docs/experiments/artifacts/exp-146-gemma-4-promotion-surface-locked-nearby-leakage-suppression-google-transport.json`

#### baseline

- score: `100.0`
- failed checks: 없음
- hook:
  - `오늘 안 오면 진짜 손해?`

#### candidate

- score: `100.0`
- failed checks: 없음
- hook:
  - `오늘 안 오면 진짜 손해?`

### repeatability

- artifact:
  - `docs/experiments/artifacts/exp-146-variant-repeatability-google-transport.json`

#### baseline

- `success_count = 3 / 3`
- `avg_score = 97.8`
- `all_runs_passed = false`
- 실패 원인:
  - 1회에서 `nearby location leaked into strict region budget`
  - leak surface: `hashtags`
  - 실제 누출 예: `#서울숲데이트`

#### candidate

- `success_count = 3 / 3`
- `avg_score = 100.0`
- `all_runs_passed = true`
- sample hooks:
  - `규카츠 할인, 오늘만 맞나요?`
  - `규카츠 할인, 오늘만 맞나요?`
  - `미친 규카츠 할인, 오늘만?`

## 해석

1. 이번에는 transport와 prompt를 분리해서 볼 수 있었습니다.
2. `90초 / retry 1회` 조건에서는 baseline도 응답은 안정적이었지만, `hashtags`에서 nearby leakage가 1회 남았습니다.
3. candidate는 같은 transport 조건에서 `3/3 all pass`를 만들었습니다.
4. 즉 이번 개선 포인트는 모델 자체 교체가 아니라, `Gemma 4 promotion strict anchor`에서 `hashtags/subText surface lock`을 더 강하게 명시한 것이었습니다.

## 판단

- `Gemma 4 + promotion_surface_locked_nearby_leakage_suppression_gemma + 90초/retry 1회` 조합은 candidate profile 승격을 검토할 수 있는 수준입니다.
- 현재 기준으로는 `EXP-143`, `EXP-144`에서 막혔던 `promotion / shorterCopy=false` gap을 실제 option profile 후보로 연결할 근거가 생겼습니다.

## 결론

- 이번 실험은 `success`로 봐도 됩니다.
- 다만 성공 조건은 분명합니다.
  - prompt만 바뀐 것이 아니라
  - `Gemma 4`의 transport profile도 `90초 / retry 1회`를 전제로 잡아야 합니다.
- 그래서 다음 단계는 실험 문서만 남기는 것이 아니라, manifest option profile과 snapshot 재현까지 연결하는 것입니다.

## 관련 파일

- `services/worker/experiments/prompt_harness.py`
- `scripts/run_google_prompt_experiment_with_transport.py`
- `scripts/run_google_prompt_variant_repeatability_with_transport.py`
- `docs/experiments/artifacts/exp-146-gemma-4-promotion-surface-locked-nearby-leakage-suppression-google-transport.json`
- `docs/experiments/artifacts/exp-146-variant-repeatability-google-transport.json`
