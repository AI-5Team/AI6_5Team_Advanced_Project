# EXP-165 GPT-5 Mini New Menu Highlight Price Region Anchor

## 배경

- `EXP-164` 기준 최상위 `P2` 후보 중 하나는 `T01 new_menu / friendly / highlightPrice=true / shorterCopy=false / emphasizeRegion=true`였습니다.
- 가장 가까운 기존 profile은 `new_menu_friendly_strict_region_anchor`였고, 이 조합은 `highlightPrice=true` 1개만 추가로 해석하면 되는 상태였습니다.
- 다만 `new_menu` 입력에는 가격 숫자가 직접 없는 경우가 많아서, `highlightPrice=true`를 그대로 숫자 가격 강조로 밀면 환각 위험이 있습니다.

## 목표

- `highlightPrice=true`를 `가격 숫자 생성`이 아니라 `body 가치 포인트 강조`로 안전하게 해석할 수 있는지 확인합니다.
- `gpt-5-mini`를 고정한 채 baseline 재사용과 candidate variant를 비교해 option profile 승격 가능 여부를 판단합니다.

## 구현

- 파일:
  - `services/worker/experiments/prompt_harness.py`
- 추가 scenario:
  - `scenario-cafe-new-menu-fixed-highlight-price`
- 추가 experiment:
  - `EXP-165`
- variant:
  - baseline: `new_menu_friendly_region_anchor_highlight_price_baseline_gpt5mini`
  - candidate: `new_menu_friendly_region_anchor_highlight_price_gpt5mini`

## 실행

- `python -m py_compile services/worker/experiments/prompt_harness.py`
- `python scripts/run_prompt_experiment.py --experiment-id EXP-165`
- `python scripts/run_prompt_variant_repeatability_spot_check.py --experiment-id EXP-165 --repeat 3`

artifact:

- `docs/experiments/artifacts/exp-165-gpt-5-mini-new-menu-highlight-price-region-anchor.json`
- `docs/experiments/artifacts/exp-165-variant-repeatability.json`

## 결과

### single run

| variant | score | hook | difference | cta |
|---|---:|---|---|---|
| deterministic reference | `93.3` | `성수동에서 먼저 만나는 신메뉴로 분위기를 한 번에 보여드립니다` | `가격 포인트가 먼저 보이도록 구성했습니다` | `오늘 바로 방문해 보세요` |
| baseline | `100.0` | `성수동에서 이거 보셨나요?` | `생크림 층과 딸기 퓌레 조합` | `방문해 확인` |
| candidate | `100.0` | `성수동에서 이거 보셨나요?` | `수제 크림과 상큼한 딸기 콤비네이션, 디저트와 페어링 최적화` | `방문해보기` |

### repeatability

| variant | success | avg score | avg hook length | avg cta length |
|---|---:|---:|---:|---:|
| baseline | `3/3` | `100.0` | `14.0` | `6.0` |
| candidate | `3/3` | `100.0` | `14.0` | `5.3` |

## 해석

1. baseline과 candidate 모두 품질선은 통과했지만, candidate가 `difference/subText`에서 메뉴 조합과 페어링 같은 가치 포인트를 더 분명하게 드러냈습니다.
2. candidate는 가격 숫자, 할인율, 특가 문구를 새로 만들지 않았고, `highlightPrice=true`를 안전한 `value emphasis`로 해석했습니다.
3. 따라서 이 축은 baseline 재사용보다 candidate variant를 option profile로 고정하는 편이 더 적절합니다.

## 판단

- `EXP-165`는 `new_menu highlightPrice=true` option profile 승격 근거로 사용할 수 있습니다.
- 다음 `new_menu` 최상위 공백은 `highlightPrice=true + shorterCopy=true + emphasizeRegion=true` 1건입니다.
