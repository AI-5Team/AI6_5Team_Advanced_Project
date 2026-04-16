# EXP-193 GPT-5 Mini New Menu Highlight Price Minimal Region Anchor

## 배경

- `EXP-188` 기준 두 번째 `P2`는 `T01 new_menu / friendly / highlightPrice=true / shorterCopy=false / emphasizeRegion=false`였습니다.
- minimal region anchor 기준이 이미 정리돼 있었기 때문에, 이번에는 같은 축 위에 `highlightPrice=true`만 안전하게 얹으면 되는 상태였습니다.

## 목표

- 가격 숫자 환각 없이 `highlightPrice=true`를 메뉴 가치 포인트 foreground로 해석하면서도 minimal region anchor를 유지할 수 있는지 확인합니다.

## 실행

- `python -m py_compile services/worker/experiments/prompt_harness.py`
- `python scripts/run_prompt_experiment.py --experiment-id EXP-193`
- `python scripts/run_prompt_variant_repeatability_spot_check.py --experiment-id EXP-193 --repeat 3`

artifact:

- `docs/experiments/artifacts/exp-193-gpt-5-mini-new-menu-highlight-price-minimal-region-anchor.json`
- `docs/experiments/artifacts/exp-193-variant-repeatability.json`

## 결과

### single run

| variant | score | hook | cta |
|---|---:|---|---|
| baseline | `100.0` | `첫 모금부터 달라요` | `저장하고 확인` |
| candidate | `100.0` | `놓치지 마세요, 신메뉴!` | `저장하고 확인` |

### repeatability

| variant | success | avg score | avg hook length | avg cta length |
|---|---:|---:|---:|---:|
| baseline | `3/3` | `100.0` | `13.3` | `7.0` |
| candidate | `3/3` | `100.0` | `12.7` | `7.7` |

## 해석

1. candidate는 가격 숫자나 할인 표현을 만들지 않고도 `놓치면 아쉬운 신메뉴`, `가치 포인트` 계열 foreground를 안정적으로 유지했습니다.
2. region은 계속 caption 1개와 `#성수동` 1개로만 남고, hook/body는 메뉴 가치 포인트에 집중했습니다.

## 판단

- `EXP-193`은 `new_menu_friendly_minimal_region_anchor_highlight_price` profile 승격 근거로 사용할 수 있습니다.

