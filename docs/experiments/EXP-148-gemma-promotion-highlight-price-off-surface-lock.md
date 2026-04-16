# EXP-148 Gemma Promotion Highlight Price Off Surface Lock

## 배경

- `EXP-143`에서 `promotion / T02 / b_grade_fun / highlightPrice=false / shorterCopy=true / emphasizeRegion=false` 축은 option profile로 올리지 못했습니다.
- 당시 `Gemma 4`는 single run 품질은 통과했지만 repeatability에서 기본 `60초` transport profile로 `3/3 timeout`이 났고, `gpt-5-mini`는 nearby leakage 때문에 품질 기준을 넘지 못했습니다.
- 이후 `EXP-146`, `EXP-147`에서 확인한 패턴은 분명했습니다.
  - `Gemma 4`는 `90초 / retry 1회`로 transport ceiling을 먼저 풀어줘야 하고
  - option-specific guard는 prompt surface에 직접 잠가두는 편이 profile 승격까지 이어지기 쉬웠습니다.

## 목표

1. `highlightPrice=false` 축을 `Gemma 4` 고정 prompt experiment로 다시 확인합니다.
2. `no-price-foreground + no-nearby-leakage`를 같이 묶은 surface-lock candidate를 추가합니다.
3. 현재 기준으로 이 축을 manifest option profile까지 올릴 수 있는지 판단합니다.

## 구현

### 1. prompt experiment 추가

- 파일: `services/worker/experiments/prompt_harness.py`
- 추가 실험:
  - `EXP-148`
- scenario:
  - `scenario-restaurant-promotion-b-grade-real-photo-highlight-price-off`
- baseline variant:
  - `promotion_strict_anchor_highlight_price_off_baseline_gemma`
- candidate variant:
  - `promotion_surface_locked_highlight_price_off_gemma`

## candidate 핵심 제약

- `highlightPrice=false`이므로 `hookText`, `benefit`, `urgency`, `captions`, `hashtags`에서 가격 숫자, 할인폭, `특가`, `할인`, `가성비`를 중심 훅처럼 쓰지 않음
- 가격 대신 `규카츠 식감`, `육즙`, `맥주 페어링`, `퇴근 후 한 끼 이유`를 전면에 둠
- `captions` 3개 중 정확히 1개 caption에만 `성수동` exact string 1회 허용
- region hashtag는 정확히 `#성수동` 1개만 허용
- `#성수동맛집`, `#서울숲맛집`, `#서울숲데이트`, `#퇴근후성수`, `#동네맛집` 같은 확장형/nearby hashtag 금지
- `서울숲`, `서울숲 근처`, `서울숲 인근`, `성수역`, `근처`, `인근`, `동네`, `앞`, `옆`, `골목`, `핫플` 같은 nearby/detail-location 표현을 모든 surface에서 금지
- `subText`는 위치 설명 대신 메뉴 강점, 식감, 방문 이유, 맥주 페어링만 남김
- `hookText`와 첫 장면 headline은 `16자`를 넘기지 않도록 추가로 압축

## 실행

1. compile
   - `python -m py_compile services/worker/experiments/prompt_harness.py scripts/run_google_prompt_experiment_with_transport.py scripts/run_google_prompt_variant_repeatability_with_transport.py`
2. single run
   - `python scripts/run_google_prompt_experiment_with_transport.py --experiment-id EXP-148 --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`
3. repeatability
   - `python scripts/run_google_prompt_variant_repeatability_with_transport.py --experiment-id EXP-148 --repeat 3 --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`

## 결과

### single run

- artifact:
  - `docs/experiments/artifacts/exp-148-gemma-4-promotion-highlight-price-off-surface-lock-google-transport.json`

#### baseline

- score: `100.0`
- failed checks: 없음
- hook:
  - `오늘 안 오면 진짜 손해?`

#### candidate

- score: `100.0`
- failed checks: 없음
- hook:
  - `이 육즙 보셨나요?`

### repeatability

- artifact:
  - `docs/experiments/artifacts/exp-148-variant-repeatability-google-transport.json`

#### baseline

- `success_count = 3 / 3`
- `avg_score = 100.0`
- `all_runs_passed = true`

#### candidate

- `success_count = 3 / 3`
- `avg_score = 100.0`
- `all_runs_passed = true`

## 해석

1. 현재 기준으로 `highlightPrice=false` 축은 더 이상 품질 때문에 바로 탈락하는 상태는 아닙니다.
2. `90초 / retry 1회` 조건에서는 baseline과 candidate 모두 strict policy를 통과했습니다.
3. 다만 이번 candidate는 baseline을 점수로 압도했다기보다, `가격 비강조 + nearby leakage 금지`를 option profile 문구로 더 명시적으로 캡슐화했다는 의미가 큽니다.
4. 기본 `60초` transport risk 자체는 여전히 `EXP-143` evidence를 같이 봐야 합니다.

## 판단

- 이번 실험은 `실험 성공, profile 승격 가능`으로 봐도 됩니다.
- 다만 핵심은 `baseline보다 훨씬 더 좋았다`가 아니라,
  - `Gemma 4`가 이 quick option 조합에서도 `90초 / retry 1회` 기준으로 안정적으로 동작했고
  - option-specific constraint를 manifest profile로 고정할 수 있는 수준의 explicit prompt가 생겼다는 점입니다.

## 결론

- `promotion / highlightPrice=false`는 이제 `승격 보류` 상태가 아닙니다.
- 다음 단계는 `prompt-baseline-v1.json` option profile로 연결하고, snapshot acceptance와 runtime summary recommendation까지 확인하는 것입니다.

## 관련 파일

- `services/worker/experiments/prompt_harness.py`
- `docs/experiments/artifacts/exp-148-gemma-4-promotion-highlight-price-off-surface-lock-google-transport.json`
- `docs/experiments/artifacts/exp-148-variant-repeatability-google-transport.json`
