# EXP-181 GPT-5 Mini Review Highlight Price Surface Lock

## 배경

- `EXP-180` 기준 남은 마지막 비지역 `P2`는 `T04 review / b_grade_fun / highlightPrice=true / shorterCopy=true / emphasizeRegion=false`였습니다.
- 가장 가까운 기존 profile은 `review_strict_fallback_surface_lock`이었고, 이 조합은 `highlightPrice=true` 해석만 추가하면 되는 상태였습니다.
- 따라서 마지막 남은 비지역 단일 토글을 `review surface-lock` 계열 안에서 정리하는 것이 가장 자연스러웠습니다.

## 목표

- `highlightPrice=true`를 review 템플릿에서 짧은 만족감 foreground로 해석하면서도 `shorterCopy=true` 압축을 유지할 수 있는지 확인합니다.
- 가격 숫자 환각, 위치 leakage, scene overflow 없이 option profile로 승격 가능한지 판단합니다.

## 구현

- 파일:
  - `services/worker/experiments/prompt_harness.py`
- 추가 scenario:
  - `scenario-restaurant-review-b-grade-real-photo-highlight-price`
- 추가 experiment:
  - `EXP-181`
- variant:
  - baseline: `review_surface_locked_highlight_price_baseline_gpt5mini`
  - candidate: `review_surface_locked_highlight_price`

## 실행

- `python -m py_compile services/worker/experiments/prompt_harness.py`
- `python scripts/run_prompt_experiment.py --experiment-id EXP-181`
- `python scripts/run_prompt_variant_repeatability_spot_check.py --experiment-id EXP-181 --repeat 3`

artifact:

- `docs/experiments/artifacts/exp-181-gpt-5-mini-review-highlight-price-surface-lock.json`
- `docs/experiments/artifacts/exp-181-variant-repeatability.json`

## 결과

### single run

| variant | score | hook | product | cta |
|---|---:|---|---|---|
| deterministic reference | `93.3` | `성수동 기준 다시 찾게 되는 한 줄 후기` | `성수동 음식점 대표 메뉴를 짧고 선명하게 소개합니다` | `지금 바로 들러보세요` |
| baseline | `100.0` | `한 번 먹고 기억남` | `겉바속촉 규카츠 정식` | `방문해보기` |
| candidate | `100.0` | `한 번 먹고 기억나요` | `겉바속촉 규카츠` | `저장하고 방문` |

candidate 추가 관찰:

- `subText.review_quote`: `고소한 육즙이 오래 남음`
- `subText.product_name`: `쫄깃한 면과 진한 국물 조합`
- 새로운 가격 숫자, 할인율, 세일 문구 생성 없음

### repeatability

| variant | success | avg score | avg hook length | avg cta length |
|---|---:|---:|---:|---:|
| baseline | `3/3` | `100.0` | `10.3` | `5.7` |
| candidate | `3/3` | `100.0` | `11.0` | `6.3` |

## 해석

1. baseline/candidate 모두 strict review fallback 품질선을 유지했습니다.
2. candidate는 `highlightPrice=true`를 `고소한 육즙`, `진한 국물 조합`처럼 짧은 만족감 근거로 흡수했고, `shorterCopy=true`답게 각 surface를 짧게 유지했습니다.
3. 즉 review 템플릿에서 남아 있던 마지막 비지역 단일 토글도 `가격 숫자 없는 value foreground`로 정리할 수 있음을 확인했습니다.

## 판단

- `EXP-181`은 `review / highlightPrice=true / shorterCopy=true / emphasizeRegion=false` option profile 승격 근거로 사용할 수 있습니다.
- 이 결과로 비지역 `P2`는 모두 해소됩니다.
