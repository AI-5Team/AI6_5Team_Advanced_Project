# EXP-152 Gemma Promotion Highlight Price Off Shorter Copy Off Surface Lock

## 배경

- `EXP-151` priority refresh 이후 `promotion`에서 남은 최상위 non-region gap은 `highlightPrice=false / shorterCopy=false / emphasizeRegion=false` 1건이었습니다.
- 이 조합은 새 scenario를 파는 것보다, 이미 승격된 `promotion_surface_lock_shorter_copy_off` profile에 `highlightPrice=false` 제약만 더하는 편이 더 자연스러운 후보였습니다.
- 따라서 이번 단계는 `P2 option-adjacent` rescue로 보는 편이 맞습니다.

## 목표

1. `promotion_surface_lock_shorter_copy_off` prompt를 combined scenario 기준 baseline으로 재사용합니다.
2. 여기에 `highlightPrice=false` 제약만 추가한 candidate를 비교합니다.
3. 이 조합도 candidate profile로 승격 가능한지 확인합니다.

## 구현

### 1. scenario 추가

- 파일: `services/worker/experiments/prompt_harness.py`
- 추가 scenario:
  - `scenario-restaurant-promotion-b-grade-real-photo-highlight-price-off-shorter-copy-off`

### 2. prompt experiment 추가

- 파일: `services/worker/experiments/prompt_harness.py`
- 추가 실험:
  - `EXP-152`
- baseline variant:
  - `promotion_surface_lock_shorter_copy_off_baseline_gemma`
- candidate variant:
  - `promotion_surface_locked_highlight_price_off_shorter_copy_off_gemma`

## candidate 핵심 제약

- `shorterCopy=false`이므로 설명은 허용하지만, 그 설명도 가격 숫자보다 메뉴 강점과 방문 이유를 먼저 보여야 함
- `highlightPrice=false`이므로 가격 숫자, 할인폭, `특가`, `할인`, `가성비`를 `hookText`, `benefit`, `urgency`, `captions`, `hashtags` 중심 훅으로 쓰지 않음
- 가격/혜택을 언급해도 raw 숫자나 퍼센트는 headline처럼 쓰지 않고 `caption` 또는 `subText` 안의 보조 정보로만 처리
- `#오늘만할인`, `#가성비`, `#특가`, `#할인중` 같은 price-foreground hashtag 금지
- 기존 shorterCopy=false profile과 동일하게
  - `성수동` exact caption 1회
  - `#성수동` 1개만 허용
  - nearby/detail-location leakage 금지
  - `hookText` 최대 `16자`

## 실행

1. compile
   - `python -m py_compile services/worker/experiments/prompt_harness.py scripts/run_google_prompt_experiment_with_transport.py scripts/run_google_prompt_variant_repeatability_with_transport.py`
2. single run
   - `python scripts/run_google_prompt_experiment_with_transport.py --experiment-id EXP-152 --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`
3. repeatability
   - `python scripts/run_google_prompt_variant_repeatability_with_transport.py --experiment-id EXP-152 --repeat 3 --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`

## 결과

### single run

- artifact:
  - `docs/experiments/artifacts/exp-152-gemma-4-promotion-highlight-price-off-shorter-copy-off-surface-lock-google-transport.json`

#### baseline

- score: `100.0`
- failed checks: 없음

#### candidate

- score: `100.0`
- failed checks: 없음

### repeatability

- artifact:
  - `docs/experiments/artifacts/exp-152-variant-repeatability-google-transport.json`

#### baseline

- `success_count = 3 / 3`
- `avg_score = 100.0`
- `all_runs_passed = true`

#### candidate

- `success_count = 3 / 3`
- `avg_score = 100.0`
- `all_runs_passed = true`

## 해석

1. 이번 combined 조합도 `90초 / retry 1회` 기준에서는 안정적으로 통과했습니다.
2. baseline과 candidate가 점수로 벌어지지는 않았지만, candidate는 `combined quick option`을 별도 profile로 설명할 수 있는 명시적 prompt라는 점에서 가치가 있습니다.
3. 즉 이번 단계의 목적은 "baseline을 압도하는 새 모델"이 아니라, 이미 검증된 option profile을 합성해 coverage를 한 칸 더 메우는 것이었습니다.

## 판단

- 이번 실험은 `실험 성공, profile 승격 가능`으로 봐도 됩니다.
- 다만 candidate의 가치는 성능 우위보다 `조합 전용 operating prompt`를 manifest에 고정할 수 있다는 점입니다.

## 결론

- `promotion / highlightPrice=false / shorterCopy=false / emphasizeRegion=false`도 candidate profile로 올릴 수 있습니다.
- 다음 단계는 manifest option profile 등록과 snapshot acceptance 확인입니다.

## 관련 파일

- `services/worker/experiments/prompt_harness.py`
- `docs/experiments/artifacts/exp-152-gemma-4-promotion-highlight-price-off-shorter-copy-off-surface-lock-google-transport.json`
- `docs/experiments/artifacts/exp-152-variant-repeatability-google-transport.json`
