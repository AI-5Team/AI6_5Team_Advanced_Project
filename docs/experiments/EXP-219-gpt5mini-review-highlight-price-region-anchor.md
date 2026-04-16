# EXP-219 GPT-5 Mini Review Highlight Price Region Anchor

## 배경

- review region 강조 계열에서 마지막으로 남은 조합은 default quick-option 조합 `highlightPrice=true / shorterCopy=true / emphasizeRegion=true`였습니다.
- 이 조합은 가장 짧은 카피 길이 안에서 region anchor와 만족감 foreground를 동시에 유지해야 했습니다.

## 목표

- `T04 review / b_grade_fun / highlightPrice=true / shorterCopy=true / emphasizeRegion=true` 조합을 닫습니다.
- 짧은 first-hook 지역 anchor 뒤에 후기 만족감과 재방문 이유를 한 줄로 압축합니다.

## 구현

- 파일:
  - `services/worker/experiments/prompt_harness.py`
- 추가 scenario:
  - `scenario-restaurant-review-b-grade-real-photo-highlight-price-region-emphasis`
- 추가 experiment:
  - `EXP-219`
- variant:
  - baseline: `review_surface_locked_highlight_price_region_baseline_gpt5mini`
  - candidate: `review_surface_locked_highlight_price_region_anchor`

## 실행

- `python scripts/run_prompt_experiment.py --experiment-id EXP-219`
- `python scripts/run_prompt_variant_repeatability_spot_check.py --experiment-id EXP-219 --repeat 3`

artifact:

- `docs/experiments/artifacts/exp-219-gpt-5-mini-review-highlight-price-region-anchor.json`
- `docs/experiments/artifacts/exp-219-variant-repeatability.json`

## 결과

### single run

| variant | score | hook | cta | note |
|---|---:|---|---|---|
| deterministic reference | `93.3` | `성수동에서 다시 찾게 되는 한 줄 후기` | - | `region repeated more than allowed` |
| baseline | `100.0` | `한 번 먹고 기억남` | `방문해보기` | nearby leakage 없음 |
| candidate | `100.0` | `성수동 오면 여기부터 가요` | `저장` | first-hook region anchor visible |

### repeatability

| variant | success | avg score | avg hook length | avg cta length | avg over-limit scene |
|---|---:|---:|---:|---:|---:|
| baseline | `3/3` | `100.0` | `11.0` | `5.3` | `0.0` |
| candidate | `3/3` | `100.0` | `14.0` | `5.7` | `0.0` |

candidate sample hooks:

- `성수동 오면 여기부터 가요`

## 해석

1. review default 조합도 region anchor 방식으로 안정적으로 분리할 수 있었습니다.
2. `shorterCopy=true`를 유지하면서도 지역 훅 뒤에 만족감 근거를 짧게 foreground하는 패턴이 repeatability까지 안정적이었습니다.
3. 이 조합이 닫히면서 review region emphasis quick-option 4건이 모두 baseline option profile로 전환될 준비가 끝났습니다.
