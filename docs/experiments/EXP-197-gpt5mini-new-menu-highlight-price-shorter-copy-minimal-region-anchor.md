# EXP-197 GPT-5 Mini New Menu Highlight Price Shorter Copy Minimal Region Anchor

## 배경

- `EXP-196` 기준 남은 마지막 non-region `P2`는 `T01 new_menu / friendly / highlightPrice=true / shorterCopy=true / emphasizeRegion=false`였습니다.
- 가장 가까운 기존 profile은 `new_menu_friendly_minimal_region_anchor_shorter_copy`였고, 여기에 `highlightPrice=true`만 더 얹으면 되는 상태였습니다.

## 목표

- minimal region anchor와 shorterCopy 압축을 유지한 채 `highlightPrice=true`를 숫자 가격 환각 없는 한 줄 value foreground로 결합할 수 있는지 확인합니다.

## 실행

- `python -m py_compile services/worker/experiments/prompt_harness.py`
- `python scripts/run_prompt_experiment.py --experiment-id EXP-197`
- `python scripts/run_prompt_variant_repeatability_spot_check.py --experiment-id EXP-197 --repeat 3`

artifact:

- `docs/experiments/artifacts/exp-197-gpt-5-mini-new-menu-highlight-price-shorter-copy-minimal-region-anchor.json`
- `docs/experiments/artifacts/exp-197-variant-repeatability.json`

## 결과

### single run

| variant | score | hook | cta |
|---|---:|---|---|
| baseline | `100.0` | `딸기 크림 라떼, 출시` | `저장하고 확인` |
| candidate | `100.0` | `놓치기 아까운 신메뉴` | `저장하고 보기` |

### repeatability

| variant | success | avg score | avg hook length | avg cta length |
|---|---:|---:|---:|---:|
| baseline | `3/3` | `100.0` | `10.3` | `6.3` |
| candidate | `3/3` | `100.0` | `9.7` | `6.7` |

## 해석

1. candidate는 `shorterCopy=true` 압축을 유지하면서도 한 줄 가치 포인트를 먼저 읽히게 만들었습니다.
2. region minimal anchor, hashtag 수, detail-location 금지, no-price-hallucination 제약이 모두 repeatability `3/3 pass`로 유지됐습니다.

## 판단

- `EXP-197`은 `new_menu_friendly_minimal_region_anchor_highlight_price_shorter_copy` profile 승격 근거로 사용할 수 있습니다.

