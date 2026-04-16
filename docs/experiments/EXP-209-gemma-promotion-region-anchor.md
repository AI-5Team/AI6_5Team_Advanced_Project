# EXP-209 Gemma 4 Promotion Region Anchor

## 배경

- `EXP-201`, `EXP-205`를 통과하고 나면 남는 promotion region 공백은 default 조합 `highlightPrice=true / shorterCopy=true / emphasizeRegion=true` 1건뿐이었습니다.
- 이 조합은 active promotion baseline에 region emphasis를 얹는 형태라, prompt 자체보다는 transport 변동성과 value foreground 안정성을 함께 봐야 했습니다.

## 목표

- default promotion baseline 위에 safe first-hook region anchor를 추가합니다.
- `highlightPrice=true`와 `shorterCopy=true`를 유지하되 숫자 가격 hallucination 없이 region emphasis를 분리할 수 있는지 확인합니다.

## 구현

- 파일:
  - `services/worker/experiments/prompt_harness.py`
- 추가 scenario:
  - `scenario-restaurant-promotion-b-grade-real-photo-region-emphasis`
- 추가 experiment:
  - `EXP-209`
- variant:
  - baseline: `promotion_surface_lock_region_baseline_gemma`
  - candidate: `promotion_surface_locked_region_anchor_gemma`

## 실행

- `python scripts/run_google_prompt_experiment_with_transport.py --experiment-id EXP-209 --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`
- `python scripts/run_google_prompt_experiment_with_transport.py --experiment-id EXP-209 --timeout-sec 120 --max-retries 1 --retry-backoff-sec 3`
- `python scripts/run_google_prompt_variant_repeatability_with_transport.py --experiment-id EXP-209 --repeat 3 --timeout-sec 120 --max-retries 1 --retry-backoff-sec 3`

artifact:

- `docs/experiments/artifacts/exp-209-gemma-4-promotion-region-anchor-google-transport.json`
- `docs/experiments/artifacts/exp-209-variant-repeatability-google-transport.json`

## 결과

### first run note

- 첫 `90초 / retry 1회` single run에서는 candidate가 transport timeout에 걸렸습니다.
- prompt 수정 없이 `120초 / retry 1회`로 다시 실행했을 때 baseline/candidate 모두 `100.0`으로 통과했습니다.

### final single run

| variant | score | hook | note |
|---|---:|---|---|
| deterministic reference | `93.3` | `성수동에서 오늘 바로 쓰기 좋은 혜택` | `region repeated more than allowed` |
| baseline | `100.0` | `오늘 안 오면 진짜 손해?` | nearby leakage 없음 |
| candidate | `100.0` | `성수동 오늘 안 오면 손해?` | first-hook region anchor visible |

### repeatability

| variant | success | avg score | avg hook length | avg over-limit scene |
|---|---:|---:|---:|---:|
| baseline | `3/3` | `100.0` | `14.0` | `0.0` |
| candidate | `3/3` | `100.0` | `13.3` | `0.0` |

candidate sample hooks:

- `성수동 이거 보셨나요?`
- `성수동에서 이거 보셨나요?`
- `성수동에서 이거 보셨나요?`

## 해석

1. default promotion 조합도 first-hook region anchor 방식으로 안전하게 분리할 수 있었습니다.
2. 다만 이 profile은 다른 두 region profile보다 transport 변동성이 조금 더 컸습니다.
3. prompt 자체는 통과선에 올라왔고, 운영상으로는 retry guard를 기본값보다 더 의식해야 하는 축으로 보는 편이 맞습니다.

