# EXP-205 Gemma 4 Promotion Shorter Copy Off Region Anchor

## 배경

- `EXP-201`로 no-price region gap을 닫은 뒤 남은 promotion region 공백은 `shorterCopy=false` 1건과 default 1건이었습니다.
- 이번 조합은 기존 `promotion_surface_lock_shorter_copy_off` family 위에 region emphasis를 얹는 형태라, 설명 여유가 nearby leakage로 새지 않는지 확인하는 것이 핵심이었습니다.

## 목표

- `shorterCopy=false` 설명 여유를 유지하면서 `emphasizeRegion=true`를 first-hook anchor로 안전하게 추가합니다.
- `highlightPrice=true` 상황에서도 가격 숫자 hallucination 없이 value foreground만 남길 수 있는지 확인합니다.

## 구현

- 파일:
  - `services/worker/experiments/prompt_harness.py`
- 추가 scenario:
  - `scenario-restaurant-promotion-b-grade-real-photo-shorter-copy-off-region-emphasis`
- 추가 experiment:
  - `EXP-205`
- variant:
  - baseline: `promotion_surface_lock_shorter_copy_off_region_baseline_gemma`
  - candidate: `promotion_surface_locked_shorter_copy_off_region_anchor_gemma`

## 실행

- `python scripts/run_google_prompt_experiment_with_transport.py --experiment-id EXP-205 --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`
- `python scripts/run_google_prompt_variant_repeatability_with_transport.py --experiment-id EXP-205 --repeat 3 --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`

artifact:

- `docs/experiments/artifacts/exp-205-gemma-4-promotion-shorter-copy-off-region-anchor-google-transport.json`
- `docs/experiments/artifacts/exp-205-variant-repeatability-google-transport.json`

## 결과

### single run

| variant | score | hook | note |
|---|---:|---|---|
| deterministic reference | `93.3` | `성수동에서 오늘 바로 쓰기 좋은 혜택로 분위기를 한 번에 보여드립니다` | `region repeated more than allowed` |
| baseline | `100.0` | `오늘 안 오면 손해인가요?` | nearby leakage 없음 |
| candidate | `100.0` | `성수동 오늘 안 오면 손해?` | first-hook region anchor visible |

### repeatability

| variant | success | avg score | avg hook length | avg over-limit scene |
|---|---:|---:|---:|---:|
| baseline | `3/3` | `100.0` | `14.0` | `0.0` |
| candidate | `3/3` | `100.0` | `14.7` | `0.0` |

candidate sample hooks:

- `성수동 오늘 안 오면 손해?`
- `성수동에서 이거 보셨나요?`
- `성수동 오늘 안 오면 손해?`

## 해석

1. `shorterCopy=false`로 생긴 설명 여유를 nearby 설명이 아니라 메뉴 매력과 방문 이유로만 묶는 방식이 실제로 버텼습니다.
2. candidate는 region emphasis를 caption 반복이 아니라 first-hook anchor로 고정해도 품질 저하 없이 통과했습니다.
3. 이 조합도 manifest option profile로 올려도 무리가 없습니다.

