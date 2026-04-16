# EXP-173 GPT-5 Mini Review Shorter Copy Off Surface Lock

## 배경

- `EXP-172` 기준 최상위 `P2` 후보 중 하나는 `T04 review / b_grade_fun / highlightPrice=false / shorterCopy=false / emphasizeRegion=false`였습니다.
- 가장 가까운 기존 profile은 `review_strict_fallback_surface_lock`이었고, 이 조합은 `shorterCopy=false`만 추가 해석하면 되는 상태였습니다.
- 따라서 새 scenario를 여는 대신, 이미 strict review fallback으로 검증된 `gpt-5-mini + surface lock` 계열에서 `설명 한 줄 확장`만 허용하는 방향이 가장 자연스러웠습니다.

## 목표

- `shorterCopy=false`가 붙어도 hook과 review slot을 장황하게 늘리지 않고, `subText`에서 맛/식감/재방문 이유를 한 줄 더 설명할 수 있는지 확인합니다.
- location leakage, nearby landmark leakage, scene overflow 없이 `review` option profile로 승격 가능한지 판단합니다.

## 구현

- 파일:
  - `services/worker/experiments/prompt_harness.py`
- 추가 scenario:
  - `scenario-restaurant-review-b-grade-real-photo-shorter-copy-off`
- 추가 experiment:
  - `EXP-173`
- variant:
  - baseline: `review_surface_locked_shorter_copy_off_baseline_gpt5mini`
  - candidate: `review_surface_locked_exact_region_anchor_shorter_copy_off`

## 실행

- `python -m py_compile services/worker/experiments/prompt_harness.py`
- `python scripts/run_prompt_experiment.py --experiment-id EXP-173`
- `python scripts/run_prompt_variant_repeatability_spot_check.py --experiment-id EXP-173 --repeat 3`

artifact:

- `docs/experiments/artifacts/exp-173-gpt-5-mini-review-shorter-copy-off-surface-lock.json`
- `docs/experiments/artifacts/exp-173-variant-repeatability.json`

## 결과

### single run

| variant | score | hook | review_quote | product | cta |
|---|---:|---|---|---|---|
| deterministic reference | `93.3` | `성수동 기준 다시 찾게 되는 한 줄 후기로 분위기를 한 번에 보여드립` | `"성수동에서 다시 찾고 싶은 한 곳"` | `성수동 음식점 대표 메뉴를 짧고 선명하게 소개합니다` | `지금 바로 들러보세요` |
| baseline | `100.0` | `한 번 먹고 기억나는 집` | `한 번 먹고 기억나요` | `겉바속촉 규카츠·진한 라멘` | `방문해보세요` |
| candidate | `100.0` | `한 번 먹고 기억나요` | `겉바속촉 기억남` | `규카츠 & 진한라멘 세트` | `방문해보기` |

### repeatability

| variant | success | avg score | avg hook length | avg cta length |
|---|---:|---:|---:|---:|
| baseline | `3/3` | `100.0` | `11.0` | `5.7` |
| candidate | `3/3` | `100.0` | `11.0` | `5.7` |

candidate 추가 관찰:

- `subText.review_quote`: `겉은 바삭하고 안은 촉촉해 계속 손이 감`
- `subText.product_name`: `규카츠는 고기 질감이 살아있고 라멘은 국물 깊이가 인상적`
- `detail_location_leak_count=0`
- `avg_over_limit_scene_count=0.0`

## 해석

1. baseline/candidate 모두 strict review fallback 품질선을 유지했습니다.
2. candidate는 hook 길이를 늘리지 않으면서, `shorterCopy=false`의 여유를 `subText` 설명 슬롯에만 쓰도록 유도했습니다.
3. 즉 `짧게 쓰지 않기`를 `위치 반복`이나 `감탄사 증식`이 아니라 `식감/풍미/재방문 이유 한 줄 보강`으로 해석하는 기준이 만들어졌습니다.

## 판단

- `EXP-173`은 `review / shorterCopy=false / emphasizeRegion=false` option profile 승격 근거로 사용할 수 있습니다.
- 이 결과로 review 비지역 `shorterCopy` 축 공백은 해소됐고, 남은 최상위 `P2`는 `highlightPrice=true` review 2건으로 정리됩니다.
