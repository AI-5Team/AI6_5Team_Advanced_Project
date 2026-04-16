# EXP-217 GPT-5 Mini Review Highlight Price Shorter Copy Off Region Anchor

## 배경

- `review` region 강조 조합 중 하나는 `highlightPrice=true / shorterCopy=false / emphasizeRegion=true`였습니다.
- 이 축은 지역 훅과 value foreground를 동시에 유지하면서 가격 숫자 hallucination 없이 통과하는지가 핵심이었습니다.

## 목표

- `T04 review / b_grade_fun / highlightPrice=true / shorterCopy=false / emphasizeRegion=true` 조합을 닫습니다.
- `highlightPrice=true`는 가격 숫자 생성이 아니라 한 끼 만족감과 다시 갈 이유를 더 먼저 읽히게 만드는 해석으로만 유지합니다.

## 구현

- 파일:
  - `services/worker/experiments/prompt_harness.py`
- 추가 scenario:
  - `scenario-restaurant-review-b-grade-real-photo-highlight-price-shorter-copy-off-region-emphasis`
- 추가 experiment:
  - `EXP-217`
- variant:
  - baseline: `review_surface_locked_highlight_price_shorter_copy_off_region_baseline_gpt5mini`
  - candidate: `review_surface_locked_highlight_price_shorter_copy_off_region_anchor`

## 실행

- `python scripts/run_prompt_experiment.py --experiment-id EXP-217`
- `python scripts/run_prompt_variant_repeatability_spot_check.py --experiment-id EXP-217 --repeat 3`

artifact:

- `docs/experiments/artifacts/exp-217-gpt-5-mini-review-highlight-price-shorter-copy-off-region-anchor.json`
- `docs/experiments/artifacts/exp-217-variant-repeatability.json`

## 결과

### single run

| variant | score | hook | cta | note |
|---|---:|---|---|---|
| deterministic reference | `93.3` | `성수동에서 다시 찾게 되는 한 줄 후기로 분위기를 한 번에 보여드립니` | - | `region repeated more than allowed` |
| baseline | `100.0` | `한 번 먹고 기억나요` | `저장하고 방문` | nearby leakage 없음 |
| candidate | `100.0` | `성수동 오면 여기부터 가요` | `방문해보기` | value foreground 유지 |

### repeatability

| variant | success | avg score | avg hook length | avg cta length | avg over-limit scene |
|---|---:|---:|---:|---:|---:|
| baseline | `3/3` | `100.0` | `11.0` | `5.0` | `0.33` |
| candidate | `3/3` | `100.0` | `14.0` | `5.0` | `0.0` |

candidate sample hooks:

- `성수동 오면 여기부터 가요`

## 해석

1. `highlightPrice=true`와 `emphasizeRegion=true`를 함께 켜도, 가격 숫자 생성 없이 value foreground와 region anchor를 함께 유지할 수 있었습니다.
2. baseline은 repeatability metric에서 한 번 over-limit가 잡혔지만 최종 pass는 유지했고, candidate는 `0.0`으로 더 안정적이었습니다.
3. 따라서 이 조합은 fallback region profile로 연결해도 무리가 없습니다.
