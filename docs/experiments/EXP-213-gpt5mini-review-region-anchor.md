# EXP-213 GPT-5 Mini Review Region Anchor

## 배경

- `EXP-211`, `EXP-212` 기준으로 남은 quick-option gap은 전부 `review / emphasizeRegion=true` 4건이었습니다.
- 이 축은 `review` strict fallback family를 유지한 채, 지역명을 첫 훅과 hashtag 1개에만 고정하는 방식이 실제로 안정적인지 확인할 필요가 있었습니다.

## 목표

- `T04 review / b_grade_fun / highlightPrice=false / shorterCopy=true / emphasizeRegion=true` 조합을 닫습니다.
- `regionName`은 첫 훅과 `#성수동` 1개에만 남기고, `review_quote`, `product_name`, `subText`는 후기형 맛/식감/재방문 이유 중심으로 유지합니다.

## 구현

- 파일:
  - `services/worker/experiments/prompt_harness.py`
- 추가 scenario:
  - `scenario-restaurant-review-b-grade-real-photo-region-emphasis`
- 추가 experiment:
  - `EXP-213`
- variant:
  - baseline: `review_surface_locked_region_baseline_gpt5mini`
  - candidate: `review_surface_locked_region_anchor`

## 실행

- `python scripts/run_prompt_experiment.py --experiment-id EXP-213`
- `python scripts/run_prompt_variant_repeatability_spot_check.py --experiment-id EXP-213 --repeat 3`

artifact:

- `docs/experiments/artifacts/exp-213-gpt-5-mini-review-region-anchor.json`
- `docs/experiments/artifacts/exp-213-variant-repeatability.json`

## 결과

### single run

| variant | score | hook | cta | note |
|---|---:|---|---|---|
| deterministic reference | `93.3` | `성수동에서 다시 찾게 되는 한 줄 후기` | - | `region repeated more than allowed` |
| baseline | `100.0` | `한 번 먹고 기억나요` | `저장하고 가기` | nearby leakage 없음 |
| candidate | `100.0` | `성수동 오면 여기부터 가요` | `방문해보세요` | first-hook region anchor visible |

### repeatability

| variant | success | avg score | avg hook length | avg cta length | avg over-limit scene |
|---|---:|---:|---:|---:|---:|
| baseline | `3/3` | `100.0` | `10.7` | `6.0` | `0.0` |
| candidate | `3/3` | `100.0` | `13.3` | `6.0` | `0.0` |

candidate sample hooks:

- `성수동 오면 여기부터 가요`
- `성수동 오면 꼭 먹어봐`

## 해석

1. `review` 기본 짧은 카피 조합도 지역 강조를 first-hook anchor 방식으로 안전하게 분리할 수 있었습니다.
2. 지역 강조를 켜도 후기 본문은 맛과 재방문 이유 중심으로 유지됐고, nearby/detail-location leakage는 없었습니다.
3. 따라서 이 조합은 strict fallback profile로 manifest에 올릴 수 있는 수준입니다.
