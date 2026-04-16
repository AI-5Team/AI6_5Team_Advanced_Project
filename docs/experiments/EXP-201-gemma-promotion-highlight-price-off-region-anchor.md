# EXP-201 Gemma 4 Promotion Highlight Price Off Region Anchor

## 배경

- `EXP-200` 기준 남은 quick option gap 7건은 전부 `emphasizeRegion=true` 축이었습니다.
- 이 중 `promotion / highlightPrice=false / shorterCopy=true / emphasizeRegion=true`는 기존 `promotion_surface_lock_highlight_price_off` family를 가장 적게 변형해서 닫을 수 있는 후보였습니다.

## 목표

- `highlightPrice=false` 조건을 유지한 채 `emphasizeRegion=true`를 safe first-hook anchor 방식으로 추가합니다.
- nearby/detail-location leakage 없이 option profile로 승격 가능한지 확인합니다.

## 구현

- 파일:
  - `services/worker/experiments/prompt_harness.py`
- 추가 scenario:
  - `scenario-restaurant-promotion-b-grade-real-photo-highlight-price-off-region-emphasis`
- 추가 experiment:
  - `EXP-201`
- variant:
  - baseline: `promotion_surface_lock_highlight_price_off_region_baseline_gemma`
  - candidate: `promotion_surface_locked_highlight_price_off_region_anchor_gemma`

## 실행

- `python -m py_compile services/worker/experiments/prompt_harness.py`
- `python scripts/run_google_prompt_experiment_with_transport.py --experiment-id EXP-201 --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`
- `python scripts/run_google_prompt_variant_repeatability_with_transport.py --experiment-id EXP-201 --repeat 3 --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`

artifact:

- `docs/experiments/artifacts/exp-201-gemma-4-promotion-highlight-price-off-region-anchor-google-transport.json`
- `docs/experiments/artifacts/exp-201-variant-repeatability-google-transport.json`

## 결과

### single run

| variant | score | hook | note |
|---|---:|---|---|
| deterministic reference | `93.3` | `성수동에서 오늘 바로 쓰기 좋은 혜택` | `region repeated more than allowed` |
| baseline | `100.0` | `이 육즙, 오늘만 맞나요?` | nearby leakage 없음 |
| candidate | `100.0` | `성수동에서 이거 보셨나요?` | first-hook region anchor visible |

### repeatability

| variant | success | avg score | avg hook length | avg over-limit scene |
|---|---:|---:|---:|---:|
| baseline | `3/3` | `100.0` | `13.7` | `0.0` |
| candidate | `3/3` | `100.0` | `14.3` | `0.0` |

candidate sample hooks:

- `성수동에서 이거 보셨나요?`
- `성수동에서 이거 보셨나요?`
- `성수동 오늘 안 오면 손해?`

## 해석

1. `highlightPrice=false` 축에서도 `emphasizeRegion=true`를 captions가 아니라 first-hook anchor로 안전하게 분리할 수 있었습니다.
2. candidate는 no-price guard를 유지하면서도 region emphasis 의도를 더 직접적으로 드러냈습니다.
3. 이 조합은 별도 profile로 승격해도 runtime drift를 늘리지 않는다고 봐도 됩니다.

