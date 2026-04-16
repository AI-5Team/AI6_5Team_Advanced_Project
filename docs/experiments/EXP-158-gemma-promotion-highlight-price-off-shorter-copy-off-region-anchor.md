# EXP-158 Gemma 4 Promotion Highlight Price Off Shorter Copy Off Region Anchor

## 배경

- `EXP-155` 이후 promotion 축의 non-region gap은 정리됐고, 남은 promotion 공백은 모두 `emphasizeRegion=true`가 포함된 `P3` 후보였습니다.
- 동시에 `new_menu/review P2`는 `gpt-5-mini` 경로가 필요했지만, 이번 세션에서는 `OPENAI_API_KEY`가 막혀 실행이 불가능했습니다.
- 따라서 이번 라운드는 실행 가능한 Google 라인 중 가장 가까운 후보인 `promotion / highlightPrice=false / shorterCopy=false / emphasizeRegion=true`를 먼저 확인했습니다.

## 목표

- 이미 승격된 `promotion_surface_lock_highlight_price_off_shorter_copy_off` prompt family 위에 safe region anchor를 추가합니다.
- `emphasizeRegion=true`를 켜더라도 nearby/detail-location leakage 없이 option profile로 승격 가능한지 확인합니다.

## 구현

- 파일:
  - `services/worker/experiments/prompt_harness.py`
- 추가 scenario:
  - `scenario-restaurant-promotion-b-grade-real-photo-highlight-price-off-shorter-copy-off-region-emphasis`
- 추가 experiment:
  - `EXP-158`
- variant:
  - baseline: `promotion_surface_lock_highlight_price_off_shorter_copy_off_region_baseline_gemma`
  - candidate: `promotion_surface_locked_highlight_price_off_shorter_copy_off_region_anchor_gemma`

## 실행

- `python -m py_compile services/worker/experiments/prompt_harness.py scripts/run_google_prompt_experiment_with_transport.py scripts/run_google_prompt_variant_repeatability_with_transport.py`
- `python scripts/run_google_prompt_experiment_with_transport.py --experiment-id EXP-158 --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`
- `python scripts/run_google_prompt_variant_repeatability_with_transport.py --experiment-id EXP-158 --repeat 3 --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`

artifact:

- `docs/experiments/artifacts/exp-158-gemma-4-promotion-highlight-price-off-shorter-copy-off-region-anchor-google-transport.json`
- `docs/experiments/artifacts/exp-158-variant-repeatability-google-transport.json`

## 결과

### single run

| variant | score | hook | note |
|---|---:|---|---|
| deterministic reference | `93.3` | `성수동에서 오늘 바로 쓰기 좋은 혜택로 분위기를 한 번에 보여드립니다` | `region repeated more than allowed` |
| baseline | `100.0` | `이 육즙, 오늘만 맞나요?` | nearby leakage 없음 |
| candidate | `100.0` | `성수동 오늘 안 오면 손해?` | region anchor visible, nearby leakage 없음 |

### repeatability

| variant | success | avg score | avg hook length | avg over-limit scene |
|---|---:|---:|---:|---:|
| baseline | `3/3` | `100.0` | `14.0` | `0.0` |
| candidate | `3/3` | `100.0` | `14.0` | `0.0` |

candidate sample hooks:

- `성수동에서 이거 보셨나요?`
- `성수동에서 이거 보셨나요?`
- `성수동에서 이거 보셨나요?`

## 해석

1. `combined no-price + shorterCopy=false` family에서도 `emphasizeRegion=true`를 안전하게 profile로 분리할 수 있다는 근거가 생겼습니다.
2. baseline도 품질은 통과했지만, candidate는 region anchor가 실제 첫 훅으로 올라온다는 점에서 option profile 의미가 더 분명합니다.
3. 즉 이번 candidate의 가치는 점수 우위보다 `region emphasis`를 safe surface 규칙으로 고정할 수 있다는 데 있습니다.

## 판단

- `promotion / highlightPrice=false / shorterCopy=false / emphasizeRegion=true`는 manifest option profile 승격 후보로 볼 수 있습니다.
- transport recommendation은 기존 Google option profile과 동일하게 `90초 / retry 1회`를 유지하는 편이 맞습니다.
