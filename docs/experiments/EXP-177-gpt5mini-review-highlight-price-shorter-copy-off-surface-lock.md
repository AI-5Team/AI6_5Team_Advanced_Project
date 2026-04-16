# EXP-177 GPT-5 Mini Review Highlight Price Shorter Copy Off Surface Lock

## 배경

- `EXP-176` 기준 최상위 `P2` 후보 중 하나는 `T04 review / b_grade_fun / highlightPrice=true / shorterCopy=false / emphasizeRegion=false`였습니다.
- 가장 가까운 기존 profile은 `review_strict_fallback_surface_lock_shorter_copy_off`였고, 이 조합은 `highlightPrice=true` 해석만 추가하면 되는 상태였습니다.
- 따라서 `review shorterCopy=false` fallback을 그대로 재사용하면서, 가격 숫자 환각 없이 `값어치가 느껴지는 이유`만 foreground하는 방향이 가장 자연스러웠습니다.

## 목표

- `highlightPrice=true`를 review 템플릿에서 숫자 가격 생성이 아니라 `한 끼 만족감/다시 갈 이유` 강조로 해석할 수 있는지 확인합니다.
- `shorterCopy=false` 설명 여유를 유지하면서도 위치 leakage, 할인 환각, scene overflow 없이 option profile로 승격 가능한지 판단합니다.

## 구현

- 파일:
  - `services/worker/experiments/prompt_harness.py`
- 추가 scenario:
  - `scenario-restaurant-review-b-grade-real-photo-highlight-price-shorter-copy-off`
- 추가 experiment:
  - `EXP-177`
- variant:
  - baseline: `review_surface_locked_highlight_price_shorter_copy_off_baseline_gpt5mini`
  - candidate: `review_surface_locked_highlight_price_shorter_copy_off`

## 실행

- `python -m py_compile services/worker/experiments/prompt_harness.py`
- `python scripts/run_prompt_experiment.py --experiment-id EXP-177`
- `python scripts/run_prompt_variant_repeatability_spot_check.py --experiment-id EXP-177 --repeat 3`

artifact:

- `docs/experiments/artifacts/exp-177-gpt-5-mini-review-highlight-price-shorter-copy-off-surface-lock.json`
- `docs/experiments/artifacts/exp-177-variant-repeatability.json`

## 결과

### single run

| variant | score | hook | product | cta |
|---|---:|---|---|---|
| deterministic reference | `93.3` | `성수동 기준 다시 찾게 되는 한 줄 후기로 분위기를 한 번에 보여드립` | `성수동 음식점 대표 메뉴를 짧고 선명하게 소개합니다` | `지금 바로 들러보세요` |
| baseline | `100.0` | `한 번 먹고 기억나요` | `겉바속촉 규카츠 정식` | `저장하고 가기` |
| candidate | `100.0` | `한 번 먹고 기억나요` | `겉바속촉 규카츠 정식` | `저장하고 확인` |

candidate 추가 관찰:

- `subText.review_quote`: `바삭한 튀김과 촉촉한 핏감이 만나 또 생각남`
- `subText.product_name`: `담백한 국물에 쫄깃한 면 조합이 완벽`
- 새로운 가격 숫자, 할인율, 세일 문구 생성 없음

### repeatability

| variant | success | avg score | avg hook length | avg cta length |
|---|---:|---:|---:|---:|
| baseline | `3/3` | `100.0` | `11.0` | `5.3` |
| candidate | `3/3` | `100.0` | `11.0` | `5.7` |

## 해석

1. baseline/candidate 모두 strict review fallback 품질선을 유지했습니다.
2. candidate는 `highlightPrice=true`를 할인/가성비 문구로 풀지 않고, `또 생각남`, `조합이 완벽` 같은 만족감 근거로 흡수했습니다.
3. 즉 review 템플릿에서도 `highlightPrice=true`를 `가격 숫자`가 아니라 `값어치가 느껴지는 이유 foreground`로 해석하는 기준이 만들어졌습니다.

## 판단

- `EXP-177`은 `review / highlightPrice=true / shorterCopy=false / emphasizeRegion=false` option profile 승격 근거로 사용할 수 있습니다.
- 이 결과로 비지역 `P2`는 1건만 남았고, 마지막 후보는 `review / highlightPrice=true / shorterCopy=true`입니다.
