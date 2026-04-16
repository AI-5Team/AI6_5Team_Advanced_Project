# EXP-215 GPT-5 Mini Review Shorter Copy Off Region Anchor

## 배경

- `EXP-213`으로 짧은 review region 강조 조합을 닫은 뒤 남은 공백 중 하나는 `shorterCopy=false / emphasizeRegion=true`였습니다.
- 이 조합은 설명 여유가 늘어나면서 위치 leakage가 다시 들어오지 않는지가 핵심이었습니다.

## 목표

- `T04 review / b_grade_fun / highlightPrice=false / shorterCopy=false / emphasizeRegion=true` 조합을 닫습니다.
- `shorterCopy=false`는 문장 길이 전체 확대가 아니라, 후기 맥락과 식감/재방문 이유를 한 줄 더 설명하는 방식으로만 해석합니다.

## 구현

- 파일:
  - `services/worker/experiments/prompt_harness.py`
- 추가 scenario:
  - `scenario-restaurant-review-b-grade-real-photo-shorter-copy-off-region-emphasis`
- 추가 experiment:
  - `EXP-215`
- variant:
  - baseline: `review_surface_locked_shorter_copy_off_region_baseline_gpt5mini`
  - candidate: `review_surface_locked_shorter_copy_off_region_anchor`

## 실행

- `python scripts/run_prompt_experiment.py --experiment-id EXP-215`
- `python scripts/run_prompt_variant_repeatability_spot_check.py --experiment-id EXP-215 --repeat 3`

artifact:

- `docs/experiments/artifacts/exp-215-gpt-5-mini-review-shorter-copy-off-region-anchor.json`
- `docs/experiments/artifacts/exp-215-variant-repeatability.json`

## 결과

### single run

| variant | score | hook | cta | note |
|---|---:|---|---|---|
| deterministic reference | `93.3` | `성수동에서 다시 찾게 되는 한 줄 후기로 분위기를 한 번에 보여드립니` | - | `region repeated more than allowed` |
| baseline | `100.0` | `한 번 먹고 기억나요` | `방문해보기` | nearby leakage 없음 |
| candidate | `100.0` | `성수동 오면 여기부터!` | `방문해보기` | audience cue count `1` |

### repeatability

| variant | success | avg score | avg hook length | avg cta length | avg over-limit scene |
|---|---:|---:|---:|---:|---:|
| baseline | `3/3` | `100.0` | `11.0` | `5.7` | `0.0` |
| candidate | `3/3` | `100.0` | `14.0` | `5.7` | `0.0` |

candidate sample hooks:

- `성수동 오면 여기부터 가요`

## 해석

1. 설명 여유가 늘어난 조합에서도 region은 first-hook과 hashtag 1개로만 고정되고, 상세 위치 leakage는 다시 생기지 않았습니다.
2. `shorterCopy=false`의 확장분은 위치 설명이 아니라 후기 맥락 설명에만 쓰여 strict fallback 기준과 충돌하지 않았습니다.
3. 이 조합도 manifest option profile로 승격해도 되는 수준입니다.
